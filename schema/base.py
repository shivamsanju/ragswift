from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, validator


class Document(BaseModel):
    asset_id: str
    doc_id: str
    filename: Optional[str] = ""
    filepath: Optional[str] = ""
    text: str
    metadata: Dict[str, Any]
    uploaded_by: str
    status: str
    message: Optional[str] = ""
    error: bool = False


class Chunk(BaseModel):
    asset_id: str
    chunk_id: str
    doc_id: str
    text: str
    metadata: Dict[str, Any]
    embeddings: Optional[List[float]] = []


class Context(BaseModel):
    text: str
    metadata: str
    score: float = 0


class GithubReader(BaseModel):
    owner: str
    repo: str
    branch: str = "main"
    github_token: str


class S3Reader(BaseModel):
    bucket_name: str
    access_key: str
    secret_key: str
    endpoint: str = None


AllowedAssetTypes = Literal["github", "s3"]
AllowedReaderKwargs = Union[S3Reader, GithubReader]


class IngestionPayload(BaseModel):
    asset_type: AllowedAssetTypes
    asset_id: str
    owner: str
    reader_kwargs: AllowedReaderKwargs
    extra_metadata: Dict[str, Any] = {}

    @validator("reader_kwargs", pre=True, always=True)
    def validate_reader_kwargs(cls, value, values):
        asset_type = values.get("asset_type")
        if asset_type == "github":
            GithubReader.model_validate(value)
        elif asset_type == "s3":
            S3Reader.model_validate(value)
        return value


class RetrievalPayload(BaseModel):
    query: str
    asset_ids: List[str]
    num_contexts: int = 10
    score_threshold: float = 1
