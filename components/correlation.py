"""Feature correlation heatmap component."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from utils.theme import PLOTLY_LAYOUT


def render_correlation_heatmap(df: pd.DataFrame) -> None:
    """Render a Plotly correlation heatmap for numeric features."""
    st.markdown("## 🔥 Feature Correlation Heatmap")
    st.caption("Pearson correlations across streaming & platform metrics")

    numeric_cols = [
        c for c in df.select_dtypes(include="number").columns
        if c != "Release Year"
    ]
    if len(numeric_cols) < 2:
        st.info("Not enough numeric columns to compute correlations.")
        return

    default_cols = numeric_cols[:min(12, len(numeric_cols))]
    selected = st.multiselect(
        "Select features for the heatmap",
        options=numeric_cols,
        default=default_cols,
        key="heatmap_cols",
    )
    if len(selected) < 2:
        st.warning("Select at least 2 features.")
        return

    corr = df[selected].corr()

    # Mask upper triangle to avoid redundant mirrored pairs
    mask = np.triu(np.ones_like(corr, dtype=bool), k=1)
    corr_masked = corr.where(~mask)

    fig = px.imshow(
        corr_masked,
        text_auto=".2f",
        color_continuous_scale=["#16213e", "#0e1117", "#1ed760"],
        zmin=-1,
        zmax=1,
        aspect="auto",
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title="Feature Correlation Matrix",
        height=max(500, len(selected) * 45),
        coloraxis_colorbar=dict(title="Pearson r"),
    )
    fig.update_traces(
        hovertemplate="%{x} vs %{y}: %{z:.2f}<extra></extra>",
    )
    st.plotly_chart(fig, use_container_width=True)

