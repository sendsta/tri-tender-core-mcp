import os
from typing import Dict, Any

import pandas as pd


def _load_table(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext in {".xls", ".xlsx"}:
        # Load first sheet by default
        return pd.read_excel(path)
    if ext in {".csv"}:
        return pd.read_csv(path)
    # Fallback: try excel anyway
    return pd.read_excel(path)


def parse_pricing(path: str, user_inputs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Read a pricing schedule and surface it as a structured JSON payload
    that an LLM can reason about.

    The goal is to be predictable rather than clever:
    - We do not guess too much.
    - We expose column names and raw values.
    """
    currency = user_inputs.get("currency", "ZAR")
    default_mark_up = float(user_inputs.get("default_mark_up", 0.0))
    rounding = int(user_inputs.get("rounding", 2))

    try:
        df = _load_table(path)
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Failed to read pricing file: {exc}",
            "items": [],
        }

    # Normalise column names
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    # Try to identify key columns
    desc_col = next((c for c in df.columns if "description" in c.lower()), None)
    qty_col = next((c for c in df.columns if "qty" in c.lower() or "quantity" in c.lower()), None)
    rate_col = next((c for c in df.columns if "rate" in c.lower() or "unit price" in c.lower()), None)
    total_col = next((c for c in df.columns if "total" in c.lower()), None)

    items = []
    for idx, row in df.iterrows():
        # Skip fully blank rows
        if row.isna().all():
            continue

        item = {
            "row_index": int(idx),
            "raw": {col: (None if pd.isna(val) else val) for col, val in row.items()},
        }

        if desc_col:
            item["description"] = row.get(desc_col)
        if qty_col:
            try:
                item["quantity"] = float(row.get(qty_col))
            except Exception:
                item["quantity"] = row.get(qty_col)
        if rate_col:
            try:
                item["unit_rate"] = float(row.get(rate_col))
            except Exception:
                item["unit_rate"] = row.get(rate_col)

        # Compute total if possible
        total_value = None
        try:
            if total_col and not pd.isna(row.get(total_col)):
                total_value = float(row.get(total_col))
            elif qty_col and rate_col and not pd.isna(row.get(qty_col)) and not pd.isna(row.get(rate_col)):
                total_value = float(row.get(qty_col)) * float(row.get(rate_col))
        except Exception:
            total_value = None

        if total_value is not None:
            item["total"] = round(total_value, rounding)

            if default_mark_up:
                marked_up = total_value * (1.0 + default_mark_up)
                item["total_with_mark_up"] = round(marked_up, rounding)

        items.append(item)

    grand_total = round(
        sum(float(i.get("total", 0) or 0) for i in items),
        rounding,
    )
    grand_total_with_mark_up = round(
        sum(float(i.get("total_with_mark_up", i.get("total", 0) or 0)) for i in items),
        rounding,
    )

    return {
        "ok": True,
        "currency": currency,
        "rounding": rounding,
        "default_mark_up": default_mark_up,
        "column_names": list(df.columns),
        "item_count": len(items),
        "grand_total": grand_total,
        "grand_total_with_mark_up": grand_total_with_mark_up,
        "items": items,
    }
