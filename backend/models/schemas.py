"""Pydantic schemas for request and response models."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ─── Document Schemas ─────────────────────────────────────────────────────────

class DocumentInfo(BaseModel):
    filename: str
    size_bytes: int
    uploaded_at: str
    chunk_count: Optional[int] = None


class UploadResponse(BaseModel):
    success: bool
    filename: str
    chunks_created: int
    message: str


class DocumentsListResponse(BaseModel):
    documents: List[DocumentInfo]
    total: int


class ClearResponse(BaseModel):
    success: bool
    message: str


# ─── Chat Schemas ──────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000, description="The student's question")
    model: Optional[str] = Field(default=None, description="Override LLM model name")
    top_k: Optional[int] = Field(default=None, ge=1, le=10, description="Number of context chunks")


class SourceDocument(BaseModel):
    source: str
    page: Optional[int] = None
    content_preview: str


class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    model_used: str
    chunks_retrieved: int


# ─── Health Schema ─────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    ollama_connected: bool
    ollama_url: str
    llm_model: str
    embed_model: str
    documents_count: int
    chroma_collection: str
