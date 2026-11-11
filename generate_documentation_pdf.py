"""
Master Architecture, Verification, and Workflow PDF Documentation Generator
Integrates all architectural specifications, verified code audits, error matrix,
limitations, roadmap, glossary, quick reference, and interview guides.
"""
import os
import sys
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable,
)
from reportlab.pdfgen import canvas

# ─── Color Palette ────────────────────────────────────────────────────────────
PRIMARY = colors.HexColor("#7C3AED")      # Electric violet
PRIMARY_LIGHT = colors.HexColor("#EDE9FE")# Light violet background
SECONDARY = colors.HexColor("#1E1B4B")    # Deep navy
TEXT_DARK = colors.HexColor("#0F172A")    # Slate 900
TEXT_MUTED = colors.HexColor("#475569")   # Slate 600
BG_CODE = colors.HexColor("#F8FAFC")      # Slate 50
BORDER_COLOR = colors.HexColor("#CBD5E1") # Slate 300
SUCCESS_COLOR = colors.HexColor("#059669")# Emerald 600
HEADER_BG = colors.HexColor("#F1F5F9")    # Slate 100
WARN_COLOR = colors.HexColor("#D97706")   # Amber 600
DANGER_COLOR = colors.HexColor("#DC2626") # Red 600


class NumberedCanvas(canvas.Canvas):
    """Canvas that computes total pages dynamically for 'Page X of Y' footer."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        if self._pageNumber == 1:
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(TEXT_MUTED)

        # Header
        self.drawString(54, 11 * inch - 36, "RAG AI Teaching Assistant — Comprehensive Technical Specification")
        self.setStrokeColor(BORDER_COLOR)
        self.setLineWidth(0.5)
        self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)

        # Footer
        self.line(54, 46, 8.5 * inch - 54, 46)
        self.drawString(54, 34, "Technical Audit & Architecture • Local Prototype Implementation")
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(8.5 * inch - 54, 34, page_str)
        self.restoreState()


def build_pdf(filename: str):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # ─── Custom Typography ────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=30,
        textColor=SECONDARY,
    )
    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=PRIMARY,
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=18,
        textColor=PRIMARY,
        spaceBefore=11,
        spaceAfter=5,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14.5,
        textColor=SECONDARY,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True,
    )
    h3_style = ParagraphStyle(
        "Heading3_Custom",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12.5,
        textColor=TEXT_DARK,
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.8,
        leading=11.2,
        textColor=TEXT_DARK,
        spaceAfter=3.5,
    )
    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.8,
        leading=11.2,
        textColor=TEXT_DARK,
        leftIndent=10,
        spaceAfter=2,
    )
    code_box = ParagraphStyle(
        "Code_Box",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7,
        leading=9.5,
        textColor=SECONDARY,
    )
    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=9.5,
        textColor=TEXT_DARK,
    )
    table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        textColor=SECONDARY,
    )

    story = []

    # ═══════════════════════════════════════════════════════════════════════════
    # 1. COVER PAGE
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 25))
    story.append(Paragraph("TECHNICAL ARCHITECTURE, AUDIT & WORKFLOW SPECIFICATION", subtitle_style))
    story.append(Spacer(1, 5))
    story.append(Paragraph("RAG-Powered AI Teaching Assistant", title_style))
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceBefore=0, spaceAfter=10))

    story.append(Paragraph(
        "Comprehensive architectural and workflow specification for an on-device, zero-cost "
        "Retrieval-Augmented Generation (RAG) system. Engineered with LangChain (v0.3), "
        "ChromaDB (v0.5), FastAPI, Streamlit, and local quantized LLM inference via Ollama "
        "(Meta Llama 3.2 3B and Nomic Embed Text). Includes verified code audits, error matrix, "
        "technical debt evaluation, limitations, and a prioritized engineering roadmap.",
        body_style
    ))
    story.append(Spacer(1, 10))

    meta_table_data = [
        [Paragraph("<b>Project Name:</b>", table_header), Paragraph("AI Teaching Assistant (Package: <code>ai-teaching-assistant</code>)", table_cell)],
        [Paragraph("<b>Author / Role:</b>", table_header), Paragraph("Senior Software Architect & Technical Lead", table_cell)],
        [Paragraph("<b>Current Architecture Status:</b>", table_header), Paragraph("<b>Local Prototype / Functional Proof-of-Concept (PoC)</b> (Verified for single-user local educational use; not enterprise production-ready)", table_cell)],
        [Paragraph("<b>Codebase Location:</b>", table_header), Paragraph("C:\\Users\\naren\\IT VEDANT PROJECT\\ai-teaching-assistant", table_cell)],
        [Paragraph("<b>Host Environment:</b>", table_header), Paragraph("Microsoft Windows 11 / Python 3.13 / Ollama Engine (:11434)", table_cell)],
        [Paragraph("<b>Audit Date:</b>", table_header), Paragraph(datetime.now().strftime("%B %d, %Y"), table_cell)],
    ]
    t_meta = Table(meta_table_data, colWidths=[120, 384])
    t_meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BG_CODE),
        ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_meta)

    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>REALISTIC STATUS & EXECUTIVE AUDIT SUMMARY</b>", h2_style))
    story.append(Paragraph(
        "<b>Architectural Realignment:</b> While earlier documentation drafts described this system as 'Production Ready', "
        "an objective engineering audit confirms that this codebase is a <b>high-performing Local Development Prototype and Proof-of-Concept (PoC)</b>. "
        "All primary functional workflows (document ingestion, chunking, Ollama vectorization, ChromaDB storage, MMR retrieval, and citation Q&A) "
        "are completely operational and verified locally. However, enterprise production characteristics (such as multi-user authentication, tenant isolation, "
        "asynchronous background queues for large files, and automated unit test suites) are not yet implemented.",
        body_style
    ))
    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # 2. CODE VERIFICATION FINDINGS
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("PART 1: RIGOROUS CODE VERIFICATION FINDINGS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=8))

    audit_data = [
        [Paragraph("Audit Item", table_header), Paragraph("Code Inspection & Empirical Result", table_header), Paragraph("Architectural Consequence", table_header)],
        [
            Paragraph("<b>(a) Chroma Distance Metric & Location</b>", table_cell),
            Paragraph("In <code>ingestion_service.py:20</code>, <code>get_vectorstore()</code> creates Chroma without <code>collection_metadata</code>. Direct inspection of <code>chroma.sqlite3</code> confirms Chroma defaults to <b>Squared L2 Norm (space='l2')</b>, NOT cosine distance.", table_cell),
            Paragraph("Vector retrieval computes Euclidean distance. Because nomic-embed-text generates normalized vectors, L2 distance is monotonically related to cosine distance, but explicit configuration is standard.", table_cell),
        ],
        [
            Paragraph("<b>(b) Page Metadata for DOCX & UI Indexing</b>", table_cell),
            Paragraph("In <code>ingestion_service.py:load_document()</code>, <code>Docx2txtLoader</code> returns <code>{'source': filename}</code> with <b>NO page metadata</b>. In <code>chat.py:59</code>, page is <code>None</code>. In <code>chat_interface.py:171</code>, <code>page_info</code> is omitted. For PDFs, <code>PyMuPDFLoader</code> produces 0-indexed pages; <code>chat.py</code> converts <code>page + 1</code>. <b>PDFs display 1-indexed pages; DOCX displays no page number</b>.", table_cell),
            Paragraph("Consistent user presentation: PDF sources show '📄 file.pdf • Page 4', while DOCX sources display solely '📄 notes.docx'.", table_cell),
        ],
        [
            Paragraph("<b>(c) Duplicate Upload Handling</b>", table_cell),
            Paragraph("In <code>documents.py</code>, raw files are overwritten via <code>open(..., 'wb')</code>. In <code>ingestion_service.py:91</code>, <code>vectorstore.add_documents()</code> generates <b>new random UUIDs</b> without pre-deleting existing chunks for that filename.", table_cell),
            Paragraph("<b>Uploading the same file twice duplicates chunks in ChromaDB</b>. Total chunk count doubles, wasting storage and causing MMR to evaluate identical redundant chunks.", table_cell),
        ],
        [
            Paragraph("<b>(d) Compatibility with .doc Files</b>", table_cell),
            Paragraph("While <code>.doc</code> is listed in <code>ALLOWED_EXTENSIONS</code>, <code>Docx2txtLoader</code> delegates to <code>docx2txt</code> which unzips OpenXML packages. Legacy binary Word 97-2003 OLE files fail with <code>zipfile.BadZipFile: File is not a zip file</code>.", table_cell),
            Paragraph("<b>Legacy binary .doc files DO NOT work</b>. They fail ingestion with an unhandled exception converted to HTTP 500. Only modern <code>.docx</code> works.", table_cell),
        ],
    ]
    t_audit = Table(audit_data, colWidths=[115, 219, 170])
    t_audit.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_audit)

    story.append(Spacer(1, 8))
    story.append(Paragraph("PART 2: ERROR & EDGE CASE MATRIX", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=8))

    err_data = [
        [Paragraph("Scenario / Edge Case", table_header), Paragraph("Trigger / Root Cause", table_header), Paragraph("Backend Behavior (Code Execution)", table_header), Paragraph("Frontend UI Presentation", table_header)],
        [
            Paragraph("<b>Ollama Offline</b>", table_cell),
            Paragraph("Daemon stopped (port 11434 unreachable).", table_cell),
            Paragraph("<code>/health</code> returns status='degraded'. In <code>/upload</code>, embedding fails (HTTP 500). In <code>/chat/</code>, catches <code>ConnectionError</code> (HTTP 503).", table_cell),
            Paragraph("Sidebar renders <code>🔴 Ollama</code> badge. Chat displays error: '❌ Ollama is not running. Run: ollama serve'.", table_cell),
        ],
        [
            Paragraph("<b>Model Not Pulled</b>", table_cell),
            Paragraph("Model tag missing in Ollama.", table_cell),
            Paragraph("Ollama returns 404. In <code>documents.py</code> or <code>chat.py</code>, uncaught exception becomes HTTP 500 with message.", table_cell),
            Paragraph("UI displays: '❌ Upload failed: model nomic-embed-text not found' or '❌ Error: Query failed: model not found'.", table_cell),
        ],
        [
            Paragraph("<b>Scanned Image PDF</b>", table_cell),
            Paragraph("PDF contains images of text without OCR layer.", table_cell),
            Paragraph("<code>load_document()</code> evaluates <code>total_chars < 50</code>, unlinks file, raises HTTP 422 Unprocessable Entity.", table_cell),
            Paragraph("UI shows: '❌ Upload failed: The file appears to be empty or is a scanned image PDF. Please use text-based PDF.'", table_cell),
        ],
        [
            Paragraph("<b>Empty Database</b>", table_cell),
            Paragraph("User queries before uploading documents.", table_cell),
            Paragraph("In <code>chat.py</code>, <code>get_collection_count() == 0</code> raises HTTP 400 Bad Request.", table_cell),
            Paragraph("UI renders warning: '⚠️ No documents found in the knowledge base. Please upload PDF or DOCX files first.'", table_cell),
        ],
        [
            Paragraph("<b>Oversized File (>50MB)</b>", table_cell),
            Paragraph("Uploaded file exceeds 50MB.", table_cell),
            Paragraph("In <code>documents.py</code>, byte check aborts prior to disk save with HTTP 413 Content Too Large.", table_cell),
            Paragraph("UI displays: '❌ Upload failed: File too large (XMB). Maximum allowed: 50MB'.", table_cell),
        ],
        [
            Paragraph("<b>Duplicate Upload</b>", table_cell),
            Paragraph("Same file uploaded a second time.", table_cell),
            Paragraph("Disk file overwritten. Chroma <code>add_documents()</code> creates new UUIDs, doubling chunks.", table_cell),
            Paragraph("UI displays success. Document list still shows 1 file, but sidebar chunk count increments.", table_cell),
        ],
        [
            Paragraph("<b>Legacy .doc Upload</b>", table_cell),
            Paragraph("Word 97-2003 binary file uploaded.", table_cell),
            Paragraph("<code>docx2txt</code> raises <code>zipfile.BadZipFile</code>. Caught by generic exception, returns HTTP 500.", table_cell),
            Paragraph("UI displays: '❌ Upload failed: Ingestion failed: File is not a zip file. Is Ollama running?'", table_cell),
        ],
        [
            Paragraph("<b>Inference Timeout</b>", table_cell),
            Paragraph("Slow local CPU generation exceeds 180s.", table_cell),
            Paragraph("Streamlit <code>httpx.post()</code> hits 180s timeout; ChatOllama has 120s timeout.", table_cell),
            Paragraph("UI displays: '⏱️ The response timed out. The model might be too slow. Try llama3.2.'", table_cell),
        ],
    ]
    t_err = Table(err_data, colWidths=[85, 110, 160, 149])
    t_err.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_err)

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # 3. COMPLETE ARCHITECTURE & FILE MAP
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("PART 3: FULL ARCHITECTURE & SYSTEM SCHEMATICS", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("3.1 Component & Module Breakdown", h2_style))
    comp_data = [
        [Paragraph("Module Path", table_header), Paragraph("Key Responsibilities", table_header), Paragraph("Inputs / Outputs", table_header), Paragraph("Dependencies", table_header)],
        [
            Paragraph("backend.core.config", table_cell),
            Paragraph("Loads .env via Pydantic BaseSettings. Auto-creates data directories.", table_cell),
            Paragraph("In: .env file<br/>Out: Settings singleton", table_cell),
            Paragraph("pydantic_settings, os", table_cell),
        ],
        [
            Paragraph("backend.models.schemas", table_cell),
            Paragraph("Defines request/response data contracts and validation boundaries.", table_cell),
            Paragraph("In: Raw JSON/Forms<br/>Out: Validated DTO objects", table_cell),
            Paragraph("pydantic", table_cell),
        ],
        [
            Paragraph("backend.services.ingestion_service", table_cell),
            Paragraph("Parses PDF/DOCX, splits text (800/150), calls Ollama embeddings, stores in Chroma.", table_cell),
            Paragraph("In: File path, filename<br/>Out: Created chunk count", table_cell),
            Paragraph("PyMuPDF, Docx2txt, RecursiveSplitter, Chroma, OllamaEmbeddings", table_cell),
        ],
        [
            Paragraph("backend.services.llm_service", table_cell),
            Paragraph("MMR retriever (k=4, fetch_k=15), injects context into TEACHING_PROMPT, invokes LLM.", table_cell),
            Paragraph("In: Question string, model<br/>Out: (Answer string, Source docs)", table_cell),
            Paragraph("ChatOllama, Chroma, LCEL runnables, StrOutputParser", table_cell),
        ],
        [
            Paragraph("backend.api.v1.endpoints.documents", table_cell),
            Paragraph("Endpoints: POST /upload (max 50MB), GET / (list files), DELETE /clear (reset DB).", table_cell),
            Paragraph("In: Multipart file, HTTP requests<br/>Out: Upload/List/Clear JSON", table_cell),
            Paragraph("FastAPI, ingestion_service", table_cell),
        ],
        [
            Paragraph("backend.api.v1.endpoints.chat", table_cell),
            Paragraph("Validates non-empty DB, runs RAG query, deduplicates citations by (source, page).", table_cell),
            Paragraph("In: ChatRequest JSON<br/>Out: ChatResponse JSON", table_cell),
            Paragraph("FastAPI, llm_service, ingestion_service", table_cell),
        ],
        [
            Paragraph("frontend.components.sidebar", table_cell),
            Paragraph("Renders model dropdown, file dropzone, doc list, health status, and danger zone.", table_cell),
            Paragraph("In: User UI clicks<br/>Out: HTTP calls to FastAPI", table_cell),
            Paragraph("Streamlit, HTTPX", table_cell),
        ],
        [
            Paragraph("frontend.components.chat_interface", table_cell),
            Paragraph("Renders chat history, user input, thinking spinners, and expandable source citations.", table_cell),
            Paragraph("In: Chat text input<br/>Out: Rendered markdown & state", table_cell),
            Paragraph("Streamlit, HTTPX", table_cell),
        ],
    ]
    t_comp = Table(comp_data, colWidths=[110, 160, 110, 124])
    t_comp.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_comp)

    story.append(Spacer(1, 6))
    story.append(Paragraph("3.2 Complete REST API Documentation", h2_style))
    api_data2 = [
        [Paragraph("Method & Endpoint", table_header), Paragraph("Request Format", table_header), Paragraph("Success Response", table_header), Paragraph("Error Codes", table_header), Paragraph("Handler Location", table_header)],
        [
            Paragraph("<b>GET</b> /health", table_cell),
            Paragraph("None", table_cell),
            Paragraph("HealthResponse (status, ollama_ok, doc_count)", table_cell),
            Paragraph("None ('degraded')", table_cell),
            Paragraph("backend/main.py", table_cell),
        ],
        [
            Paragraph("<b>POST</b> /api/v1/documents/upload", table_cell),
            Paragraph("multipart/form-data: <code>file</code> (PDF/DOCX)", table_cell),
            Paragraph("UploadResponse (chunks_created, success=true)", table_cell),
            Paragraph("400 (ext), 413 (size), 422 (scanned), 500", table_cell),
            Paragraph("backend/api/v1/endpoints/documents.py", table_cell),
        ],
        [
            Paragraph("<b>GET</b> /api/v1/documents/", table_cell),
            Paragraph("None", table_cell),
            Paragraph("DocumentsListResponse (array of DocumentInfo)", table_cell),
            Paragraph("500", table_cell),
            Paragraph("backend/api/v1/endpoints/documents.py", table_cell),
        ],
        [
            Paragraph("<b>DELETE</b> /api/v1/documents/clear", table_cell),
            Paragraph("None", table_cell),
            Paragraph("ClearResponse (files_deleted, success=true)", table_cell),
            Paragraph("500", table_cell),
            Paragraph("backend/api/v1/endpoints/documents.py", table_cell),
        ],
        [
            Paragraph("<b>POST</b> /api/v1/chat/", table_cell),
            Paragraph("JSON: <code>question</code>, <code>model</code>, <code>top_k</code>", table_cell),
            Paragraph("ChatResponse (answer, sources array, model_used)", table_cell),
            Paragraph("400 (empty DB), 503 (Ollama), 500", table_cell),
            Paragraph("backend/api/v1/endpoints/chat.py", table_cell),
        ],
    ]
    t_api2 = Table(api_data2, colWidths=[105, 100, 120, 85, 94])
    t_api2.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_api2)

    story.append(Spacer(1, 6))
    story.append(Paragraph("3.3 Quick Reference Mapping: Feature ➔ Files ➔ Endpoints / DB", h2_style))
    ref_data = [
        [Paragraph("Feature", table_header), Paragraph("Key Files Involved", table_header), Paragraph("Primary Functions / Classes", table_header), Paragraph("Bound Endpoint / DB Table", table_header)],
        [Paragraph("Document Upload", table_cell), Paragraph("sidebar.py, documents.py, ingestion_service.py", table_cell), Paragraph("_handle_upload(), upload_document(), ingest_document()", table_cell), Paragraph("POST /api/v1/documents/upload<br/>raw_documents/", table_cell)],
        [Paragraph("Text Chunking", table_cell), Paragraph("ingestion_service.py", table_cell), Paragraph("RecursiveCharacterTextSplitter.split_documents()", table_cell), Paragraph("In-memory transform", table_cell)],
        [Paragraph("Vector Indexing", table_cell), Paragraph("ingestion_service.py", table_cell), Paragraph("get_vectorstore(), vectorstore.add_documents()", table_cell), Paragraph("Chroma collection: teaching_materials (HNSW)", table_cell)],
        [Paragraph("RAG Q&A", table_cell), Paragraph("chat_interface.py, chat.py, llm_service.py", table_cell), Paragraph("handle_user_input(), chat(), query_rag()", table_cell), Paragraph("POST /api/v1/chat/", table_cell)],
        [Paragraph("MMR Retrieval", table_cell), Paragraph("llm_service.py", table_cell), Paragraph("get_retriever(), retriever.invoke()", table_cell), Paragraph("Chroma query (k=4, fetch_k=15)", table_cell)],
        [Paragraph("Citation Generation", table_cell), Paragraph("chat.py, chat_interface.py", table_cell), Paragraph("chat() deduplicator, _render_sources()", table_cell), Paragraph("SourceDocument DTO", table_cell)],
        [Paragraph("Clear Database", table_cell), Paragraph("sidebar.py, documents.py, ingestion_service.py", table_cell), Paragraph("clear_all(), clear_all_documents()", table_cell), Paragraph("DELETE /api/v1/documents/clear", table_cell)],
        [Paragraph("System Health", table_cell), Paragraph("sidebar.py, main.py", table_cell), Paragraph("_render_health_status(), health_check()", table_cell), Paragraph("GET /health", table_cell)],
    ]
    t_ref = Table(ref_data, colWidths=[90, 140, 150, 124])
    t_ref.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    story.append(t_ref)

    story.append(PageBreak())

    # ═══════════════════════════════════════════════════════════════════════════
    # 4. LIMITATIONS, TECHNICAL DEBT & ROADMAP
    # ═══════════════════════════════════════════════════════════════════════════
    story.append(Paragraph("PART 4: LIMITATIONS, TECHNICAL DEBT & ROADMAP", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("4.1 Architectural Limitations & Technical Debt", h2_style))
    story.append(Paragraph("• <b>Single-Tenant Architecture:</b> Zero authentication, authorization, or user isolation. All users access and mutate the same vector collection.", bullet_style))
    story.append(Paragraph("• <b>Synchronous Ingestion Blocking:</b> Document loading and vector generation execute synchronously inside the FastAPI threadpool. Ingesting large 200-page textbooks blocks worker resources.", bullet_style))
    story.append(Paragraph("• <b>Duplicate Upload Inefficiency:</b> Uploading an identical document creates duplicate chunks in ChromaDB without idempotency checks.", bullet_style))
    story.append(Paragraph("• <b>Non-Streaming Chat Latency:</b> LLM responses are returned as a single block after full completion. Users experience 10-30 seconds of perceived latency on CPU hardware.", bullet_style))
    story.append(Paragraph("• <b>Memory-Bound Session State:</b> Chat history resides entirely in Streamlit RAM (<code>st.session_state</code>). Refreshing the browser tab permanently clears conversation history.", bullet_style))
    story.append(Paragraph("• <b>Inaccurate .doc Support:</b> Code accepts <code>.doc</code> in allowlists but underlying <code>Docx2txtLoader</code> crashes on legacy binary Word files.", bullet_style))
    story.append(Paragraph("• <b>Unverified Hardware Scenarios:</b> Performance on external dedicated GPUs, encrypted PDFs, or multi-user concurrent loads has <i>Not been verified</i>.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("4.2 Prioritized Improvement Roadmap", h2_style))
    roadmap_data = [
        [Paragraph("Priority", table_header), Paragraph("Milestone / Initiative", table_header), Paragraph("Technical Implementation Details", table_header)],
        [
            Paragraph("<b>P0 (Immediate)</b>", table_cell),
            Paragraph("Ingestion Idempotency & Duplicate Purge", table_cell),
            Paragraph("Invoke <code>delete_document_chunks(filename)</code> prior to <code>add_documents()</code>. Prevents duplicate chunks in ChromaDB upon re-uploading.", table_cell),
        ],
        [
            Paragraph("<b>P0 (Immediate)</b>", table_cell),
            Paragraph("Fix .doc Extension Handling", table_cell),
            Paragraph("Remove <code>.doc</code> from allowlists or integrate <code>antiword</code>/<code>catdoc</code>. Display clear error that only OpenXML <code>.docx</code> is supported.", table_cell),
        ],
        [
            Paragraph("<b>P1 (Near-Term)</b>", table_cell),
            Paragraph("Streaming Token Responses", table_cell),
            Paragraph("Implement Server-Sent Events (SSE) or WebSockets in FastAPI using LangChain <code>chain.astream()</code> to stream tokens directly into Streamlit.", table_cell),
        ],
        [
            Paragraph("<b>P1 (Near-Term)</b>", table_cell),
            Paragraph("Persistent Chat History", table_cell),
            Paragraph("Add SQLite or DuckDB conversational memory table to preserve user chat threads across browser reloads.", table_cell),
        ],
        [
            Paragraph("<b>P2 (Production)</b>", table_cell),
            Paragraph("Background Task Worker (Celery / RQ)", table_cell),
            Paragraph("Offload heavy document ingestion to background task workers with Redis, returning a task ID and polling status bar.", table_cell),
        ],
        [
            Paragraph("<b>P2 (Production)</b>", table_cell),
            Paragraph("Multi-Tenancy & JWT Auth", table_cell),
            Paragraph("Implement OAuth2/JWT authentication and isolate vector collections per user ID or course ID.", table_cell),
        ],
    ]
    t_road = Table(roadmap_data, colWidths=[80, 150, 274])
    t_road.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("BOX", (0, 0), (-1, -1), 1, BORDER_COLOR),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(t_road)

    story.append(Spacer(1, 8))
    story.append(Paragraph("4.3 Technical Glossary", h2_style))
    story.append(Paragraph("• <b>RAG (Retrieval-Augmented Generation):</b> Combining information retrieval with text synthesis to ground LLMs in external knowledge.", bullet_style))
    story.append(Paragraph("• <b>LCEL (LangChain Expression Language):</b> Declarative composition syntax for chaining prompts, models, and parsers (e.g. <code>prompt | llm | parser</code>).", bullet_style))
    story.append(Paragraph("• <b>MMR (Maximal Marginal Relevance):</b> A retrieval algorithm balancing relevance to the query with diversity among retrieved items.", bullet_style))
    story.append(Paragraph("• <b>Bi-Encoder:</b> A transformer model (e.g. nomic-embed-text) encoding queries and documents independently into vector space.", bullet_style))
    story.append(Paragraph("• <b>HNSW (Hierarchical Navigable Small World):</b> A multi-layer graph-based indexing algorithm for ultra-fast approximate nearest neighbor search.", bullet_style))
    story.append(Paragraph("• <b>GGUF / Quantization:</b> Compression format converting 16-bit model weights to 4-bit (Q4_K_M) for high-speed local inference.", bullet_style))

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Master PDF successfully generated at: {filename}")


if __name__ == "__main__":
    output_pdf = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "AI_Teaching_Assistant_Documentation.pdf"
    )
    build_pdf(output_pdf)
