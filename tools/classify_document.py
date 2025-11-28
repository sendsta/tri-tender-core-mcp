import os
import mimetypes


KEYWORDS_MAP = {
    "pricing_schedule": ["pricing schedule", "bill of quantities", "boq", "pricing", "rate", "unit price"],
    "scope_of_work": ["scope of work", "specification", "technical specification", "deliverables"],
    "terms_and_conditions": ["terms and conditions", "conditions of contract", "general conditions"],
    "evaluation_criteria": ["evaluation criteria", "functionality", "weighting", "points"],
    "compliance_document": ["tax clearance", "bee certificate", "b-bbee", "company registration", "id copy"],
    "tender": ["request for bid", "rfb", "rfq", "tender number", "bid number", "invitation to bid"],
}


def _guess_from_filename(path: str) -> str | None:
    name = os.path.basename(path).lower()
    if any(x in name for x in ["pricing", "boq", "bill_of_quantities"]):
        return "pricing_schedule"
    if "scope" in name or "sow" in name:
        return "scope_of_work"
    if "terms" in name or "conditions" in name:
        return "terms_and_conditions"
    if "eval" in name:
        return "evaluation_criteria"
    if any(x in name for x in ["compliance", "bee", "bbb", "tax", "cidb"]):
        return "compliance_document"
    if any(x in name for x in ["rfq", "rfb", "tender", "bid"]):
        return "tender"
    return None


def classify_document(path: str) -> str:
    """
    Very light‑weight heuristic classifier for tender documents.

    Uses filename, mime type and a small keyword scan on the first 4 KB.
    """
    # 1) filename hints
    guess = _guess_from_filename(path)
    if guess:
        return guess

    # 2) mime type
    mime, _ = mimetypes.guess_type(path)
    if mime and mime.startswith("image/"):
        # likely logo or brand asset
        return "brand_asset"

    # 3) content keywords (first few KB as text)
    try:
        with open(path, "rb") as f:
            head = f.read(4096).decode(errors="ignore").lower()
    except Exception:
        head = ""

    for label, keywords in KEYWORDS_MAP.items():
        if any(k in head for k in keywords):
            return label

    return "unknown"
