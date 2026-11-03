"""Theming constants and styling for the Streamlit dashboard."""

from __future__ import annotations

CUSTOM_CSS: str = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* KPI metric cards */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid rgba(30, 215, 96, 0.15);
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
div[data-testid="stMetric"] label {
    color: #b3b3b3 !important;
    font-size: 0.8rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #1ed760 !important;
    font-weight: 700;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #161b22 100%);
    border-right: 1px solid rgba(30, 215, 96, 0.1);
}

/* Section dividers */
hr {
    border-color: rgba(30, 215, 96, 0.15) !important;
}

/* Tab styling */
button[data-baseweb="tab"] {
    font-weight: 600 !important;
}

/* Dataframe styling */
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(30, 215, 96, 0.1);
    border-radius: 8px;
}
</style>
"""

PLOTLY_LAYOUT: dict[str, object] = {
    "template": "plotly_dark",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"family": "Inter, sans-serif", "color": "#e0e0e0"},
    "margin": {"l": 40, "r": 40, "t": 50, "b": 40},
}

SPOTIFY_COLORS: list[str] = [
    "#1ed760", "#1db954", "#17a74a", "#14943f",
    "#b3b3b3", "#ff6b6b", "#ffd93d", "#6bcbff",
    "#c084fc", "#fb923c", "#f472b6",
]
