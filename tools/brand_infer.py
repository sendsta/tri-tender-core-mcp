import os
from typing import Dict, Any, List

from PIL import Image


def _extract_palette_from_image(path: str, max_colors: int = 5) -> List[str]:
    """
    Rough dominant color extraction. Returns a list of HEX strings.

    This is deliberately simple and deterministic. It can be replaced
    later with a more sophisticated brand-color extractor.
    """
    img = Image.open(path).convert("RGB")
    # resize for speed
    img = img.resize((128, 128))
    result = img.getcolors(128 * 128)
    if not result:
        return []

    # sort by frequency descending
    result.sort(key=lambda x: x[0], reverse=True)
    palette = []
    for count, rgb in result[:max_colors]:
        r, g, b = rgb
        palette.append("#%02x%02x%02x" % (r, g, b))
    return palette


def infer_brand(path: str) -> Dict[str, Any]:
    """
    Infer basic brand styling from an uploaded file.

    If the file is an image (logo), we attempt to detect a simple color palette.
    For all other types, we fall back to filename-based heuristics.
    """
    file_name = os.path.basename(path)
    name_root, ext = os.path.splitext(file_name)
    ext = ext.lower()

    palette = []  # type: List[str]
    notes = []  # type: List[str]

    if ext in {".png", ".jpg", ".jpeg"}:
        try:
            palette = _extract_palette_from_image(path)
            notes.append("Palette extracted from image logo.")
        except Exception as exc:
            notes.append("Failed to analyse image for palette: %s" % (exc,))
    else:
        notes.append("Non-image file; brand colours inferred only from filename.")

    # Heuristic brand name
    brand_name = name_root.replace("_", " ").replace("-", " ").title()

    primary = palette[0] if palette else "#003366"  # deep blue default
    secondary = palette[1] if len(palette) > 1 else "#f5f5f5"
    accent = palette[2] if len(palette) > 2 else "#ffcc00"

    return {
        "file_name": file_name,
        "brand_name": brand_name or "Tri-Tender Client",
        "primary_color": primary,
        "secondary_color": secondary,
        "accent_color": accent,
        "palette": palette or [primary, secondary, accent],
        "notes": notes,
    }
