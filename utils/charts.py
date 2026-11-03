"""Reusable chart builders for consistent visual styling."""

from __future__ import annotations

from typing import Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.theme import PLOTLY_LAYOUT


def horizontal_bar(
    data: pd.DataFrame,
    x: str,
    y: str,
    title: str,
    height: int,
    **extra_layout: Any,
) -> go.Figure:
    """Create a styled horizontal Plotly bar chart and return the figure."""
    fig = px.bar(
        data,
        x=x,
        y=y,
        orientation="h",
        color=x,
        color_continuous_scale=["#16213e", "#1ed760"],
        labels={x: x, y: ""},
    )
    fig.update_layout(
        **PLOTLY_LAYOUT,
        title=title,
        height=height,
        coloraxis_showscale=False,
        yaxis=dict(tickfont=dict(size=11)),
        **extra_layout,
    )
    return fig

