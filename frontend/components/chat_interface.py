"""
Chat interface component — message history, streaming display, source citations.
"""
import os
import httpx
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def initialize_chat_state():
    """Initialize Streamlit session state for chat."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "is_thinking" not in st.session_state:
        st.session_state.is_thinking = False


def render_chat_header():
    """Render the main chat area header."""
    st.markdown("""
    <style>
    .chat-header {
        background: linear-gradient(135deg, #1A1A2E 0%, #16213E 50%, #0F3460 100%);
        border: 1px solid rgba(124, 58, 237, 0.3);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        text-align: center;
    }
    .chat-header h1 {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #7C3AED, #A78BFA, #60A5FA);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 8px 0;
    }
    .chat-header p {
        color: #94A3B8;
        font-size: 1rem;
        margin: 0;
    }
    .message-user {
        background: linear-gradient(135deg, rgba(124,58,237,0.15), rgba(124,58,237,0.05));
        border: 1px solid rgba(124,58,237,0.2);
        border-radius: 16px 16px 4px 16px;
        padding: 14px 18px;
        margin: 8px 0;
    }
    .message-assistant {
        background: rgba(26, 26, 46, 0.8);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px 16px 16px 4px;
        padding: 14px 18px;
        margin: 8px 0;
    }
    .source-card {
        background: rgba(124, 58, 237, 0.08);
        border: 1px solid rgba(124, 58, 237, 0.2);
        border-radius: 8px;
        padding: 10px 14px;
        margin: 4px 0;
        font-size: 0.82rem;
    }
    .source-title {
        color: #A78BFA;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .source-preview {
        color: #94A3B8;
        font-size: 0.78rem;
        margin-top: 4px;
        line-height: 1.4;
    }

  
    .thinking-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #A78BFA;
        font-style: italic;
        padding: 12px 18px;
    }
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        color: #64748B;
    }
    .empty-state .icon { font-size: 4rem; margin-bottom: 16px; }
    .empty-state h3 { color: #94A3B8; font-size: 1.3rem; margin: 0 0 8px 0; }
    .suggestion-chip {
        display: inline-block;
        background: rgba(124,58,237,0.1);
        border: 1px solid rgba(124,58,237,0.25);
        border-radius: 20px;
        padding: 6px 14px;
        margin: 4px;
        font-size: 0.82rem;
        color: #A78BFA;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="chat-header">
        <h1>🎓 AI Teaching Assistant</h1>
        <p>Upload your course materials and ask me anything — I'll answer from your documents</p>
    </div>
    """, unsafe_allow_html=True)


def render_chat_messages():
    """Render all chat messages with styling."""
    if not st.session_state.messages:
        _render_empty_state()
        return

    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        sources = msg.get("sources", [])

        if role == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(content)
        else:
            with st.chat_message("assistant", avatar="🎓"):
                st.markdown(content)
                if sources:
                    _render_sources(sources)


def _render_empty_state():
    """Show welcome message and example questions when no chat history."""
    st.markdown("""
    <div class="empty-state">
        <div class="icon">📚</div>
        <h3>Ready to help you learn!</h3>
        <p>Upload your course materials in the sidebar, then ask me anything about them.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Try asking:**")
    sample_questions = [
        "📖 Summarize the main topics in this document",
        "🔍 Explain the concept of [key term]",
        "❓ What are the key points from chapter 1?",
        "🧪 Give me examples of [concept]",
    ]
    cols = st.columns(2)
    for i, q in enumerate(sample_questions):
        with cols[i % 2]:
            st.markdown(
                f"<div class='suggestion-chip'>{q}</div>",
                unsafe_allow_html=True
            )


def _render_sources(sources: list):
    """Render source citation cards below an assistant message."""
    if not sources:
        return

    with st.expander(f"📎 {len(sources)} source(s) used", expanded=False):
        for src in sources:
            page_info = f" • Page {src.get('page')}" if src.get('page') else ""
            st.markdown(
                f"""<div class="source-card">
                    <div class="source-title">📄 {src['source']}{page_info}</div>
                    <div class="source-preview">{src.get('content_preview', '')}</div>
                </div>""",
                unsafe_allow_html=True,
            )


def handle_user_input(model: str):
    """Process user input from chat box and call the RAG backend."""
    question = st.chat_input("Ask a question about your uploaded documents...", key="chat_input")

    if not question:
        return

    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": question})

    # Display user message immediately
    with st.chat_message("user", avatar="👤"):
        st.markdown(question)

    # Query backend and display response
    with st.chat_message("assistant", avatar="🎓"):
        with st.spinner("🤔 Thinking..."):
            try:
                response = httpx.post(
                    f"{BACKEND_URL}/api/v1/chat/",
                    json={
                        "question": question,
                        "model": model,
                    },
                    timeout=180,  # Large timeout for slow local models
                )

                if response.status_code == 200:
                    data = response.json()
                    answer = data["answer"]
                    sources = data.get("sources", [])
                    model_used = data.get("model_used", model)
                    chunks = data.get("chunks_retrieved", 0)

                    st.markdown(answer)

                    # Show sources
                    if sources:
                        _render_sources(sources)

                    # Meta info
                    st.caption(f"🤖 {model_used} • 📊 {chunks} chunks retrieved")

                    # Save to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    })

                elif response.status_code == 400:
                    error_msg = response.json().get("detail", "No documents found.")
                    st.warning(f"⚠️ {error_msg}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"⚠️ {error_msg}",
                        "sources": [],
                    })
                elif response.status_code == 503:
                    st.error("❌ Ollama is not running. Please run `ollama serve` in your terminal.")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "❌ Ollama is not running. Please run `ollama serve` in your terminal.",
                        "sources": [],
                    })
                else:
                    error = response.json().get("detail", "Unknown error")
                    st.error(f"❌ Error: {error}")

            except httpx.ConnectError:
                msg = "❌ Cannot connect to the backend server. Make sure it's running:\n\n```\nuvicorn backend.main:app --reload\n```"
                st.error(msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": msg,
                    "sources": [],
                })
            except httpx.TimeoutException:
                msg = "⏱️ The response timed out. The model might be too slow. Try a smaller model like `llama3.2`."
                st.warning(msg)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": msg,
                    "sources": [],
                })
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")


def render_clear_chat_button():
    """Render a button to clear the chat history."""
    if st.session_state.messages:
        if st.button("🗑️ Clear Chat", key="clear_chat", help="Clear conversation history"):
            st.session_state.messages = []
            st.rerun()


def _handle_clear():
    """Call backend to clear all documents and vector store."""
    with st.spinner("🗑️ Clearing everything..."):
        try:
            resp = httpx.delete(f"{BACKEND_URL}/api/v1/documents/clear", timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                st.success(data["message"])
                st.session_state.messages = []
                st.rerun()
            else:
                st.error(f"Failed to clear: {resp.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
