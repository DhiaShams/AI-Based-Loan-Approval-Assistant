"""
Loads the custom icon set from the top-level `icons/` folder and exposes
them as base64 data URIs. We embed icons as data URIs (rather than
pointing <img> tags at a file path) so they render reliably inside our
custom HTML components regardless of how/where Streamlit is being served -
no static-file-serving configuration required.
"""

import base64
from pathlib import Path

import streamlit as st

ICONS_DIR = Path(__file__).resolve().parent.parent / "icons"


@st.cache_data
def icon_data_uri(name: str) -> str:
    """Base64 data URI for icons/{name}.png."""
    path = ICONS_DIR / f"{name}.png"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def icon_img(name: str, size: int = 18, alt: str = "", css_class: str = "") -> str:
    """<img> tag snippet for icons/{name}.png, ready to drop into any
    HTML string rendered via render_html()."""
    cls = f' class="{css_class}"' if css_class else ""
    return (
        f'<img src="{icon_data_uri(name)}" width="{size}" height="{size}" '
        f'alt="{alt}"{cls} style="display:block; flex-shrink:0;" />'
    )
