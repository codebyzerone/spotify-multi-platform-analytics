"""Artist analytics views: performance tables, top rankings, comparisons, and insights."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.charts import horizontal_bar
from utils.formatting import fmt_big, get_track_col
from utils.theme import PLOTLY_LAYOUT, SPOTIFY_COLORS

# Declarative spec: (source_column, agg_func, display_label)
_AGG_SPEC = [
    ("Spotify Streams",        "sum",  "Total Streams"),
    ("Track Score",            "mean", "Avg Track Score"),
    ("Spotify Popularity",     "mean", "Avg Popularity"),
    ("Spotify Playlist Reach", "mean", "Avg Playlist Reach"),
]


def build_artist_agg(df: pd.DataFrame) -> pd.DataFrame:
    """Group by Artist and compute aggregate metrics.

    Only includes columns that actually exist in the dataframe so the
    dashboard degrades gracefully when optional columns are absent.
    Returns a sorted DataFrame (by Total Streams desc, then Tracks desc).
    """
    track_col = get_track_col(df)

    agg_dict = {track_col: "count"} if track_col else {}
    rename_map = {track_col: "Tracks"} if track_col else {}

    for src, func, label in _AGG_SPEC:
        if src in df.columns:
            agg_dict[src] = func
            rename_map[src] = label

    grouped = df.groupby("Artist", as_index=False).agg(agg_dict)
    grouped = grouped.rename(columns=rename_map)

    sort_col = "Total Streams" if "Total Streams" in grouped.columns else "Tracks"
    return grouped.sort_values(sort_col, ascending=False).reset_index(drop=True)


def available_metrics(artist_df: pd.DataFrame) -> list[tuple[str, str]]:
    """Return [(display_label, column_name), …] for every metric column
    present in the aggregated artist DataFrame.
    """
    candidates = [
        ("Spotify Streams",    "Total Streams"),
        ("Track Score",        "Avg Track Score"),
        ("Spotify Popularity", "Avg Popularity"),
        ("Playlist Reach",     "Avg Playlist Reach"),
        ("Playlist Count",     "Total Playlist Count"),
        ("Number of Tracks",   "Tracks"),
    ]
    return [(label, col) for label, col in candidates if col in artist_df.columns]


def render_artist_analytics(df: pd.DataFrame) -> None:
    """Master section for Artist Analytics.

    Renders:
    1. Performance Table
    2. Top Artists Chart
    3. Head-to-Head Artist Comparison
    4. Auto-Computed Artist Insights
    """
    st.markdown("## 🎤 Artist Analytics")
    st.caption("Who dominates the charts — and by how much?")

    if "Artist" not in df.columns or df["Artist"].dropna().empty:
        st.info("No artist data available.")
        return

    # Pre-compute the aggregated artist table (shared by all sub-features)
    artist_df = build_artist_agg(df)

    if artist_df.empty:
        st.info("No artist summary available for current filter selection.")
        return

    # Attach Playlist Count if the source column exists
    if "Spotify Playlist Count" in df.columns:
        artist_df["Total Playlist Count"] = (
            df.groupby("Artist")["Spotify Playlist Count"]
            .sum()
            .reindex(artist_df["Artist"])
            .values
        )

    metrics = available_metrics(artist_df)
    metric_cols = [col for _, col in metrics]

    # ── 1. Performance Table ──────────────────────────────────────────────────
    st.markdown("### 📋 Artist Performance Table")

    display_df = artist_df.copy()
    for col in ("Total Streams", "Avg Playlist Reach"):
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(
                lambda v: fmt_big(v) if pd.notna(v) else "N/A"
            )
    for col in ("Avg Track Score", "Avg Popularity"):
        if col in display_df.columns:
            display_df[col] = display_df[col].round(1)

    st.dataframe(display_df.head(50), use_container_width=True, hide_index=True)
    st.markdown("---")

    # ── 2. Top Artists Chart ──────────────────────────────────────────────────
    if metrics:
        st.markdown("### 🏆 Top Artists")
        c1, c2 = st.columns([2, 1])
        with c1:
            selected_label = st.selectbox(
                "Rank artists by",
                [label for label, _ in metrics],
                key="artist_rank_metric",
            )
        with c2:
            max_limit = min(20, max(5, len(artist_df)))
            top_n = st.slider("Top N", 5, max(5, max_limit), min(10, max_limit), key="artist_top_n")

        rank_col = dict(metrics)[selected_label]
        top_artists = artist_df.nlargest(top_n, rank_col).sort_values(rank_col, ascending=True)

        fig = horizontal_bar(
            top_artists,
            x=rank_col,
            y="Artist",
            title=f"Top {top_n} Artists by {selected_label}",
            height=max(380, top_n * 34),
            xaxis_title=selected_label,
        )
        fig.update_traces(
            text=top_artists[rank_col],
            texttemplate="%{text:.3s}",
            textposition="outside",
            textfont_size=11,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("---")

    # ── 3. Artist Comparison ──────────────────────────────────────────────────
    st.markdown("### 🔀 Artist Comparison")

    all_artists = artist_df["Artist"].tolist()
    default_picks = all_artists[:min(3, len(all_artists))]

    selected_artists = st.multiselect(
        "Select up to 3 artists to compare",
        options=all_artists,
        default=default_picks,
        max_selections=3,
        key="artist_compare",
    )

    if len(selected_artists) >= 2:
        compare_df = artist_df[artist_df["Artist"].isin(selected_artists)]
        compare_cols = [
            c for c in metric_cols
            if c in compare_df.columns and c != "Total Playlist Count"
        ]

        if compare_cols:
            melted = compare_df.melt(
                id_vars="Artist",
                value_vars=compare_cols,
                var_name="Metric",
                value_name="Value",
            )
            melted["Raw"] = melted["Value"].copy()
            for m in compare_cols:
                mask = melted["Metric"] == m
                max_val = melted.loc[mask, "Value"].max()
                if max_val > 0:
                    melted.loc[mask, "Value"] = melted.loc[mask, "Value"] / max_val * 100

            fig_cmp = px.bar(
                melted,
                x="Metric",
                y="Value",
                color="Artist",
                barmode="group",
                color_discrete_sequence=SPOTIFY_COLORS,
                custom_data=["Raw"],
                labels={"Value": "Relative %", "Metric": ""},
            )
            fig_cmp.update_traces(
                hovertemplate="%{x}: %{customdata[0]:,.0f}<extra>%{fullData.name}</extra>",
            )
            fig_cmp.update_layout(
                **PLOTLY_LAYOUT,
                title="Artist Head-to-Head",
                height=420,
                legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
                yaxis_title="Relative Scale (0–100)",
            )
            st.plotly_chart(fig_cmp, use_container_width=True)
        else:
            st.info("No comparative metrics available.")
    else:
        st.info("Select at least **2** artists to see a head-to-head comparison.")

    st.markdown("---")

    # ── 4. Artist Insights ────────────────────────────────────────────────────
    st.markdown("### 💡 Artist Insights")

    insights: list[str] = []

    if "Total Streams" in artist_df.columns and len(artist_df) > 0:
        top_row = artist_df.iloc[0]
        insights.append(
            f"**Highest-streamed artist:** {top_row['Artist']} "
            f"with **{fmt_big(top_row['Total Streams'])}** total streams"
        )

    if "Tracks" in artist_df.columns:
        insights.append(f"**Average tracks per artist:** {artist_df['Tracks'].mean():.1f}")

    best_of = [
        ("Highest avg track score", "Avg Track Score", ".1f"),
        ("Highest avg popularity",  "Avg Popularity",  ".1f"),
    ]
    for label, col, fmt in best_of:
        if col in artist_df.columns and pd.notna(artist_df[col].max()):
            row = artist_df.loc[artist_df[col].idxmax()]
            insights.append(f"**{label}:** {row['Artist']} ({row[col]:{fmt}})")

    if "Total Streams" in artist_df.columns and len(artist_df) >= 2:
        first, second = artist_df.iloc[0], artist_df.iloc[1]
        gap = first["Total Streams"] - second["Total Streams"]
        insights.append(
            f"**Gap between #1 and #2:** {fmt_big(gap)} streams "
            f"({first['Artist']} leads {second['Artist']})"
        )

    for insight in insights:
        st.markdown(f"• {insight}")
