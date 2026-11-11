"""
Main Streamlit application entry point.
Assembles all components into the full Teaching Assistant UI.
"""
import sys
import os

# Ensure project root is in path (for running as: streamlit run frontend/streamlit_app.py)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
from frontend.components.sidebar import render_sidebar
from frontend.components.chat_interface import (
    initialize_chat_state,
    render_chat_header,
    render_chat_messages,
    handle_user_input,
    render_clear_chat_button,
)

# ─── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="🎓 AI Teaching Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "🎓 RAG-Based AI Teaching Assistant — Powered by LangChain, ChromaDB & Ollama",
    },
)

# ─── Global CSS Overrides ─────────────────────────────────────────────────────
st.markdown("""
<style>
/* Import Google Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Global font */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Main background */
.stApp {
    background: linear-gradient(160deg, #0F0F1A 0%, #0D0D1A 60%, #0A0A18 100%);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D0D1E 0%, #111128 100%) !important;
    border-right: 1px solid rgba(124, 58, 237, 0.2) !important;
}

/* Chat input box */
[data-testid="stChatInput"] textarea {
    background: rgba(26, 26, 46, 0.9) !important;
    border: 1px solid rgba(124, 58, 237, 0.3) !important;
    border-radius: 12px !important;
    color: #E2E8F0 !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: rgba(124, 58, 237, 0.7) !important;
    box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.15) !important;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border-radius: 16px !important;
    padding: 4px 0 !important;
}

/* Primary button */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #7C3AED, #6D28D9) !important;
    border: none !important;
    border-radius: 10px !important;
    color: white !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #8B5CF6, #7C3AED) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4) !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: rgba(26, 26, 46, 0.6) !important;
    border: 1px solid rgba(124, 58, 237, 0.15) !important;
    border-radius: 10px !important;
}

/* Divider */
hr {
    border-color: rgba(124, 58, 237, 0.2) !important;
}

/* Spinner */
.stSpinner > div {
    border-top-color: #7C3AED !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0F0F1A; }
::-webkit-scrollbar-thumb { background: rgba(124, 58, 237, 0.4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(124, 58, 237, 0.7); }

/* Select box */
[data-testid="stSelectbox"] select {
    background: rgba(26, 26, 46, 0.9) !important;
    border: 1px solid rgba(124, 58, 237, 0.3) !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: rgba(26, 26, 46, 0.4) !important;
    border: 2px dashed rgba(124, 58, 237, 0.3) !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(124, 58, 237, 0.6) !important;
}

/* Success/error/warning messages */
[data-testid="stAlert"] {
    border-radius: 10px !important;
}

/* Top toolbar padding fix */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 900px !important;
}
</style>
""", unsafe_allow_html=True)


# ─── Main App ─────────────────────────────────────────────────────────────────
def main():
    # Initialize session state
    initialize_chat_state()

    # Render sidebar and get config
    config = render_sidebar()
    selected_model = config.get("model", "llama3.2")

    # Render main chat area
    render_chat_header()

    # Top-right clear chat button
    col1, col2 = st.columns([6, 1])
    with col2:
        render_clear_chat_button()

    # Chat messages display
    render_chat_messages()

    # Chat input — handles user question → backend → response
    handle_user_input(model=selected_model)


if __name__ == "__main__":
    main()
