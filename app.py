"""
app.py — Spotify 2024 Multi-Platform Analytics Dashboard.

Entry point orchestrating data loading, preprocessing, filter application,
and modular component rendering.
"""

from __future__ import annotations

from pathlib import Path
import streamlit as st

from components.artist import render_artist_analytics
from components.correlation import render_correlation_heatmap
from components.distributions import render_distributions
from components.insights import render_platform_insights
from components.kpis import render_kpis
from components.sidebar import is_demo_mode, render_sidebar, set_demo_mode
from data_loader import (
    clean_data,
    generate_demo_dataframe,
    load_data,
    load_uploaded_file,
    validate_required_columns,
)
from utils.theme import CUSTOM_CSS

# ─── Page Config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Spotify 2024 · Multi-Platform Analytics",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

DATA_PATH = Path("data/spotify_2024.csv")
DATA_ZIP_PATH = Path("data/spotify_2024.zip")


# ─── Landing Page ─────────────────────────────────────────────────────────────

def render_missing_data_page() -> None:
    """Landing view when no dataset is detected on disk."""
    st.markdown("---")
    _, col2, _ = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ## 📁 Dataset Not Found

        Place your **Most Streamed Spotify Songs 2024** CSV at:

        ```
        data/spotify_2024.csv
        ```

        ### How to get the dataset
        1. Visit [Kaggle – Most Streamed Spotify Songs 2024](https://www.kaggle.com/datasets/nelgiriyewithana/most-streamed-spotify-songs-2024)
        2. Download the CSV file
        3. Rename it to `spotify_2024.csv`
        4. Place it in the `data/` folder of this project
        5. Refresh this page ↻

        ---

        ### Or try the demo
        """)
        st.button(
            "🎵 Load demo sample",
            on_click=lambda: set_demo_mode(True),
            type="primary",
            use_container_width=True,
            key="demo_button_landing",
        )
        st.caption(
            "Loads 16 synthetic tracks with illustrative data — "
            "not real Kaggle data."
        )


# ─── Header & Footer ──────────────────────────────────────────────────────────

def render_header() -> None:
    """Render branded top banner."""
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 0 0;'>
        <h1 style='font-size:2.4rem; font-weight:700;
            background: linear-gradient(90deg, #1ed760, #1db954, #6bcbff);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 0;'>
            🎧 Spotify 2024 · Multi-Platform Analytics
        </h1>
        <p style='color:#b3b3b3; font-size:0.95rem; margin-top:4px;'>
            Exploring streaming patterns across Spotify, YouTube, TikTok & more
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_footer() -> None:
    """Render footer citation."""
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center; color:#666; font-size:0.8rem; padding:10px;'>"
        "Built with Streamlit & Plotly · Dataset: "
        "<a href='https://www.kaggle.com/datasets/nelgiriyewithana/most-streamed-spotify-songs-2024' "
        "style='color:#1db954;'>Kaggle</a>"
        "</div>",
        unsafe_allow_html=True,
    )


# ─── Main Pipeline ────────────────────────────────────────────────────────────

def main() -> None:
    """Main application loop."""
    render_header()

    raw = None

    # Priority 1: User uploaded file replacing demo mode
    if "_uploaded_raw_df" in st.session_state:
        raw = st.session_state.pop("_uploaded_raw_df")

    # Priority 2: File on disk
    if raw is None:
        data_path = None
        if DATA_PATH.exists():
            data_path = DATA_PATH
        elif DATA_ZIP_PATH.exists():
            data_path = DATA_ZIP_PATH

        if data_path is not None:
            try:
                raw = load_data(data_path)
            except (ValueError, Exception) as exc:
                st.error(
                    f"**Error loading dataset:** {exc}\n\n"
                    "Try re-downloading the CSV from Kaggle, or upload it directly."
                )
                st.stop()

    # Priority 3: Interactive demo mode
    if st.query_params.get("demo", "").lower() in ("true", "1", "yes"):
        set_demo_mode(True)

    if raw is None and is_demo_mode():
        raw = generate_demo_dataframe()

    # Priority 4: File upload widget or missing data page
    if raw is None:
        st.markdown("---")
        uploaded = st.file_uploader(
            "📤 Upload your Spotify 2024 dataset",
            type=["csv", "zip"],
            key="main_file_uploader",
        )
        if uploaded is not None:
            try:
                raw = load_uploaded_file(uploaded)
                missing = validate_required_columns(raw)
                if missing:
                    st.error(
                        f"**Missing required columns:** {', '.join(missing)}.\n\n"
                        "Please upload the [Kaggle Spotify 2024 dataset]"
                        "(https://www.kaggle.com/datasets/nelgiriyewithana/"
                        "most-streamed-spotify-songs-2024)."
                    )
                    st.stop()
            except ValueError as exc:
                st.error(str(exc))
                st.stop()
        else:
            render_missing_data_page()
            st.stop()

    # Demo mode notification
    if is_demo_mode():
        st.warning(
            "🎵 **Demo sample** — You are viewing illustrative data with "
            "synthetic tracks. Upload the real Kaggle dataset to replace it.",
            icon="⚠️",
        )

    df = clean_data(raw)

    if df.empty:
        st.error(
            "**No valid data rows found in the dataset.**\n\n"
            "All rows were empty or invalid. Please upload a valid CSV or ZIP file."
        )
        st.stop()

    missing = validate_required_columns(df)
    if missing:
        st.error(
            f"**Missing required columns after cleaning:** {', '.join(missing)}.\n\n"
            "The uploaded file does not appear to be the Spotify 2024 dataset."
        )
        st.stop()

    # Sidebar filtering
    filtered = render_sidebar(df)

    if filtered.empty:
        st.warning(
            "No tracks match the current filters. "
            "Try broadening the artist selection or year range in the sidebar."
        )
        st.stop()

    # Render modular visual sections
    render_kpis(filtered)
    st.markdown("---")

    render_artist_analytics(filtered)
    st.markdown("---")

    render_platform_insights(filtered)
    st.markdown("---")

    render_correlation_heatmap(filtered)
    st.markdown("---")

    render_distributions(filtered)

    render_footer()


if __name__ == "__main__":
    main()
