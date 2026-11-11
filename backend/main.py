"""
FastAPI main application entry point.
Includes CORS, health check, and API routers.
"""
import logging
import httpx
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.core.config import settings
from backend.api.v1.router import api_router
from backend.models.schemas import HealthResponse
from backend.services.ingestion_service import get_collection_count

# ─── Logging Setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ─── Startup / Shutdown ───────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Check Ollama connectivity on startup."""
    logger.info("🚀 AI Teaching Assistant starting up...")
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
                logger.info(f"✅ Ollama connected. Available models: {models}")
            else:
                logger.warning("⚠️  Ollama responded but with unexpected status.")
    except Exception:
        logger.warning(
            "⚠️  Could not connect to Ollama at startup. "
            f"Ensure it's running: ollama serve  (URL: {settings.ollama_base_url})"
        )

    logger.info(f"📚 ChromaDB collection: '{settings.collection_name}' at '{settings.chroma_path}'")
    logger.info(f"🤖 LLM Model: {settings.llm_model} | Embed Model: {settings.embed_model}")
    yield
    logger.info("🛑 AI Teaching Assistant shutting down.")


# ─── FastAPI App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="🎓 AI Teaching Assistant API",
    description="RAG-based AI Teaching Assistant — powered by LangChain, ChromaDB, and Ollama",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",   # Streamlit default
        "http://127.0.0.1:8501",
        "http://localhost:3000",   # Dev tools
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(api_router, prefix="/api/v1")


# ─── Health Check ─────────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check system health: Ollama connection, vector store, and config."""
    ollama_ok = False
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            ollama_ok = resp.status_code == 200
    except Exception:
        pass

    return HealthResponse(
        status="ok" if ollama_ok else "degraded",
        ollama_connected=ollama_ok,
        ollama_url=settings.ollama_base_url,
        llm_model=settings.llm_model,
        embed_model=settings.embed_model,
        documents_count=get_collection_count(),
        chroma_collection=settings.collection_name,
    )


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "🎓 AI Teaching Assistant API is running!",
        "docs": "/docs",
        "health": "/health",
        "api": "/api/v1",
    }
