"""
Agent 1 — Document Parser
Extracts clean text + metadata from PDF, DOCX, or plain-text files.
"""
import io
import re
from typing import Tuple, Dict, Any


def parse_document(file_bytes: bytes, filename: str) -> Tuple[str, Dict[str, Any]]:
    """Return (raw_text, metadata_dict)."""
    ext = filename.lower().split(".")[-1]
    metadata: Dict[str, Any] = {"filename": filename, "file_type": ext, "pages": 0, "word_count": 0}

    if ext == "pdf":
        text, pages = _parse_pdf(file_bytes)
        metadata["pages"] = pages
    elif ext in ("docx", "doc"):
        text = _parse_docx(file_bytes)
        metadata["pages"] = max(1, len(text) // 3000)
    else:
        text = file_bytes.decode("utf-8", errors="ignore")
        metadata["pages"] = max(1, len(text) // 3000)

    text = _clean_text(text)
    metadata["word_count"] = len(text.split())
    metadata["char_count"] = len(text)
    return text, metadata


def _parse_pdf(file_bytes: bytes) -> Tuple[str, int]:
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages = doc.page_count
        chunks = []
        for page in doc:
            chunks.append(page.get_text("text"))
        return "\n".join(chunks), pages
    except Exception:
        pass

    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = len(pdf.pages)
            chunks = [p.extract_text() or "" for p in pdf.pages]
        return "\n".join(chunks), pages
    except Exception as e:
        return f"[PDF parse error: {e}]", 0


def _parse_docx(file_bytes: bytes) -> str:
    from docx import Document
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def _clean_text(text: str) -> str:
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]{2,}', ' ', text)
    text = re.sub(r'\f', '\n\n', text)          # form-feed → double newline
    return text.strip()
