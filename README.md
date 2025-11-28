# Tri‑Tender Core MCP

This is the **core FastMCP server** for the Tri‑Tender ecosystem.

It exposes a small, production‑ready set of tools that your LLM
(ChatGPT / Dyad / custom agent) can call when a user uploads
tender‑related documents.

## Tools exposed

- `detect_document(file)`  
  Light‑weight classifier that returns a label like `tender`,
  `pricing_schedule`, `scope_of_work`, `terms_and_conditions`,
  `evaluation_criteria`, `compliance_document`, `brand_asset` or
  `unknown`.

- `extract_tender_metadata(file)`  
  Extracts high‑level tender metadata (title, reference number,
  buyer, closing date, summary, detected sections).

- `pricing_engine(file, user_inputs)`  
  Reads XLS/XLSX/CSV pricing schedules and returns a structured
  JSON payload with column names, rows, and computed totals
  (with optional mark‑up).

- `detect_brand(file)`  
  Infers a very simple brand palette from an uploaded logo image
  (PNG/JPG) or falls back to filename‑based heuristics.

- `compile_output(documents, brand, pricing)`  
  Compiles the final tender response into a **single HTML** document
  that can be converted to PDF. It uses brand colours and embeds
  a parsed pricing table when provided.

---

## Local development

```bash
git clone <your-repo-url>
cd tri_tender_core_mcp

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

Then run the MCP server locally:

```bash
python server.py
```

Depending on your FastMCP tooling, you can now point your MCP host
at this server (usually `http://localhost:8000` or similar, depending
on how you launch it). See the FastMCP docs for exact instructions.

---

## FastMCP Cloud deployment

1. Zip this folder (so that `server.py` is at the root of the ZIP).
2. Go to your **FastMCP Cloud** dashboard.
3. Create a new **Python MCP server**.
4. Upload the ZIP and deploy.
5. Once deployed, FastMCP Cloud will give you:
   - An MCP endpoint URL
   - An API key
   - A test console to run tools

Use those values inside Tri‑Tender / Dyad, for example:

```yaml
mcpServers:
  tri_tender_core_mcp:
    url: "https://api.fastmcp.com/your-server-id"
    apiKey: "YOUR-KEY"
```

---

## GitHub usage

This folder is already structured as a clean repository:

```bash
cd tri_tender_core_mcp
git init
git add .
git commit -m "Initial Tri-Tender core MCP"
git remote add origin git@github.com:<you>/tri_tender_core_mcp.git
git push -u origin main
```

---

## Next steps / extensions

- Add more advanced NLP‑based metadata extraction.
- Extend `pricing_engine` with tender‑specific pricing rules.
- Integrate risk scoring and compliance checks.
- Wire this MCP together with:
  - Tri‑Tender Brand MCP
  - Tri‑Tender Pricing MCP
  - Tri‑Tender Orchestrator MCP
  - Tri‑Tender Compiler MCP

This repo is intentionally **simple, readable and production‑safe**
so you can evolve it as Tri‑Tender grows.
"# tri-tender-core-mcp" 
