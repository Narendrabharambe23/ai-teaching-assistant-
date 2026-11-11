# 🎓 AI Teaching Assistant — RAG-Powered

A **100% local, cost-free AI Teaching Assistant** that answers questions from your uploaded course materials using Retrieval-Augmented Generation (RAG).

Built with **LangChain · ChromaDB · Ollama · FastAPI · Streamlit**.

---

## 🏗️ Architecture

```
Streamlit UI (Chat + Upload)
        ↕  HTTP
FastAPI Backend
    ├── Document Ingestion  →  ChromaDB (Vector DB)
    └── RAG Query  →  ChromaDB + Ollama (LLM)
```

---

## 📋 Prerequisites

### 1. Python 3.10+
```bash
python --version   # Should be 3.10 or higher
```

### 2. Ollama (Local AI Models)
Download and install from: **https://ollama.com**

After install, pull the required models:
```bash
# Pull the LLM (choose based on your RAM)
ollama pull llama3.2        # Recommended for 8GB RAM  (~2GB download)
ollama pull llama3.1        # Better answers, needs 16GB RAM  (~4.7GB)
ollama pull mistral         # Best for teaching, needs 16GB RAM  (~4.1GB)

# Pull the embedding model (REQUIRED — always)
ollama pull nomic-embed-text
```

Check that Ollama is running:
```bash
ollama serve      # Start Ollama server
ollama list       # Should show your pulled models
```

---

## 🚀 Setup & Installation

### Step 1 — Clone / navigate to project
```bash
cd ai-teaching-assistant
```

### Step 2 — Create a virtual environment
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Configure settings (optional)
The `.env` file is pre-configured with defaults. Edit it if you want to:
- Change the default model
- Use a different Ollama URL
- Adjust chunk size

```env
LLM_MODEL=llama3.2          # Change to mistral or llama3.1
EMBED_MODEL=nomic-embed-text
OLLAMA_BASE_URL=http://localhost:11434
```

---

## ▶️ Running the Application

You need **3 terminals** running simultaneously:

### Terminal 1 — Start Ollama
```bash
ollama serve
```

### Terminal 2 — Start FastAPI Backend
```bash
# From the ai-teaching-assistant/ directory
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
✅ Backend runs at: http://localhost:8000
📚 API Docs at: http://localhost:8000/docs

### Terminal 3 — Start Streamlit Frontend
```bash
# From the ai-teaching-assistant/ directory
streamlit run frontend/streamlit_app.py
```
✅ Frontend runs at: http://localhost:8501

---

## 📖 How to Use

1. **Upload documents** — Click "Upload Documents" in the sidebar → select a PDF or DOCX
2. **Wait for ingestion** — The app will chunk and embed your document (takes 10–30 seconds)
3. **Ask questions** — Type your question in the chat box and press Enter
4. **View sources** — Click "📎 N source(s) used" to see which parts of your document were cited
5. **Switch models** — Use the model dropdown in the sidebar to switch Ollama models

---

## 📁 Project Structure

```
ai-teaching-assistant/
├── .env                    ← Configuration (edit model names here)
├── requirements.txt        ← Python dependencies
│
├── backend/
│   ├── main.py            ← FastAPI app entry point
│   ├── core/config.py     ← Settings (reads from .env)
│   ├── models/schemas.py  ← Pydantic request/response models
│   ├── api/v1/            ← REST API routes
│   │   └── endpoints/
│   │       ├── documents.py  ← Upload, list, clear
│   │       └── chat.py       ← RAG Q&A
│   └── services/
│       ├── ingestion_service.py  ← Load → Chunk → Embed → Store
│       └── llm_service.py        ← Retrieve → Prompt → Generate
│
├── frontend/
│   ├── streamlit_app.py   ← Main Streamlit UI
│   └── components/
│       ├── sidebar.py        ← File upload, model selector
│       └── chat_interface.py ← Chat UI, source citations
│
└── data/
    ├── raw_documents/     ← Uploaded files stored here
    └── vector_db/         ← ChromaDB persists here (backup this!)
```

---

## 🔧 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Check Ollama, ChromaDB status |
| `POST` | `/api/v1/documents/upload` | Upload & ingest a PDF/DOCX |
| `GET` | `/api/v1/documents/` | List all uploaded documents |
| `DELETE` | `/api/v1/documents/clear` | Clear all documents & vector store |
| `POST` | `/api/v1/chat/` | Ask a question (RAG query) |

Full interactive docs: **http://localhost:8000/docs**

---

## ❓ Troubleshooting

| Problem | Fix |
|---------|-----|
| "Cannot connect to Ollama" | Run `ollama serve` in a terminal |
| "No model named llama3.2" | Run `ollama pull llama3.2` |
| "Empty or scanned PDF" | Use a text-based PDF, not image scans |
| Response is very slow | Switch to `llama3.2` (smaller model) |
| Irrelevant answers | Upload more specific course materials |
| Import errors | Make sure you ran `pip install -r requirements.txt` |
| ChromaDB version error | Run `pip install "chromadb>=0.5.0" "langchain-chroma>=0.1.0"` |

---

## 📦 Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Ollama (llama3.2 / mistral / llama3.1) |
| Embeddings | nomic-embed-text via Ollama |
| Vector DB | ChromaDB ≥ 0.5 (persistent local) |
| RAG Framework | LangChain ≥ 0.3 (modular packages) |
| Backend | FastAPI + uvicorn |
| Frontend | Streamlit ≥ 1.39 |
| PDF Parser | PyMuPDF (pymupdf) |
| DOCX Parser | Docx2txt / python-docx |

---

## 🌟 Features

- ✅ 100% local — no API keys, no costs
- ✅ PDF and Word document support
- ✅ Source citations with page numbers
- ✅ MMR retrieval (no redundant context)
- ✅ Model selector (switch LLMs in UI)
- ✅ Persistent vector store (survives restarts)
- ✅ Beautiful dark theme chat UI
- ✅ System health monitoring
- ✅ Grounded answers (won't hallucinate)
