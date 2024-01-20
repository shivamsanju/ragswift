from typing import List

from qdrant_client import QdrantClient
from qdrant_client.http import models
from ray import serve
from sentence_transformers import CrossEncoder
from stop_words import get_stop_words
from transformers import AutoModel

from schema.base import Context, RetrievalPayload
from settings import settings

from api.fastapi.base import app


@serve.deployment()
@serve.ingress(app)
class ServeDeployment:
    def __init__(self):
        self.stop_words = get_stop_words("en")
        self.reranker_model = CrossEncoder(settings.RERANKER_MODEL)
        self.embedding_model = AutoModel.from_pretrained(
            settings.EMBEDDING_MODEL, trust_remote_code=True
        )
        self.vector_store_client = QdrantClient(
            url=settings.QDRANT_BASE_URI,
            api_key=settings.QDRANT_API_KEY,
            https=False,
        )

    def _remove_stopwords(self, text: str) -> str:
        return " ".join([word for word in text.split() if word not in self.stop_words])

    def _get_query_embedding(self, query: str) -> List[float]:
        processed_query = self._remove_stopwords(query)
        embeddings = self.embedding_model.encode([processed_query]).tolist()
        return embeddings[0]

    def _search_chunks_by_vector(
        self, asset_ids: List[str], vector: List[float], limit
    ) -> List[models.ScoredPoint]:
        # Implement this: https://qdrant.tech/articles/hybrid-search/
        collections = self.vector_store_client.search(
            collection_name=settings.VECTOR_DB_COLLECTION_NAME,
            query_vector=vector,
            query_filter=models.Filter(
                should=[
                    models.FieldCondition(
                        key="asset_id",
                        match=models.MatchValue(
                            value=asset_id,
                        ),
                    )
                    for asset_id in asset_ids
                ]
                if len(asset_ids) > 0
                else None,
            ),
            with_payload=True,
            with_vectors=False,
            limit=limit * 10,  # get more elements to remove duplicates
        )
        unique = []
        seen_scores = set()
        for c in collections:
            if c.score not in seen_scores:
                seen_scores.add(c.score)
                unique.append(c)
        return unique[:limit]

    def _rerank_contexts(
        self,
        query: str,
        contexts: List[models.ScoredPoint],
        score_threshold: float = 1,
    ) -> List[Context]:
        if len(contexts) == 0:
            return []
        query_paragraph_pairs = [
            (query, context.payload.get("text")) for context in contexts
        ]
        scores = self.reranker_model.predict(
            query_paragraph_pairs,
            batch_size=50,
        )

        # Update scores in the ranked_chunks
        relevant_contexts = []
        seen_scores = set()
        for context, score in zip(contexts, scores):
            if score >= score_threshold and score not in seen_scores:
                seen_scores.add(score)
                relevant_contexts.append(
                    Context(
                        text=context.payload.get("text"),
                        metadata=context.payload.get("metadata"),
                        score=score,
                    )
                )
        relevant_contexts.sort(key=lambda x: x.score, reverse=True)
        return relevant_contexts

    @app.post("/retrieve", tags=["Retrieval"], response_model=List[Context])
    def get_contexts(self, request: RetrievalPayload):
        vector = self._get_query_embedding(request.query)
        contexts = self._search_chunks_by_vector(
            request.asset_ids, vector, request.num_contexts
        )
        reranked_contexts = self._rerank_contexts(
            request.query, contexts, request.score_threshold
        )
        return reranked_contexts
