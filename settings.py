from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Basic
    HTTP_PORT: int = 8000
    ENV: Literal["development", "production", "testing", "docker"] = "development"

    # Ray config
    RAY_ADDRESS: str = "auto"
    RAY_DASHBOARD_ADDRESS: str = (
        "http://172.17.0.1:8265" if ENV == "docker" else "http://127.0.0.1:8265"
    )
    MAX_INGESTION_JOB_WORKERS: int = 2
    PARALLEL_INGESTION_JOBS: int = 1

    @computed_field
    @property
    def INGESTION_WORKERS_PER_JOB(self) -> int:
        return self.MAX_INGESTION_JOB_WORKERS // self.PARALLEL_INGESTION_JOBS

    # Model configs
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"
    USE_SENTENCE_TRANSFORMERS: bool = True
    EMBEDDING_DIMENSION: int = 384
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 100
    RERANKER_MODEL: str = "cross-encoder/ms-marco-TinyBERT-L-2-v2"

    # Vector db config
    VECTOR_DB_COLLECTION_NAME: str = "default"
    QDRANT_BASE_URI: str = "172.17.0.1" if ENV == "docker" else "127.0.0.1"
    QDRANT_API_KEY: str
    QDRANT_PORT: str = "6333"
    QDRANT_GRPC_PORT: str = "6334"
    QDRANT_PREFER_GRPC: str = "0"

    # S3 config
    S3_ENDPOINT: str = "172.17.0.1:9000" if ENV == "docker" else "127.0.0.1:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"


settings = Settings()
