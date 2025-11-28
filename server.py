from fastmcp import FastMCP, tool, Resource

from tools.extract_metadata import extract_metadata
from tools.classify_document import classify_document
from tools.parse_pricing import parse_pricing
from tools.brand_infer import infer_brand
from tools.compile_html import compile_html


mcp = FastMCP("tri_tender_core_mcp")


@tool
def detect_document(file: Resource) -> str:
    """
    Identify the type of tender-related document.

    Returns a short label like:
    - "tender"
    - "pricing_schedule"
    - "scope_of_work"
    - "terms_and_conditions"
    - "evaluation_criteria"
    - "compliance_document"
    - "unknown"
    """
    return classify_document(file.path)


@tool
def extract_tender_metadata(file: Resource) -> dict:
    """
    Extract core tender metadata from the uploaded document.

    Expected keys (when they can be found):
    - title
    - reference_number
    - buyer
    - closing_date
    - summary
    - raw_text_excerpt
    - detected_sections (list of {{name, snippet}})
    """
    return extract_metadata(file.path)


@tool
def pricing_engine(file: Resource, user_inputs: dict | None = None) -> dict:
    """
    Parse a pricing schedule (XLS/XLSX/CSV) and return a structured pricing model.

    user_inputs can include:
    - currency (e.g. "ZAR")
    - default_mark_up (e.g. 0.25)
    - rounding (e.g. 2)
    """
    if user_inputs is None:
        user_inputs = {}
    return parse_pricing(file.path, user_inputs)


@tool
def detect_brand(file: Resource) -> dict:
    """
    Infer basic brand styling from a logo or a tender PDF.

    Returns:
    - brand_name
    - primary_color
    - secondary_color
    - accent_color
    - palette (list of hex)
    - notes
    """
    return infer_brand(file.path)


@tool
def compile_output(documents: list, brand: dict | None = None, pricing: dict | None = None) -> str:
    """
    Compile the final tender response into a single HTML string.

    documents: list of strings or dicts with {{"title", "html"}}.
    brand: output from detect_brand()
    pricing: output from pricing_engine()
    """
    return compile_html(documents, brand or {}, pricing or {})


if __name__ == "__main__":
    # Local dev entry point
    mcp.run()
