"""Configuration management for RAG application."""

import logging
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Load values from .env
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    # Pinecone Configuration
    pinecone_api_key: str
    pinecone_index_name: str = "agentic-ai-index"
    pinecone_environment: str = "us-east-1"
    pinecone_dimension: int = 1536

    # RAG Configuration
    retrieval_top_k: int = 3
    confidence_threshold: float = 0.5
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Application Configuration
    log_level: str = "INFO"
    pdf_path: str = "data/Ebook-Agentic-AI.pdf"

    @field_validator("openai_api_key", "pinecone_api_key")
    @classmethod
    def validate_api_keys(cls, value: str) -> str:
        """Ensure required API keys are not empty."""
        if not value or not value.strip():
            raise ValueError("API key cannot be empty")
        return value

    def get_logger(self) -> logging.Logger:
        """Get configured logger."""
        logger = logging.getLogger("rag_chatbot")

        if logger.hasHandlers():
            return logger

        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, self.log_level.upper(), logging.INFO))

        return logger


_logger: Optional[logging.Logger] = None


def load_settings() -> Settings:
    """Load settings from environment variables."""
    global _logger

    settings = Settings()
    _logger = settings.get_logger()

    _logger.info("Configuration loaded successfully")

    return settings


def get_logger() -> logging.Logger:
    """Get the global logger instance."""

    if _logger is None:
        logger = logging.getLogger("rag_chatbot")

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )

            handler.setFormatter(formatter)
            logger.addHandler(handler)

        logger.setLevel(logging.INFO)
        return logger

    return _logger