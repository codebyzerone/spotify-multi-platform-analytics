"""
components/insights.py — Computed multi-platform insights & performance efficiency.

Computes:
1. Cross-platform correlation drivers (which external platform metric correlates
   most strongly with Spotify Streams).
2. Streaming efficiency metrics (streams per playlist, reach per playlist).
3. Year-over-Year release trend analytics and growth summary.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from data_loader import ALL_PLATFORM_COLS
from utils.charts import horizontal_bar
from utils.formatting import fmt_big
from utils.theme import PLOTLY_LAYOUT, SPOTIFY_COLORS


def compute_cross_platform_driver(df: pd.DataFrame) -> dict[str, object] | None:
    """Find the non-Spotify metric with the strongest correlation to Spotify Streams.

    Returns a dict with:
    - 'metric': display name of the metric
    - 'r': Pearson correlation coefficient (-1.0 to 1.0)
    - 'sample_size': number of valid paired observations
    Or None if Spotify Streams or candidate metrics are unavailable.
    """
    if "Spotify Streams" not in df.columns:
        return None

    # Platform metrics excluding Spotify's own metrics
    non_spotify_cols = [
        col for col in ALL_PLATFORM_COLS
        if col in df.columns and not col.startswith("Spotify")
    ]
    if not non_spotify_cols:
        return None

    best_metric: str | None = None
    best_r: float = 0.0
    best_n: int = 0

    for col in non_spotify_cols:
        paired = df[["Spotify Streams", col]].dropna()
        if len(paired) < 3:
            continue
        # Avoid zero variance
        if paired["Spotify Streams"].std() == 0 or paired[col].std() == 0:
            continue
        r = float(paired["Spotify Streams"].corr(paired[col]))
        if pd.notna(r) and abs(r) > abs(best_r):
            best_r = r
            best_metric = col
            best_n = len(paired)

    if best_metric is None:
        return None

    return {
        "metric": best_metric,
        "r": best_r,
        "sample_size": best_n,
    }


def compute_platform_efficiency(df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-artist streaming efficiency metrics.

    Metrics:
    - Streams per Playlist: Total Streams / Total Playlist Count
    - Reach per Playlist: Total Reach / Total Playlist Count
    """
    if "Artist" not in df.columns:
        return pd.DataFrame()

    has_streams = "Spotify Streams" in df.columns
    has_count = "Spotify Playlist Count" in df.columns
    has_reach = "Spotify Playlist Reach" in df.columns

    if not (has_streams and has_count):
        return pd.DataFrame()

    grouped = df.groupby("Artist", as_index=False).agg({
        "Spotify Streams": "sum",
        "Spotify Playlist Count": "sum",
        **({"Spotify Playlist Reach": "sum"} if has_reach else {}),
    })

    # Filter out artists with 0 playlists to prevent division by zero
    grouped = grouped[grouped["Spotify Playlist Count"] > 0].copy()
    if grouped.empty:
        return pd.DataFrame()

    grouped["Streams per Playlist"] = (
        grouped["Spotify Streams"] / grouped["Spotify Playlist Count"]
    ).round(0)

    if has_reach:
        grouped["Reach per Playlist"] = (
            grouped["Spotify Playlist Reach"] / grouped["Spotify Playlist Count"]
        ).round(0)

    return grouped.sort_values("Streams per Playlist", ascending=False).reset_index(drop=True)


def render_platform_insights(df: pd.DataFrame) -> None:
    """Render cross-platform analytics, efficiency metrics, and YoY trends."""
    st.markdown("## 🌐 Cross-Platform & Market Insights")
    st.caption("Computed cross-network dynamics, playlist efficiency, and temporal trends")

    col_left, col_right = st.columns([1, 1])

    # ── Left: Cross-Platform Driver & Efficiency Insights ─────────────────────
    with col_left:
        st.markdown("### 🔗 Cross-Platform Synergy")
        driver = compute_cross_platform_driver(df)
        if driver is not None:
            direction = "positive" if driver["r"] >= 0 else "inverse"
            st.markdown(
                f"""
                <div style='background: linear-gradient(135deg, #16213e 0%, #0d1117 100%);
                            border-left: 4px solid #1ed760; padding: 14px 18px; border-radius: 8px;'>
                    <div style='color: #b3b3b3; font-size: 0.85rem; text-transform: uppercase;'>
                        Strongest Platform Predictor
                    </div>
                    <div style='font-size: 1.25rem; font-weight: 700; color: #ffffff; margin-top: 4px;'>
                        {driver['metric']}
                    </div>
                    <div style='color: #1ed760; font-size: 1.05rem; font-weight: 600; margin-top: 2px;'>
                        Pearson r = {driver['r']:+.2f} ({direction} correlation)
                    </div>
                    <div style='color: #888; font-size: 0.8rem; margin-top: 6px;'>
                        Computed across {driver['sample_size']} paired track observations.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("Insufficient cross-platform metrics to determine correlation drivers.")

        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        st.markdown("### ⚡ Playlist Efficiency")

        eff_df = compute_platform_efficiency(df)
        if not eff_df.empty:
            top_eff = eff_df.iloc[0]
            st.markdown(
                f"• **Most efficient artist by playlist yield:** **{top_eff['Artist']}** "
                f"generating **{fmt_big(top_eff['Streams per Playlist'])} streams** per playlist placement."
            )
            if "Reach per Playlist" in eff_df.columns:
                top_reach = eff_df.sort_values("Reach per Playlist", ascending=False).iloc[0]
                st.markdown(
                    f"• **Highest reach multiplier:** **{top_reach['Artist']}** "
                    f"averaging **{fmt_big(top_reach['Reach per Playlist'])} potential listeners** per playlist."
                )

            # Mini bar chart of top 5 efficient artists
            top5_eff = eff_df.head(5).sort_values("Streams per Playlist", ascending=True)
            fig_eff = horizontal_bar(
                top5_eff,
                x="Streams per Playlist",
                y="Artist",
                title="Top Artists by Streams per Playlist",
                height=260,
            )
            fig_eff.update_traces(
                text=top5_eff["Streams per Playlist"],
                texttemplate="%{text:.2s}",
                textposition="outside",
            )
            st.plotly_chart(fig_eff, use_container_width=True)
        else:
            st.info("Playlist count and streaming metrics required for efficiency calculation.")

    # ── Right: Year-over-Year Trajectory ───────────────────────────────────────
    with col_right:
        st.markdown("### 📅 Release Year Trajectory")
        if "Release Year" in df.columns and df["Release Year"].notna().any():
            yearly = (
                df.dropna(subset=["Release Year"])
                .groupby("Release Year", as_index=False)
                .agg({
                    "Track": "count" if "Track" in df.columns else "size",
                    **({"Spotify Streams": "sum"} if "Spotify Streams" in df.columns else {}),
                    **({"Spotify Popularity": "mean"} if "Spotify Popularity" in df.columns else {}),
                })
                .rename(columns={"Track": "Tracks"})
            )
            yearly["Release Year"] = yearly["Release Year"].astype(int).astype(str)

            if len(yearly) > 1:
                y_col = "Spotify Streams" if "Spotify Streams" in yearly.columns else "Tracks"
                fig_yr = px.bar(
                    yearly,
                    x="Release Year",
                    y=y_col,
                    color=y_col,
                    color_continuous_scale=["#16213e", "#1ed760"],
                    labels={y_col: y_col, "Release Year": "Year"},
                )
                fig_yr.update_layout(
                    **PLOTLY_LAYOUT,
                    title=f"Volume by Release Year ({y_col})",
                    height=360,
                    coloraxis_showscale=False,
                )
                st.plotly_chart(fig_yr, use_container_width=True)

                # Computed YoY insight
                peak_year_row = yearly.loc[yearly[y_col].idxmax()]
                st.markdown(
                    f"• **Peak Catalog Year:** **{peak_year_row['Release Year']}** "
                    f"with **{fmt_big(peak_year_row[y_col]) if y_col == 'Spotify Streams' else peak_year_row[y_col]}** "
                    f"total {'streams' if y_col == 'Spotify Streams' else 'tracks'}."
                )
            else:
                st.info(f"Dataset currently filtered to a single release year ({yearly['Release Year'].iloc[0]}).")
        else:
            st.info("Release dates not available for trajectory analysis.")

