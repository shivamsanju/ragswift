import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Literal

from llama_hub.s3 import S3Reader
from llama_index.readers import GithubRepositoryReader
from pydantic import BaseModel

from constants import READ_SUCCESSFULLY
from schema.base import Document


class GithubReaderKwargs(BaseModel):
    owner: str
    repo: str
    branch: str = "main"
    github_token: str


class S3ReaderKwargs(BaseModel):
    bucket_name: str
    access_key: str
    secret_key: str
    endpoint: str = None


AllowedAssetTypes = Literal["github", "s3"]
AllowedReaderKwargs = GithubReaderKwargs


class BaseReader(ABC):
    def __init__(self, asset_id, owner: str, extra_metadata: Dict[str, Any]):
        self.asset_id = asset_id
        self.owner = owner
        self.extra_metadata = extra_metadata

    @abstractmethod
    def _load(self) -> List[Any]:
        pass

    def _add_metadata(self, documents: List[Any]) -> List[Any]:
        for doc in documents:
            doc.metadata.update(self.extra_metadata)
        return documents

    def _transform(self, documents: List[Any]) -> List[Document]:
        documents = self._add_metadata(documents)
        doc_objects = []
        for doc in documents:
            doc_id = str(uuid.uuid4())
            custom_doc = Document(
                asset_id=self.asset_id,
                doc_id=doc_id,
                text=doc.text,
                metadata={
                    **doc.metadata,
                    "doc_id": doc_id,
                    "asset_id": self.asset_id,
                    "uploaded_by": self.owner,
                },
                filename=doc.metadata.get("file_name"),
                filepath=doc.metadata.get("file_path"),
                uploaded_by=self.owner,
                status=READ_SUCCESSFULLY,
            )
            doc_objects.append(custom_doc)
        return doc_objects

    def load(self) -> List[Document]:
        docs = self._load()
        docs = self._transform(docs)
        return docs


class GitHubReader(BaseReader):
    def __init__(
        self,
        asset_id: str,
        owner: str,
        kwargs: GithubReaderKwargs,
        extra_metadata: Dict[str, Any] = {},
    ):
        super().__init__(asset_id, owner, extra_metadata)
        self.branch = kwargs.branch
        self.reader = GithubRepositoryReader(
            owner=kwargs.owner, repo=kwargs.repo, github_token=kwargs.github_token
        )

    def _load(self):
        return self.reader.load_data(branch=self.branch)


class S3ContainerReader(BaseReader):
    def __init__(
        self,
        asset_id: str,
        owner: str,
        kwargs: S3ReaderKwargs,
        extra_metadata: Dict[str, Any] = {},
    ):
        super().__init__(asset_id, owner, extra_metadata)
        self.reader = S3Reader(
            bucket=kwargs.bucket_name,
            aws_access_id=kwargs.access_key,
            aws_access_secret=kwargs.secret_key,
            s3_endpoint_url=kwargs.endpoint,
        )

    def _load(self):
        return self.reader.load_data()


def get_reader(
    asset_type: AllowedAssetTypes,
    asset_id: str,
    owner: str,
    kwargs: AllowedReaderKwargs,
    extra_metadata: Dict[str, Any] = {},
) -> BaseReader:
    if asset_type == "github":
        return GitHubReader(asset_id, owner, kwargs, extra_metadata)
    elif asset_type == "s3":
        return S3ContainerReader(asset_id, owner, kwargs, extra_metadata)
    else:
        raise ValueError(f"Asset type {asset_type} is not supported")
