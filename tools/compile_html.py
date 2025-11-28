from typing import List, Dict, Any


BASE_CSS = """
body {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    margin: 0;
    padding: 0;
    background: #f5f5f7;
    color: #111827;
}
.page {
    max-width: 960px;
    margin: 24px auto;
    background: #ffffff;
    padding: 32px 40px;
    border-radius: 16px;
    box-shadow: 0 18px 45px rgba(15, 23, 42, 0.12);
}
h1, h2, h3, h4 {
    margin-top: 0;
}
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 32px;
}
.brand-name {
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: 0.04em;
}
.badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    background: rgba(15, 23, 42, 0.04);
}
.section {
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 1px solid #e5e7eb;
}
.section:last-of-type {
    border-bottom: none;
    padding-bottom: 0;
}
.section h2 {
    font-size: 1.25rem;
    margin-bottom: 12px;
}
.meta-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px 24px;
    margin-top: 12px;
    font-size: 0.9rem;
}
.meta-label {
    color: #6b7280;
    font-weight: 500;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.meta-value {
    font-weight: 600;
    color: #111827;
}
table.pricing {
    border-collapse: collapse;
    width: 100%;
    margin-top: 12px;
    font-size: 0.9rem;
}
table.pricing th,
table.pricing td {
    border: 1px solid #e5e7eb;
    padding: 8px 10px;
    text-align: left;
}
table.pricing th {
    background: #f9fafb;
    font-weight: 600;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.pricing-total {
    margin-top: 12px;
    text-align: right;
    font-weight: 700;
}
.footer {
    margin-top: 32px;
    font-size: 0.8rem;
    color: #9ca3af;
    text-align: center;
}
"""


def compile_html(documents: List[Any], brand: Dict[str, Any], pricing: Dict[str, Any]) -> str:
    """
    Combine tender content, brand styling and pricing info into a single
    clean HTML document that can be converted to PDF.

    `documents` can be:
    - a list of raw HTML strings, or
    - a list of dicts with keys {"title", "html"}.
    """
    primary = brand.get("primary_color", "#003366")
    secondary = brand.get("secondary_color", "#f5f5f5")
    accent = brand.get("accent_color", "#ffcc00")
    brand_name = brand.get("brand_name", "Tri-Tender Client")

    # Normalise documents
    normalised_sections = []
    for idx, doc in enumerate(documents):
        if isinstance(doc, str):
            normalised_sections.append(
                {
                    "title": "Section %d" % (idx + 1,),
                    "html": doc,
                }
            )
        elif isinstance(doc, dict):
            normalised_sections.append(
                {
                    "title": doc.get("title", "Section %d" % (idx + 1,)),
                    "html": doc.get("html", ""),
                }
            )

    pricing_html = ""
    if pricing and pricing.get("ok"):
        cols = pricing.get("column_names") or []
        items = pricing.get("items") or []
        currency = pricing.get("currency", "")
        grand = pricing.get("grand_total")
        grand_mu = pricing.get("grand_total_with_mark_up")

        header_cols = "".join("<th>%s</th>" % (c,) for c in cols)
        rows_html = []
        for item in items:
            raw = item.get("raw", {})
            cells = []
            for c in cols:
                val = raw.get(c)
                cells.append("<td>%s</td>" % ("" if val is None else val,))
            rows_html.append("<tr>%s</tr>" % ("".join(cells),))

        pricing_html = """
        <div class=\"section\">
          <h2>Pricing Schedule (Parsed)</h2>
          <table class=\"pricing\">
            <thead><tr>%s</tr></thead>
            <tbody>
              %s
            </tbody>
          </table>
          <div class=\"pricing-total\">
            Grand Total: %s %s <br/>
            Grand Total (with mark-up): %s %s
          </div>
        </div>
        """ % (header_cols, "".join(rows_html), currency, grand, currency, grand_mu)

    sections_html = []
    for sec in normalised_sections:
        sections_html.append(
            """
            <div class=\"section\">
              <h2>%s</h2>
              <div>%s</div>
            </div>
            """ % (sec["title"], sec["html"])
        )

    html = """<!DOCTYPE html>
    <html lang=\"en\">
    <head>
      <meta charset=\"utf-8\">
      <title>Tender Proposal – %s</title>
      <style>
      %s

      .page {
        border-top: 6px solid %s;
      }
      .badge {
        background: %s;
        color: %s;
      }
      a {
        color: %s;
      }
      mark {
        background: %s33;
        color: %s;
      }
      </style>
    </head>
    <body>
      <div class=\"page\">
        <header class=\"header\">
          <div>
            <div class=\"brand-name\">%s</div>
            <div class=\"badge\">Tri-Tender | AI-Assisted Tender Response</div>
          </div>
        </header>

        %s

        %s

        <div class=\"footer\">
          Generated via Tri-Tender Core MCP. This HTML is print-ready and can be converted to PDF.
        </div>
      </div>
    </body>
    </html>
    """ % (
        brand_name,
        BASE_CSS,
        primary,
        secondary,
        primary,
        primary,
        accent,
        primary,
        brand_name,
        "".join(sections_html),
        pricing_html,
    )
    return html
