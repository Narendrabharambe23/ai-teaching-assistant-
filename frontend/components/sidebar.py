"""
Sidebar component — file upload, model selector, document list, settings.
"""
import os
import httpx
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

AVAILABLE_MODELS = [
    "llama3.2",
    "llama3.1",
    "mistral",
    "mistral-nemo",
    "qwen2.5",
]


def render_sidebar() -> dict:
    """
    Render the sidebar and return a config dict with selected settings.
    """
    with st.sidebar:
        # ── Logo & Title ──────────────────────────────────────────────────────
        st.markdown("""
        <div style='text-align:center; padding: 10px 0 20px 0;'>
            <div style='font-size:3rem;'>🎓</div>
            <h2 style='color:#7C3AED; margin:0; font-size:1.3rem; font-weight:700;'>
                AI Teaching Assistant
            </h2>
            <p style='color:#94A3B8; font-size:0.8rem; margin:4px 0 0 0;'>
                RAG-Powered • 100% Local
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        # ── Model Selector ────────────────────────────────────────────────────
        st.markdown("### 🤖 AI Model")
        selected_model = st.selectbox(
            "Select Ollama model",
            options=AVAILABLE_MODELS,
            index=0,
            help="Switch between local Ollama models. Larger models give better answers but are slower.",
            label_visibility="collapsed",
        )

        # ── Document Upload ───────────────────────────────────────────────────
        st.markdown("### 📄 Upload Documents")
        uploaded_file = st.file_uploader(
            "Upload PDF or Word documents",
            type=["pdf", "docx", "doc"],
            help="Upload your course materials, textbooks, or notes.",
            label_visibility="collapsed",
        )

        if uploaded_file:
            if st.button("📥 Ingest Document", use_container_width=True, type="primary"):
                _handle_upload(uploaded_file)

        st.divider()

        # ── Uploaded Documents List ───────────────────────────────────────────
        st.markdown("### 📚 Knowledge Base")
        _render_document_list()

        st.divider()

        # ── System Health ─────────────────────────────────────────────────────
        st.markdown("### ⚙️ System Status")
        _render_health_status()

        st.divider()

        # ── Clear All ─────────────────────────────────────────────────────────
        with st.expander("⚠️ Danger Zone"):
            st.warning("This will delete ALL uploaded documents and clear the knowledge base.")
            if st.button("🗑️ Clear Everything", use_container_width=True, type="secondary"):
                with st.spinner("🗑️ Clearing everything..."):
                    try:
                        resp = httpx.delete(f"{BACKEND_URL}/api/v1/documents/clear", timeout=30)
                        if resp.status_code == 200:
                            data = resp.json()
                            st.success(data["message"])
                            if "messages" in st.session_state:
                                st.session_state.messages = []
                            st.rerun()
                        else:
                            st.error(f"Failed: {resp.json().get('detail', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    return {"model": selected_model}


def _handle_upload(uploaded_file):
    """Send file to FastAPI backend for ingestion."""
    with st.spinner(f"📥 Ingesting '{uploaded_file.name}'..."):
        try:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = httpx.post(
                f"{BACKEND_URL}/api/v1/documents/upload",
                files=files,
                timeout=120,
            )
            if response.status_code == 200:
                data = response.json()
                st.success(data["message"])
                st.rerun()
            else:
                error = response.json().get("detail", "Unknown error")
                st.error(f"❌ Upload failed: {error}")
        except httpx.ConnectError:
            st.error("❌ Cannot connect to backend. Is the FastAPI server running?")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")


def _render_document_list():
    """Fetch and display the list of ingested documents."""
    try:
        response = httpx.get(f"{BACKEND_URL}/api/v1/documents/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            docs = data.get("documents", [])
            total = data.get("total", 0)

            if total == 0:
                st.info("No documents uploaded yet.\nUpload a PDF or DOCX above to get started!")
            else:
                st.caption(f"{total} document(s) in knowledge base")
                for doc in docs:
                    size_kb = doc["size_bytes"] / 1024
                    with st.container():
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            ext = doc["filename"].split(".")[-1].upper()
                            icon = "📕" if ext == "PDF" else "📘"
                            st.markdown(
                                f"{icon} **{doc['filename']}**  \n"
                                f"<span style='color:#94A3B8; font-size:0.75rem;'>"
                                f"{size_kb:.0f} KB • {doc['uploaded_at']}"
                                f"</span>",
                                unsafe_allow_html=True,
                            )
        else:
            st.warning("Could not fetch document list.")
    except httpx.ConnectError:
        st.error("Backend offline")
    except Exception:
        st.warning("Could not fetch documents.")


def _render_health_status():
    """Render Ollama and backend health indicators."""
    try:
        response = httpx.get(f"{BACKEND_URL}/health", timeout=3)
        if response.status_code == 200:
            health = response.json()
            ollama_ok = health.get("ollama_connected", False)
            doc_count = health.get("documents_count", 0)

            col1, col2 = st.columns(2)
            with col1:
                if ollama_ok:
                    st.success("🟢 Ollama")
                else:
                    st.error("🔴 Ollama")
            with col2:
                st.info(f"📊 {doc_count} chunks")

            if not ollama_ok:
                st.warning("Run: `ollama serve` in terminal")
        else:
            st.warning("Backend degraded")
    except httpx.ConnectError:
        st.error("🔴 Backend offline\nRun: `uvicorn backend.main:app`")
    except Exception:
        st.warning("Status unavailable")
