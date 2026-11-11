"""
Chat API endpoint.
Handles RAG-powered Q&A queries from the Streamlit frontend.
"""
import logging
from fastapi import APIRouter, HTTPException

from backend.models.schemas import ChatRequest, ChatResponse, SourceDocument
from backend.services.llm_service import query_rag
from backend.services.ingestion_service import get_collection_count
from backend.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a student question using RAG and return an answer with source citations.
    """
    # Check if any documents have been ingested
    chunk_count = get_collection_count()
    if chunk_count == 0:
        raise HTTPException(
            status_code=400,
            detail="No documents found in the knowledge base. Please upload PDF or DOCX files first."
        )

    try:
        answer, source_docs = query_rag(
            question=request.question,
            model=request.model,
            top_k=request.top_k,
        )
    except ConnectionError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Cannot connect to Ollama. Make sure it's running: ollama serve — Error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Chat query failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {str(e)}"
        )

    # Build source citations
    sources = []
    seen_sources = set()
    for doc in source_docs:
        source_name = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", None)
        key = f"{source_name}_{page}"

        if key not in seen_sources:
            seen_sources.add(key)
            sources.append(SourceDocument(
                source=source_name,
                page=int(page) + 1 if page is not None else None,
                content_preview=doc.page_content[:200].strip() + "...",
            ))

    return ChatResponse(
        answer=answer,
        sources=sources,
        model_used=request.model or settings.llm_model,
        chunks_retrieved=len(source_docs),
    )
