"""Sidebar filter controls and upload overrides."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from data_loader import load_uploaded_file, validate_required_columns

_DEMO_KEY = "demo_mode_active"


def is_demo_mode() -> bool:
    """Check whether the dashboard is currently running on demo data."""
    return bool(st.session_state.get(_DEMO_KEY, False))


def set_demo_mode(active: bool) -> None:
    """Set the session-state demo mode flag."""
    st.session_state[_DEMO_KEY] = active


def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    """Render sidebar filters and return the filtered DataFrame."""
    with st.sidebar:
        st.markdown("## 🎧 Filters")
        st.markdown("---")

        # Artist filter
        artists = sorted(df["Artist"].dropna().unique().tolist())
        selected_artists = st.multiselect(
            "🎤 Artists",
            options=artists,
            default=[],
            help="Leave empty to include all artists",
            key="sidebar_artist_filter",
        )

        # Year range
        if "Release Year" in df.columns and df["Release Year"].notna().any():
            min_yr = int(df["Release Year"].min())
            max_yr = int(df["Release Year"].max())
            if min_yr < max_yr:
                year_range = st.slider(
                    "📅 Release Year",
                    min_value=min_yr,
                    max_value=max_yr,
                    value=(min_yr, max_yr),
                    key="sidebar_year_slider",
                )
            else:
                year_range = (min_yr, max_yr)
        else:
            year_range = None

        # Apply filters
        mask = pd.Series(True, index=df.index)
        if selected_artists:
            mask &= df["Artist"].isin(selected_artists)
        if year_range is not None:
            mask &= df["Release Year"].between(*year_range)

        filtered = df[mask]

        st.markdown("---")
        st.caption(f"**{len(filtered):,}** of **{len(df):,}** tracks selected")

        if not filtered.empty:
            csv_bytes = filtered.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download filtered data (CSV)",
                data=csv_bytes,
                file_name="spotify_filtered_tracks.csv",
                mime="text/csv",
                key="sidebar_download_csv",
                use_container_width=True,
            )

        # In demo mode, offer a way to exit by uploading real data
        if is_demo_mode():
            st.markdown("---")
            uploaded = st.file_uploader(
                "📤 Replace demo with your dataset",
                type=["csv", "zip"],
                key="sidebar_upload_replace",
            )
            if uploaded is not None:
                try:
                    raw = load_uploaded_file(uploaded)
                    missing = validate_required_columns(raw)
                    if missing:
                        st.error(
                            f"Missing required columns: {', '.join(missing)}. "
                            "Please upload the Kaggle Spotify 2024 dataset."
                        )
                    else:
                        set_demo_mode(False)
                        st.session_state["_uploaded_raw_df"] = raw
                        st.rerun()
                except ValueError as exc:
                    st.error(str(exc))

    return filtered
