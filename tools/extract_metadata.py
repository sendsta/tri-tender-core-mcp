import os
import re
from typing import Dict, Any

from pypdf import PdfReader
from docx import Document as DocxDocument


def _read_text_from_pdf(path: str, max_pages: int = 3) -> str:
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages[:max_pages]):
        try:
            pages.append(page.extract_text() or "")
        except Exception:
            continue
    return "\n".join(pages)


def _read_text_from_docx(path: str) -> str:
    doc = DocxDocument(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())


def _read_text_fallback(path: str, max_bytes: int = 16384) -> str:
    with open(path, "rb") as f:
        raw = f.read(max_bytes)
    return raw.decode(errors="ignore")


def _extract_field(patterns, text, max_len: int = 200) -> str | None:
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            value = m.group(1).strip()
            return value[:max_len]
    return None


def extract_metadata(path: str) -> Dict[str, Any]:
    """
    Extract high‑level tender metadata using regex heuristics.

    This is intentionally conservative and safe for production use,
    and can be refined later with more advanced NLP or custom rules.
    """
    ext = os.path.splitext(path)[1].lower()

    if ext == ".pdf":
        text = _read_text_from_pdf(path)
    elif ext in {".docx"}:
        text = _read_text_from_docx(path)
    else:
        text = _read_text_fallback(path)

    # Normalise internal whitespace for simpler regex
    normalised = re.sub(r"[ \t]+", " ", text)
    normalised = re.sub(r"\n+", "\n", normalised)

    title = _extract_field(
        [
            r"(?:tender|bid|rfq|rfb)\s*title[:\-]\s*(.+)",
            r"(?:invitation to bid|invitation to tender)\s*(.+)",
        ],
        normalised,
    )

    reference_number = _extract_field(
        [
            r"(?:tender|bid|rfq|reference)\s*(?:no\.|number|ref)[:\-]\s*(.+)",
            r"(?:tender|bid)\s*no\.?:\s*([A-Za-z0-9/\-]+)",
        ],
        normalised,
        max_len=80,
    )

    buyer = _extract_field(
        [
            r"(?:issued by|procuring entity|employer|purchaser)[:\-]\s*(.+)",
            r"(?:department|entity|organisation|organization)[:\-]\s*(.+)",
        ],
        normalised,
    )

    closing_date = _extract_field(
        [
            r"(?:closing date|closing time)[:\-]\s*([0-9]{1,2}[/\-][0-9]{1,2}[/\-][0-9]{2,4})",
            r"(?:closing date|closing time)[:\-]\s*([0-9]{1,2} \w+ 20[0-9]{2})",
        ],
        normalised,
        max_len=40,
    )

    # crude summary = first 5–8 lines
    lines = [ln.strip() for ln in normalised.split("\n") if ln.strip()]
    summary = " ".join(lines[:8])[:1200]

    # detect sections by simple headings
    section_patterns = [
        ("scope_of_work", r"scope of work|scope of services|scope"),
        ("evaluation_criteria", r"evaluation criteria|evaluation process|scoring"),
        ("pricing", r"pricing schedule|bill of quantities|boq"),
        ("conditions", r"terms and conditions|conditions of bid|conditions of contract"),
    ]
    detected_sections = []
    lower_text = normalised.lower()
    for name, pat in section_patterns:
        m = re.search(pat, lower_text)
        if m:
            idx = m.start()
            snippet = normalised[max(0, idx - 200): idx + 300]
            detected_sections.append(
                {
                    "name": name,
                    "snippet": snippet.strip()[:600],
                }
            )

    return {
        "file_name": os.path.basename(path),
        "title": title,
        "reference_number": reference_number,
        "buyer": buyer,
        "closing_date": closing_date,
        "summary": summary,
        "raw_text_excerpt": normalised[:4000],
        "detected_sections": detected_sections,
    }
