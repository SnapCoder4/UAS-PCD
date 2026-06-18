"""
Background Removal & Replacement Web App
=========================================
Premium AI SaaS interface — dark luxury aesthetic.
Run: streamlit run app.py
"""

import io
import sys
import importlib
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG — must be the FIRST streamlit call
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Background Changer",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# SAFE IMPORT
# ─────────────────────────────────────────────────────────────────────────────
IMPORT_ERRORS = []

def try_import(module_name: str):
    try:
        return importlib.import_module(module_name)
    except Exception as e:
        IMPORT_ERRORS.append(f"❌ `{module_name}` — {e}")
        return None

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

from PIL import Image
from rembg import remove

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS — Premium Dark Luxury SaaS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=Syne+Mono&family=Inter:wght@300;400;500&display=swap');

/* ── RESET & BASE ── */
*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
    background: transparent !important;
    color: #d4cfc8 !important;
    font-family: 'Inter', sans-serif !important;
}

/* Deep layered background */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    z-index: -2;
    background:
        radial-gradient(ellipse 80% 50% at 20% 0%, rgba(99,60,180,0.18) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 10%, rgba(0,190,140,0.10) 0%, transparent 55%),
        radial-gradient(ellipse 100% 80% at 50% 100%, rgba(20,10,50,0.6) 0%, transparent 70%),
        #080810;
    pointer-events: none;
}

/* Noise grain overlay */
[data-testid="stAppViewContainer"]::after {
    content: '';
    position: fixed;
    inset: 0;
    z-index: -1;
    opacity: 0.025;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
    background-size: 128px 128px;
    pointer-events: none;
}

[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
#MainMenu, footer { visibility: hidden !important; }

/* ── MAIN CONTENT PADDING ── */
.block-container {
    padding: 3rem 4rem 6rem !important;
    max-width: 1280px !important;
}

/* ── HERO ── */
.hero-wrap {
    padding: 4rem 0 2rem;
    position: relative;
}
.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'Syne Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: #a899f5;
    background: rgba(124,111,224,0.12);
    border: 1px solid rgba(124,111,224,0.35);
    border-radius: 100px;
    padding: 0.3rem 0.9rem;
    margin-bottom: 1.6rem;
}
.hero-eyebrow::before {
    content: '';
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #a899f5;
    box-shadow: 0 0 6px #a899f5;
    animation: pulse-dot 2s ease-in-out infinite;
}
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.7); }
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: clamp(2.8rem, 5.5vw, 5rem);
    line-height: 1.0;
    letter-spacing: -0.03em;
    color: #f0ece4;
    margin: 0 0 1.2rem;
}
.hero-title .accent {
    background: linear-gradient(135deg, #a78bfa 0%, #38d9a9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-desc {
    font-family: 'Inter', sans-serif;
    font-weight: 300;
    font-size: 1.05rem;
    line-height: 1.7;
    color: #9b9690;
    max-width: 480px;
    margin: 0;
}
.hero-divider {
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(124,111,224,0.3) 30%, rgba(56,217,169,0.2) 70%, transparent);
    margin: 3rem 0;
}

/* ── SECTION LABELS ── */
.section-label {
    font-family: 'Syne Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.26em;
    text-transform: uppercase;
    color: #38d9a9;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(56,217,169,0.3), transparent);
}

/* ── UPLOAD GLASSMORPHISM CARDS ── */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 16px !important;
    padding: 1.4rem 1.6rem !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    transition: border-color 0.3s ease, background 0.3s ease, box-shadow 0.3s ease !important;
    box-shadow: 0 0 0 0 rgba(124,111,224,0) !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(124,111,224,0.4) !important;
    background: rgba(124,111,224,0.04) !important;
    box-shadow: 0 0 30px rgba(124,111,224,0.08), inset 0 1px 0 rgba(255,255,255,0.05) !important;
}
[data-testid="stFileUploader"] label {
    color: #9b9690 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    border: 1px dashed rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    transition: border-color 0.3s !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: rgba(124,111,224,0.5) !important;
}

/* ── PROCESS BUTTON ── */
[data-testid="stButton"] > button {
    width: 100% !important;
    background: linear-gradient(135deg, #6d4fc2 0%, #38d9a9 100%) !important;
    color: #fff !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.85rem 2.2rem !important;
    cursor: pointer !important;
    position: relative !important;
    overflow: hidden !important;
    transition: opacity 0.2s ease, transform 0.2s ease, box-shadow 0.3s ease !important;
    box-shadow: 0 4px 24px rgba(109,79,194,0.35), 0 1px 0 rgba(255,255,255,0.08) inset !important;
}
[data-testid="stButton"] > button::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.12) 0%, transparent 60%);
    pointer-events: none;
}
[data-testid="stButton"] > button:hover {
    opacity: 0.92 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 32px rgba(109,79,194,0.5), 0 1px 0 rgba(255,255,255,0.08) inset !important;
}
[data-testid="stButton"] > button:active {
    transform: translateY(0px) !important;
}

/* ── DOWNLOAD BUTTON ── */
[data-testid="stDownloadButton"] > button {
    background: rgba(255,255,255,0.03) !important;
    color: #a78bfa !important;
    border: 1px solid rgba(167,139,250,0.3) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    border-radius: 10px !important;
    padding: 0.7rem 2rem !important;
    backdrop-filter: blur(8px) !important;
    transition: all 0.25s ease !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(167,139,250,0.12) !important;
    border-color: rgba(167,139,250,0.6) !important;
    box-shadow: 0 0 20px rgba(167,139,250,0.2) !important;
    transform: translateY(-1px) !important;
}

/* ── ALERTS & WARNINGS ── */
[data-testid="stAlert"] {
    background: rgba(20,18,38,0.6) !important;
    border: 1px solid rgba(124,111,224,0.2) !important;
    border-left: 3px solid #7c6fe0 !important;
    color: #b0aab8 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    border-radius: 10px !important;
    backdrop-filter: blur(10px) !important;
}

/* ── SPINNER ── */
[data-testid="stSpinner"] {
    font-family: 'Syne Mono', monospace !important;
    color: #a899f5 !important;
    font-size: 0.8rem !important;
}

/* ── IMAGE PANELS ── */
.img-card {
    background: rgba(255,255,255,0.018);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1rem;
    transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    position: relative;
    overflow: hidden;
}
.img-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
    pointer-events: none;
}
.img-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.4), 0 0 0 1px rgba(124,111,224,0.15);
    border-color: rgba(124,111,224,0.18);
}
.img-caption {
    font-family: 'Syne Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #7a756e;
    margin-top: 0.75rem;
    text-align: center;
    padding: 0.4rem 0 0.1rem;
    border-top: 1px solid rgba(255,255,255,0.04);
}
.img-badge {
    display: inline-block;
    font-family: 'Syne Mono', monospace;
    font-size: 0.58rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #38d9a9;
    background: rgba(56,217,169,0.08);
    border: 1px solid rgba(56,217,169,0.2);
    border-radius: 4px;
    padding: 0.15rem 0.5rem;
    margin-bottom: 0.75rem;
    display: block;
    width: fit-content;
    margin-left: auto;
    margin-right: auto;
}

/* ── RESULTS SECTION ── */
.results-header {
    text-align: center;
    padding: 1rem 0 2rem;
}
.results-header h3 {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 1.5rem;
    color: #f0ece4;
    letter-spacing: -0.02em;
    margin: 0 0 0.4rem;
}
.results-header p {
    font-family: 'Inter', sans-serif;
    font-size: 0.82rem;
    color: #7a756e;
    margin: 0;
}

/* ── FOOTER ── */
.footer {
    margin-top: 5rem;
    padding: 2rem 0 1rem;
    border-top: 1px solid rgba(255,255,255,0.08);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
}
.footer-brand {
    font-family: 'Syne', sans-serif;
    font-weight: 700;
    font-size: 0.9rem;
    color: #8a8480;
    letter-spacing: -0.01em;
}
.footer-brand span {
    color: #a78bfa;
}
.footer-meta {
    font-family: 'Syne Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #6e6a65;
}

/* ── COLUMNS GAP ── */
[data-testid="column"] {
    padding: 0 0.5rem !important;
}

/* ── DIVIDER UTIL ── */
.glow-divider {
    width: 100%;
    height: 1px;
    background: linear-gradient(90deg,
        transparent 0%,
        rgba(124,111,224,0.25) 25%,
        rgba(56,217,169,0.18) 60%,
        transparent 100%
    );
    margin: 2.5rem 0;
}

/* ── STEP INDICATORS ── */
.step-row {
    display: flex;
    gap: 2rem;
    margin-bottom: 2.5rem;
    flex-wrap: wrap;
}
.step-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.78rem;
    color: #8a8580;
}
.step-num {
    width: 22px; height: 22px;
    border-radius: 50%;
    background: rgba(168,153,245,0.15);
    border: 1px solid rgba(168,153,245,0.35);
    color: #a899f5;
    font-family: 'Syne Mono', monospace;
    font-size: 0.6rem;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

/* ── UPLOAD PANEL WRAPPER ── */
.upload-wrap {
    background: rgba(255,255,255,0.015);
    border: 1px solid rgba(255,255,255,0.055);
    border-radius: 20px;
    padding: 1.6rem 1.6rem 1.2rem;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s, box-shadow 0.3s;
}
.upload-wrap::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.07), transparent);
    pointer-events: none;
}
.upload-wrap:hover {
    border-color: rgba(124,111,224,0.22);
    box-shadow: 0 8px 40px rgba(0,0,0,0.2), 0 0 40px rgba(124,111,224,0.06);
}
.upload-icon {
    font-size: 1.8rem;
    margin-bottom: 0.5rem;
    display: block;
    filter: grayscale(0.3);
}
.upload-title {
    font-family: 'Syne', sans-serif;
    font-weight: 600;
    font-size: 0.9rem;
    color: #c8c3bc;
    margin-bottom: 0.25rem;
    letter-spacing: -0.01em;
}
.upload-hint {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    color: #7a756e;
    margin-bottom: 1rem;
}

/* ── SUCCESS GLOW ── */
.result-glow-wrap {
    position: relative;
}
.result-glow-wrap::before {
    content: '';
    position: absolute;
    inset: -1px;
    border-radius: 17px;
    background: linear-gradient(135deg, rgba(109,79,194,0.35), rgba(56,217,169,0.25));
    z-index: -1;
    filter: blur(8px);
    opacity: 0;
    transition: opacity 0.4s;
}
.result-glow-wrap:hover::before { opacity: 1; }

</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PROCESSING FUNCTIONS (unchanged)
# ─────────────────────────────────────────────────────────────────────────────

def load_image(uploaded_file) -> Image.Image:
    uploaded_file.seek(0)
    raw_bytes = uploaded_file.read()
    return Image.open(io.BytesIO(raw_bytes))


def remove_background(image: Image.Image) -> Image.Image:
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
    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    return buffer.getvalue()


def run_pipeline(fg_file, bg_file):
    original_fg = load_image(fg_file).convert("RGB")
    background  = load_image(bg_file)
    removed_bg      = remove_background(original_fg)
    background_rgba = resize_background(background, original_fg.size)
    final_result    = composite_images(removed_bg, background_rgba)
    return original_fg, removed_bg, final_result


# ─────────────────────────────────────────────────────────────────────────────
# UI COMPONENTS
# ─────────────────────────────────────────────────────────────────────────────

def render_image_card(image, caption: str, badge: str = None):
    badge_html = f"<span class='img-badge'>{badge}</span>" if badge else ""
    st.markdown(f"<div class='img-card result-glow-wrap'>{badge_html}", unsafe_allow_html=True)
    st.image(image, use_container_width=True)
    st.markdown(f"<p class='img-caption'>{caption}</p></div>", unsafe_allow_html=True)


def main():
    # ── HERO SECTION ──
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-eyebrow">✦ AI-Powered Background Studio</div>
        <h1 class="hero-title">
            Remove.<br>Replace.<br><span class="accent">Transform.</span>
        </h1>
        <p class="hero-desc">
            Professional-grade background removal powered by deep learning.
            Swap any background in seconds — no editing skills required.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── STEP INDICATORS ──
    st.markdown("""
    <div class="step-row">
        <div class="step-item"><div class="step-num">1</div>Upload your subject image</div>
        <div class="step-item"><div class="step-num">2</div>Choose a new background</div>
        <div class="step-item"><div class="step-num">3</div>Process &amp; download</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    # ── UPLOAD SECTION ──
    col_fg, spacer, col_bg = st.columns([1, 0.06, 1])

    with col_fg:
        st.markdown("<p class='section-label'>01 · Subject Image</p>", unsafe_allow_html=True)
        st.markdown("""
        <div class="upload-wrap">
            <span class="upload-icon">🖼️</span>
            <div class="upload-title">Drop your subject here</div>
            <div class="upload-hint">PNG, JPG, JPEG, WEBP · The AI will isolate your subject</div>
        </div>
        """, unsafe_allow_html=True)
        fg_file = st.file_uploader(
            "Foreground", type=["png", "jpg", "jpeg", "webp"],
            key="fg", label_visibility="collapsed"
        )

    with col_bg:
        st.markdown("<p class='section-label'>02 · New Background</p>", unsafe_allow_html=True)
        st.markdown("""
        <div class="upload-wrap">
            <span class="upload-icon">🌅</span>
            <div class="upload-title">Drop your background here</div>
            <div class="upload-hint">PNG, JPG, JPEG, WEBP · Will be auto-resized to fit</div>
        </div>
        """, unsafe_allow_html=True)
        bg_file = st.file_uploader(
            "Background", type=["png", "jpg", "jpeg", "webp"],
            key="bg", label_visibility="collapsed"
        )

    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    # ── PROCESS BUTTON ──
    _, btn_col, _ = st.columns([1.5, 1, 1.5])
    with btn_col:
        process_clicked = st.button("✦  Process Image", use_container_width=True)

    # ── PROCESSING + RESULTS ──
    if process_clicked:
        if not fg_file:
            st.warning("⚠ Please upload a subject image to continue.")
            return
        if not bg_file:
            st.warning("⚠ Please upload a background image to continue.")
            return

        with st.spinner("Neural network processing your image — this may take a moment on first run..."):
            try:
                original_fg, removed_bg, final_result = run_pipeline(fg_file, bg_file)
            except Exception as exc:
                st.error(f"**Processing failed:** {exc}")
                st.code(str(exc))
                return

        # ── RESULTS HEADER ──
        st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="results-header">
            <h3>✦ Results</h3>
            <p>Your image has been processed successfully</p>
        </div>
        """, unsafe_allow_html=True)

        # ── IMAGE CARDS ──
        col1, col2, col3 = st.columns(3, gap="medium")
        with col1:
            render_image_card(original_fg, "Original", "Source")
        with col2:
            render_image_card(removed_bg, "Background Removed", "Masked")
        with col3:
            render_image_card(final_result, "Final Composite", "✦ Result")

        # ── DOWNLOAD ──
        st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
        _, dl_col, _ = st.columns([1.8, 1, 1.8])
        with dl_col:
            st.download_button(
                label="⬇  Download Result",
                data=image_to_bytes(final_result),
                file_name="cutout_ai_result.png",
                mime="image/png",
            )

    # ── FOOTER ──
    st.markdown("""
    <div class="footer">
        <div class="footer-meta">Powered by rembg · Built with Streamlit</div>
        <div class="footer-meta">Deep Learning Background Removal</div>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
