"""
Background Removal & Replacement Web App
=========================================
Streamlit app with robust import error handling.
Run: streamlit run app.py
"""

import io
import sys
import importlib
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  — must be the FIRST streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BG Remover & Replacer",
    page_icon="✂️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# SAFE IMPORT — show a clear error in browser instead of black screen
# ─────────────────────────────────────────────────────────────────────────────
IMPORT_ERRORS = []

def try_import(module_name: str):
    try:
        return importlib.import_module(module_name)
    except Exception as e:
        IMPORT_ERRORS.append(f"❌ `{module_name}` — {e}")
        return None

np_mod    = try_import("numpy")
PIL_mod   = try_import("PIL")
rembg_mod = try_import("rembg")

if IMPORT_ERRORS:
    st.error("### 🚨 Import Error — App cannot start")
    st.markdown("Beberapa library gagal di-import. Jalankan perintah berikut di terminal:\n")
    st.code("pip install -r requirements.txt", language="bash")
    st.markdown("**Detail error:**")
    for err in IMPORT_ERRORS:
        st.markdown(f"- {err}")
    st.markdown(f"**Python version:** `{sys.version}`")
    st.markdown("**Pastikan menggunakan Python 3.10–3.12 dan virtual environment yang aktif.**")
    st.stop()

# Safe to import now
import numpy as np
from PIL import Image
from rembg import remove

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&display=swap');

html, body, [data-testid="stAppViewContainer"] {
    background: #0d0d0d;
    color: #e8e2d9;
    font-family: 'DM Mono', monospace;
}
[data-testid="stHeader"] { background: transparent; }

.hero-title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: clamp(2.4rem, 5vw, 4.2rem);
    font-style: italic;
    line-height: 1.05;
    letter-spacing: -0.02em;
    color: #f0ebe2;
    margin: 0;
}
.hero-subtitle {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #6b6560;
    margin-top: 0.6rem;
}
.hero-accent { color: #c8ff00; }
.rule { border: none; border-top: 1px solid #2a2a2a; margin: 2rem 0; }

[data-testid="stFileUploader"] {
    background: #161616;
    border: 1px solid #2a2a2a;
    border-radius: 4px;
    padding: 1rem 1.2rem;
    transition: border-color .2s;
}
[data-testid="stFileUploader"]:hover { border-color: #c8ff00; }

.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #c8ff00;
    margin-bottom: 0.4rem;
}
.img-panel {
    background: #111;
    border: 1px solid #232323;
    border-radius: 4px;
    padding: 1rem;
    text-align: center;
}
.img-caption {
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #555;
    margin-top: 0.6rem;
}

[data-testid="stButton"] > button {
    background: #c8ff00 !important;
    color: #0d0d0d !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 2px !important;
    padding: 0.65rem 2rem !important;
    transition: opacity .15s !important;
}
[data-testid="stButton"] > button:hover { opacity: 0.85 !important; }

[data-testid="stDownloadButton"] > button {
    background: transparent !important;
    color: #c8ff00 !important;
    border: 1px solid #c8ff00 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    border-radius: 2px !important;
    padding: 0.55rem 1.6rem !important;
    transition: background .15s, color .15s !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: #c8ff00 !important;
    color: #0d0d0d !important;
}

[data-testid="stAlert"] {
    background: #161616 !important;
    border-left: 3px solid #c8ff00 !important;
    color: #e8e2d9 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
    border-radius: 2px !important;
}

#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PROCESSING FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def load_image(uploaded_file) -> Image.Image:
    """Read an uploaded file and return a PIL Image."""
    uploaded_file.seek(0)
    raw_bytes = uploaded_file.read()
    return Image.open(io.BytesIO(raw_bytes))


def remove_background(image: Image.Image) -> Image.Image:
    """Remove background using rembg. Returns RGBA image."""
    rgb_image = image.convert("RGB")
    result = remove(rgb_image)
    if result.mode != "RGBA":
        result = result.convert("RGBA")
    return result


def resize_background(background: Image.Image, target_size: tuple) -> Image.Image:
    """Resize background to match foreground dimensions (width, height)."""
    resized = background.resize(target_size, Image.LANCZOS)
    return resized.convert("RGBA")


def composite_images(foreground_rgba: Image.Image, background_rgba: Image.Image) -> Image.Image:
    """Alpha-composite foreground onto background. Both must be RGBA and same size."""
    composite = Image.alpha_composite(background_rgba, foreground_rgba)
    return composite.convert("RGB")


def image_to_bytes(image: Image.Image, fmt: str = "PNG") -> bytes:
    """Encode a PIL Image to bytes."""
    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    return buffer.getvalue()


def run_pipeline(fg_file, bg_file):
    """Full pipeline: load → remove BG → resize BG → composite → return."""
    original_fg = load_image(fg_file).convert("RGB")
    background  = load_image(bg_file)

    removed_bg      = remove_background(original_fg)
    background_rgba = resize_background(background, original_fg.size)
    final_result    = composite_images(removed_bg, background_rgba)

    return original_fg, removed_bg, final_result


# ─────────────────────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────────────────────

def render_image_panel(image, caption: str):
    st.markdown("<div class='img-panel'>", unsafe_allow_html=True)
    st.image(image, use_container_width=True)
    st.markdown(f"<p class='img-caption'>{caption}</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def main():
    # Header
    st.markdown("""
        <h1 class="hero-title">
            Cut&nbsp;<span class="hero-accent">&amp;</span>&nbsp;Replace
        </h1>
        <p class="hero-subtitle">Automatic background removal &amp; replacement</p>
    """, unsafe_allow_html=True)
    st.markdown("<hr class='rule'>", unsafe_allow_html=True)

    # Upload section
    col_fg, col_bg = st.columns(2, gap="large")
    with col_fg:
        st.markdown("<p class='section-label'>01 — Subject image</p>", unsafe_allow_html=True)
        fg_file = st.file_uploader(
            "Foreground", type=["png", "jpg", "jpeg", "webp"],
            key="fg", label_visibility="collapsed"
        )
    with col_bg:
        st.markdown("<p class='section-label'>02 — Replacement background</p>", unsafe_allow_html=True)
        bg_file = st.file_uploader(
            "Background", type=["png", "jpg", "jpeg", "webp"],
            key="bg", label_visibility="collapsed"
        )

    st.markdown("<hr class='rule'>", unsafe_allow_html=True)

    # Process button
    _, btn_col, _ = st.columns([2, 1, 2])
    with btn_col:
        process_clicked = st.button("✂  Process image", use_container_width=True)

    if process_clicked:
        if not fg_file:
            st.warning("Upload gambar subject (foreground) terlebih dahulu.")
            return
        if not bg_file:
            st.warning("Upload gambar background terlebih dahulu.")
            return

        with st.spinner("Menghapus background... (pertama kali mungkin agak lama karena download model ~170MB)"):
            try:
                original_fg, removed_bg, final_result = run_pipeline(fg_file, bg_file)
            except Exception as exc:
                st.error(f"**Processing gagal:** {exc}")
                st.code(str(exc))
                return

        # Results
        st.markdown("<hr class='rule'>", unsafe_allow_html=True)
        st.markdown("<p class='section-label'>03 — Results</p>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3, gap="medium")
        with col1:
            render_image_panel(original_fg, "Original")
        with col2:
            render_image_panel(removed_bg, "Background removed")
        with col3:
            render_image_panel(final_result, "Final composite")

        st.markdown("<hr class='rule'>", unsafe_allow_html=True)
        st.download_button(
            label="⬇  Download final image",
            data=image_to_bytes(final_result),
            file_name="result.png",
            mime="image/png",
        )


if __name__ == "__main__":
    main()