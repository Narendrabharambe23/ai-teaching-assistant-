"""
LLM Service — builds the RAG chain and runs queries.
Uses LCEL (LangChain Expression Language) for chain composition.
"""
import logging
from typing import Optional, List, Tuple

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from backend.core.config import settings

logger = logging.getLogger(__name__)

# ─── Teaching System Prompt ───────────────────────────────────────────────────
TEACHING_SYSTEM_PROMPT = """You are an expert AI Teaching Assistant helping students learn from their uploaded course materials.

STRICT RULES:
1. Answer ONLY using the provided context from the uploaded documents.
2. If the answer is NOT in the context, say exactly: "I don't have that information in the uploaded materials. Please check with your professor or refer to additional resources."
3. NEVER fabricate, guess, or use outside knowledge.
4. Always be encouraging, clear, and educational in tone.
5. When explaining concepts, use simple language and reference specific parts of the context.
6. If asked to summarize, cover the key points from the context.
7. Cite the source document and page when possible.

Context from uploaded documents:
{context}
"""

TEACHING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", TEACHING_SYSTEM_PROMPT),
    ("human", "{question}"),
])


def _format_docs(docs: List[Document]) -> str:
    """Format retrieved documents into a readable context string."""
    formatted = []
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page", "")
        page_info = f", Page {page + 1}" if page != "" else ""
        formatted.append(
            f"[Document {i} — {source}{page_info}]\n{doc.page_content.strip()}"
        )
    return "\n\n---\n\n".join(formatted)


def get_retriever(model: Optional[str] = None):
    """Initialize ChromaDB retriever with MMR search."""
    embeddings = OllamaEmbeddings(
        model=settings.embed_model,
        base_url=settings.ollama_base_url,
    )
    vectorstore = Chroma(
        collection_name=settings.collection_name,
        embedding_function=embeddings,
        persist_directory=settings.chroma_path,
    )
    retriever = vectorstore.as_retriever(
        search_type="mmr",  # Max Marginal Relevance — avoids redundant chunks
        search_kwargs={
            "k": settings.top_k,
            "fetch_k": settings.fetch_k,
        },
    )
    return retriever


def query_rag(question: str, model: Optional[str] = None, top_k: Optional[int] = None) -> Tuple[str, List[Document]]:
    """
    Run a RAG query and return (answer, source_documents).

    Args:
        question: The student's question
        model: Override LLM model (defaults to settings.llm_model)
        top_k: Override number of chunks to retrieve

    Returns:
        Tuple of (answer_text, list_of_source_documents)
    """
    llm_model = model or settings.llm_model
    logger.info(f"Running RAG query with model={llm_model}: '{question[:80]}...'")

    # Override top_k in retriever if specified
    embeddings = OllamaEmbeddings(
        model=settings.embed_model,
        base_url=settings.ollama_base_url,
    )
    vectorstore = Chroma(
        collection_name=settings.collection_name,
        embedding_function=embeddings,
        persist_directory=settings.chroma_path,
    )

    k = top_k or settings.top_k
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": k, "fetch_k": settings.fetch_k},
    )

    # Retrieve relevant documents
    source_docs = retriever.invoke(question)

    if not source_docs:
        return (
            "I couldn't find any relevant information in the uploaded documents to answer your question. "
            "Please make sure you've uploaded relevant course materials.",
            [],
        )

    # Build context
    context = _format_docs(source_docs)

    # Initialize LLM
    llm = ChatOllama(
        model=llm_model,
        base_url=settings.ollama_base_url,
        temperature=0.1,  # Low temp for factual, grounded answers
        timeout=120,
    )

    # Build and invoke chain
    chain = TEACHING_PROMPT | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question})

    logger.info(f"RAG query completed. Retrieved {len(source_docs)} chunks.")
    return answer, source_docs
