"""
Configuration settings for the RAG Teaching Assistant.
Reads from .env file using Pydantic BaseSettings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
import os


class Settings(BaseSettings):
    # Ollama
    ollama_base_url: str = Field(default="http://localhost:11434", env="OLLAMA_BASE_URL")
    llm_model: str = Field(default="llama3.2", env="LLM_MODEL")
    embed_model: str = Field(default="nomic-embed-text", env="EMBED_MODEL")

    # ChromaDB
    chroma_path: str = Field(default="data/vector_db/chroma_db", env="CHROMA_PATH")
    collection_name: str = Field(default="teaching_materials", env="COLLECTION_NAME")

    # Document storage
    upload_dir: str = Field(default="data/raw_documents", env="UPLOAD_DIR")

    # RAG settings
    chunk_size: int = Field(default=800, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=150, env="CHUNK_OVERLAP")
    top_k: int = Field(default=4, env="TOP_K")
    fetch_k: int = Field(default=15, env="FETCH_K")

    # FastAPI server
    backend_host: str = Field(default="0.0.0.0", env="BACKEND_HOST")
    backend_port: int = Field(default=8000, env="BACKEND_PORT")

    # Streamlit → Backend URL
    backend_url: str = Field(default="http://localhost:8000", env="BACKEND_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global settings singleton
settings = Settings()

# Ensure required directories exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.chroma_path, exist_ok=True)
