"""
Document Ingestion Service.
Handles: Load → Split → Embed → Store in ChromaDB.
"""
import os
import logging
from pathlib import Path
from typing import Optional

from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

from backend.core.config import settings

logger = logging.getLogger(__name__)


def get_vectorstore(embed_model: Optional[str] = None) -> Chroma:
    """Initialize and return ChromaDB vector store."""
    embeddings = OllamaEmbeddings(
        model=embed_model or settings.embed_model,
        base_url=settings.ollama_base_url,
    )
    vectorstore = Chroma(
        collection_name=settings.collection_name,
        embedding_function=embeddings,
        persist_directory=settings.chroma_path,
    )
    return vectorstore


def load_document(file_path: str) -> list:
    """Load a PDF or DOCX file and return list of LangChain Documents."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        loader = PyMuPDFLoader(str(path))
        logger.info(f"Loading PDF: {path.name}")
    elif suffix in (".docx", ".doc"):
        loader = Docx2txtLoader(str(path))
        logger.info(f"Loading DOCX: {path.name}")
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Only PDF and DOCX are supported.")

    docs = loader.load()

    # Check for empty content (e.g., scanned image-only PDFs)
    total_chars = sum(len(d.page_content.strip()) for d in docs)
    if total_chars < 50:
        raise ValueError(
            f"The file '{path.name}' appears to be empty or is a scanned image PDF. "
            "Please use a text-based PDF or convert it first."
        )

    return docs


def ingest_document(file_path: str, filename: str) -> int:
    """
    Full ingestion pipeline: Load → Split → Embed → Store.
    Returns number of chunks created.
    """
    logger.info(f"Starting ingestion for: {filename}")

    # 1. Load document
    docs = load_document(file_path)
    logger.info(f"Loaded {len(docs)} pages/sections from {filename}")

    # 2. Enrich metadata
    for doc in docs:
        doc.metadata["source"] = filename
        doc.metadata["doc_type"] = Path(filename).suffix.lower().lstrip(".")

    # 3. Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len,
    )
    chunks = splitter.split_documents(docs)
    logger.info(f"Split into {len(chunks)} chunks")

    if not chunks:
        raise ValueError("No content could be extracted from the document.")

    # 4. Store in ChromaDB (embeddings generated automatically)
    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)
    logger.info(f"Stored {len(chunks)} chunks in ChromaDB for: {filename}")

    return len(chunks)


def delete_document_chunks(filename: str) -> int:
    """Delete all ChromaDB chunks belonging to a specific filename."""
    vectorstore = get_vectorstore()
    collection = vectorstore._collection

    # Find all chunk IDs where source == filename
    results = collection.get(where={"source": filename})
    ids_to_delete = results.get("ids", [])

    if ids_to_delete:
        collection.delete(ids=ids_to_delete)
        logger.info(f"Deleted {len(ids_to_delete)} chunks for: {filename}")

    return len(ids_to_delete)


def clear_all_documents() -> bool:
    """Delete the entire ChromaDB collection and reset it."""
    try:
        vectorstore = get_vectorstore()
        vectorstore.delete_collection()
        logger.info("ChromaDB collection cleared successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to clear ChromaDB: {e}")
        return False


def get_collection_count() -> int:
    """Return total number of chunks stored in ChromaDB."""
    try:
        vectorstore = get_vectorstore()
        return vectorstore._collection.count()
    except Exception:
        return 0
