"""
Documents API endpoints.
Handles file upload, listing, and clearing of the vector store.
"""
import os
import shutil
import logging
from pathlib import Path
from datetime import datetime, timezone

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

from backend.core.config import settings
from backend.models.schemas import UploadResponse, DocumentsListResponse, DocumentInfo, ClearResponse
from backend.services.ingestion_service import ingest_document, clear_all_documents, get_collection_count

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
MAX_FILE_SIZE_MB = 50


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF or DOCX document and ingest it into the vector store.
    """
    # Validate file extension
    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{suffix}'. Allowed: PDF, DOCX"
        )

    # Validate file size
    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({size_mb:.1f}MB). Maximum allowed: {MAX_FILE_SIZE_MB}MB"
        )

    # Save file to disk
    safe_filename = Path(file.filename).name  # Sanitize filename
    file_path = os.path.join(settings.upload_dir, safe_filename)

    try:
        with open(file_path, "wb") as f:
            f.write(content)
        logger.info(f"Saved uploaded file: {file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Ingest document into ChromaDB
    try:
        chunks_created = ingest_document(file_path, safe_filename)
    except ValueError as e:
        # Remove the saved file if ingestion fails
        os.remove(file_path)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        os.remove(file_path)
        logger.error(f"Ingestion failed for {safe_filename}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(e)}. Is Ollama running? Try: ollama serve"
        )

    return UploadResponse(
        success=True,
        filename=safe_filename,
        chunks_created=chunks_created,
        message=f"✅ Successfully ingested '{safe_filename}' ({chunks_created} chunks created)"
    )


@router.get("/", response_model=DocumentsListResponse)
async def list_documents():
    """
    List all uploaded documents with metadata.
    """
    upload_path = Path(settings.upload_dir)
    documents = []

    if upload_path.exists():
        for file_path in sorted(upload_path.iterdir()):
            if file_path.is_file() and file_path.suffix.lower() in ALLOWED_EXTENSIONS:
                stat = file_path.stat()
                documents.append(DocumentInfo(
                    filename=file_path.name,
                    size_bytes=stat.st_size,
                    uploaded_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                ))

    return DocumentsListResponse(documents=documents, total=len(documents))


@router.delete("/clear", response_model=ClearResponse)
async def clear_all():
    """
    Clear all documents from the vector store and delete uploaded files.
    """
    # Clear ChromaDB
    success = clear_all_documents()

    # Delete all uploaded files
    upload_path = Path(settings.upload_dir)
    files_deleted = 0
    if upload_path.exists():
        for file_path in upload_path.iterdir():
            if file_path.is_file():
                file_path.unlink()
                files_deleted += 1

    if success:
        return ClearResponse(
            success=True,
            message=f"✅ Cleared vector store and deleted {files_deleted} document(s)."
        )
    else:
        raise HTTPException(status_code=500, detail="Failed to clear the vector store.")
