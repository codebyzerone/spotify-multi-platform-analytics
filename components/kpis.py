"""Top-level Key Performance Indicator (KPI) metric cards."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.formatting import fmt_big


def render_kpis(df: pd.DataFrame) -> None:
    """Render the top-level KPI metric cards.

    Displays:
    - Total Tracks
    - Total Streams (formatted with suffix)
    - Average Popularity
    - Top Artist (by track frequency in current slice)
    - Unique Artists
    """
    cols = st.columns(5)
    with cols[0]:
        st.metric("Total Tracks", f"{len(df):,}")
    with cols[1]:
        if "Spotify Streams" in df.columns and pd.notna(df["Spotify Streams"].sum()):
            st.metric("Total Streams", fmt_big(df["Spotify Streams"].sum()))
        else:
            st.metric("Total Streams", "N/A")
    with cols[2]:
        if "Spotify Popularity" in df.columns and pd.notna(df["Spotify Popularity"].mean()):
            st.metric("Avg Popularity", f"{df['Spotify Popularity'].mean():.1f}")
        else:
            st.metric("Avg Popularity", "N/A")
    with cols[3]:
        if "Artist" in df.columns and len(df) > 0 and df["Artist"].notna().any():
            st.metric("Top Artist", df["Artist"].value_counts().idxmax())
        else:
            st.metric("Top Artist", "N/A")
    with cols[4]:
        if "Artist" in df.columns:
            st.metric("Unique Artists", f"{df['Artist'].nunique():,}")
        else:
            st.metric("Unique Artists", "N/A")

