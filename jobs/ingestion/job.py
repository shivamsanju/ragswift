import argparse
import json
import uuid
from typing import List, Union

import ray
from llama_index.text_splitter import CodeSplitter, SentenceSplitter
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse
from sentence_transformers import SentenceTransformer
from stop_words import get_stop_words
from tqdm import tqdm
from transformers import AutoModel

from jobs.batcher import run_actor_paralelly
from jobs.ingestion.reader import get_reader
from schema.base import Chunk, Document, GithubIngestionPayload, S3IngestionPayload
from settings import settings


@ray.remote(
    num_cpus=0.5,
    num_gpus=0,
)
class Reader:
    def __init__(self):
        pass

    def read_docs(self, payload: Union[GithubIngestionPayload, S3IngestionPayload]):
        reader = get_reader(
            asset_type=payload.asset_type,
            asset_id=payload.asset_id,
            owner=payload.owner,
            kwargs=payload.reader_kwargs,
            extra_metadata=payload.extra_metadata,
        )
        documents = reader.load()
        return documents


@ray.remote(
    num_cpus=0.25,
    num_gpus=0,
)
class Chunker:
    def __init__(self):
        self.supported_languages = {
            ".bash": "bash",
            ".c": "c",
            ".cs": "c-sharp",
            ".lisp": "commonlisp",
            ".cpp": "cpp",
            ".css": "css",
            ".dockerfile": "dockerfile",
            ".dot": "dot",
            ".elisp": "elisp",
            ".ex": "elixir",
            ".elm": "elm",
            ".et": "embedded-template",
            ".erl": "erlang",
            ".f": "fixed-form-fortran",
            ".f90": "fortran",
            ".go": "go",
            ".mod": "go-mod",
            ".hack": "hack",
            ".hs": "haskell",
            ".hcl": "hcl",
            ".html": "html",
            ".java": "java",
            ".js": "javascript",
            ".jsdoc": "jsdoc",
            ".json": "json",
            ".jl": "julia",
            ".kt": "kotlin",
            ".lua": "lua",
            ".mk": "make",
            ".md": "markdown",
            ".m": "objc",
            ".ml": "ocaml",
            ".pl": "perl",
            ".php": "php",
            ".py": "python",
            ".ql": "ql",
            ".r": "r",
            ".regex": "regex",
            ".rst": "rst",
            ".rb": "ruby",
            ".rs": "rust",
            ".scala": "scala",
            ".sql": "sql",
            ".sqlite": "sqlite",
            ".toml": "toml",
            ".tsq": "tsq",
            ".tsx": "typescript",
            ".ts": "typescript",
            ".yaml": "yaml",
        }

    def chunk_doc(
        self,
        doc: Document,
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    ) -> List[Chunk]:
        ext = doc.filename.split(".")[-1] if doc.filename else "generic"
        language = self.supported_languages.get(ext)

        text_splitter = None
        if language:
            text_splitter = CodeSplitter(
                language=language,
                max_chars=chunk_size,
                chunk_lines_overlap=chunk_overlap,
            )
        else:
            text_splitter = SentenceSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )

        text_splits = text_splitter.split_text(doc.text)
        return [
            Chunk(
                chunk_id=str(uuid.uuid4()),
                asset_id=doc.asset_id,
                doc_id=doc.doc_id,
                text=text,
                metadata=doc.metadata,
            )
            for text in text_splits
        ]


@ray.remote(
    num_cpus=1,
    num_gpus=0,
)
class Embedder:
    def __init__(self):
        self.stop_words = get_stop_words("en")
        if settings.USE_SENTENCE_TRANSFORMERS:
            self.embed_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        else:
            self.embed_model = AutoModel.from_pretrained(
                settings.EMBEDDING_MODEL, trust_remote_code=True
            )

    def _remove_stopwords(self, text: str) -> str:
        return " ".join([word for word in text.split() if word not in self.stop_words])

    def embed_chunks_batch(
        self, chunks: List[Chunk], batch_size: int = 10
    ) -> List[Chunk]:
        chunk_texts = [self._remove_stopwords(chunk.text) for chunk in chunks]
        embeddings = self.embed_model.encode(
            chunk_texts,
            batch_size=batch_size,
        ).tolist()
        assert len(chunk_texts) == len(embeddings)
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embeddings = embedding
        return chunks


@ray.remote(
    num_cpus=0.25,
    num_gpus=0,
)
class VectorStoreClient:
    def __init__(self):
        self.vectorstore_client = QdrantClient(
            url=settings.QDRANT_BASE_URI,
            api_key=settings.QDRANT_API_KEY,
            https=False,
        )
        self._dim = settings.EMBEDDING_DIMENSION
        self._collection_name = settings.VECTOR_DB_COLLECTION_NAME
        self._create_collection_if_not_exists()

    def _create_collection_if_not_exists(self):
        try:
            self.vectorstore_client.get_collection(self._collection_name)
        except (UnexpectedResponse, ValueError):
            self.vectorstore_client.create_collection(
                collection_name=self._collection_name,
                vectors_config=models.VectorParams(
                    size=self._dim, distance=models.Distance.COSINE, on_disk=True
                ),
                on_disk_payload=True,
                hnsw_config=models.HnswConfigDiff(payload_m=16, m=0, on_disk=True),
            )
            self._create_asset_id_index()

    def _create_asset_id_index(self):
        self.vectorstore_client.create_payload_index(
            collection_name=self._collection_name,
            field_name="asset_id",
            field_schema=models.PayloadSchemaType.KEYWORD,
        )

    def _get_batch_points(self, chunk_batch: List[List[Chunk]]):
        ids = []
        payloads = []
        vectors = []

        for batch in chunk_batch:
            for chunk in batch:
                ids.append(chunk.chunk_id)
                vectors.append(chunk.embeddings)
                payloads.append(
                    {
                        "doc_id": chunk.doc_id,
                        "asset_id": chunk.asset_id,
                        "metadata": json.dumps(chunk.metadata),
                        "text": chunk.text,
                    }
                )

        return [ids, payloads, vectors]

    def store_chunks_in_vector_db(self, chunks_batches: List[List[Chunk]]):
        points_batch = self._get_batch_points(chunks_batches)
        self.vectorstore_client.upload_collection(
            collection_name=self._collection_name,
            vectors=points_batch[2],
            payload=points_batch[1],
            ids=points_batch[0],
            parallel=20,
            wait=True,
        )
        return True


def with_tqdm_iterator(obj_ids):
    while obj_ids:
        done, obj_ids = ray.wait(obj_ids)
        yield ray.get(done[0])


# Please note that setting num_cpus=0 means that the task or actor can run on a node even if no CPUs are available.
# However, the actual CPU utilization is not controlled or limited by Ray, so the task or actor could still use CPU
# resources when it runs.
@ray.remote(num_cpus=0.25)
def ingest_asset(payload: Union[GithubIngestionPayload, S3IngestionPayload]):
    NUM_WORKERS = settings.INGESTION_WORKERS_PER_JOB

    # Read documents
    reader = Reader.remote()
    docs = ray.get(reader.read_docs.remote(payload))
    del reader  # delete actor to free space

    # Chunk the docs in parallel
    (chunks_refs, actors) = run_actor_paralelly(Chunker, "chunk_doc", docs, NUM_WORKERS)
    chunks = [
        chunk for chunk in tqdm(with_tqdm_iterator(chunks_refs), total=len(chunks_refs))
    ]
    flat_chunks = [item for sublist in chunks for item in sublist]
    # delete actors to free up cpu allocation
    for actor in actors:
        ray.kill(actor)

    # Embed the chunks again in parallel
    batch_size, batches = 2, []
    for i in range(0, len(flat_chunks), batch_size):
        batch = flat_chunks[i : i + batch_size]
        batches.append(batch)
    (embed_refs, actors) = run_actor_paralelly(
        Embedder, "embed_chunks_batch", batches, NUM_WORKERS
    )
    embedded_chunks = [
        chunk for chunk in tqdm(with_tqdm_iterator(embed_refs), total=len(embed_refs))
    ]
    flat_chunks = [item for sublist in chunks for item in sublist]
    # delete actors to free up cpu allocation
    for actor in actors:
        ray.kill(actor)

    # Save the chunk in vectorstore
    vectorstore = VectorStoreClient.remote()
    result = vectorstore.store_chunks_in_vector_db.remote(embedded_chunks)
    ray.get(result)
    del vectorstore


if __name__ == "__main__":
    context = ray.init()
    parser = argparse.ArgumentParser(
        description="Process JSON payload for ingestion job"
    )
    parser.add_argument("--payload", required=True, help="JSON payload as a string")

    args = parser.parse_args()
    payload_dict = json.loads(args.payload)
    payload_model = None
    if payload_dict.get("asset_type") == "github":
        payload_model = GithubIngestionPayload.model_validate(payload_dict)
    elif payload_dict.get("asset_type") == "s3":
        payload_model = S3IngestionPayload.model_validate(payload_dict)
    else:
        print("Invalid asset type")
    obj = ingest_asset.remote(payload_model)
    result = ray.get(obj)
    print("Ingestion job result:", result)
