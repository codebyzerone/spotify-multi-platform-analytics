"""Distribution explorer component (histograms, violins, and top-N track rankings)."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.charts import horizontal_bar
from utils.formatting import get_track_col
from utils.theme import PLOTLY_LAYOUT


def render_distributions(df: pd.DataFrame) -> None:
    """Render distribution histograms/violins and Top-N track rankings."""
    st.markdown("## 📊 Distribution Explorer")

    tab_dist, tab_topn = st.tabs(["📈 Distributions", "🏆 Top-N Rankings"])

    numeric_cols = [
        c for c in df.select_dtypes(include="number").columns
        if c != "Release Year"
    ]

    with tab_dist:
        if not numeric_cols:
            st.info("No numeric columns available for distribution plots.")
            return

        col_pick = st.selectbox("Select a metric", numeric_cols, key="dist_col")
        plot_type = st.radio(
            "Plot type", ["Histogram", "Violin"], horizontal=True, key="dist_type"
        )

        series = df[col_pick].dropna()
        if series.empty:
            st.info(f"No non-empty data points for metric '{col_pick}'.")
        else:
            if plot_type == "Histogram":
                fig = px.histogram(
                    series,
                    nbins=50,
                    color_discrete_sequence=["#1ed760"],
                    labels={"value": col_pick},
                )
            else:
                fig = px.violin(
                    y=series,
                    color_discrete_sequence=["#1ed760"],
                    box=True,
                    points="outliers",
                    labels={"y": col_pick},
                )

            fig.update_layout(
                **PLOTLY_LAYOUT,
                title=f"Distribution of {col_pick}",
                height=400,
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

    with tab_topn:
        c1, c2 = st.columns([2, 1])

        label_col = get_track_col(df)
        if label_col is None:
            st.info("No track-name column found for rankings.")
            return

        if not numeric_cols:
            st.info("No numeric metrics available for ranking tracks.")
            return

        with c1:
            rank_metric = st.selectbox(
                "Rank by", numeric_cols, key="rank_metric"
            )
        with c2:
            max_n = min(30, max(5, len(df)))
            top_n = st.slider("Top N", 5, max(5, max_n), min(15, max_n), key="top_n")

        top = df.nlargest(top_n, rank_metric)[[label_col, "Artist", rank_metric]].copy()
        top["label"] = top[label_col].astype(str).str[:30] + " · " + top["Artist"].astype(str).str[:20]
        top = top.sort_values(rank_metric, ascending=True)

        fig = horizontal_bar(
            top,
            x=rank_metric,
            y="label",
            title=f"Top {top_n} Tracks by {rank_metric}",
            height=max(350, top_n * 28),
        )
        st.plotly_chart(fig, use_container_width=True)
