"""Formatting and column resolution utilities."""

from __future__ import annotations

import pandas as pd


def fmt_big(n: float | int) -> str:
    """Format large numbers with T/B/M/K suffixes.

    Examples:
        >>> fmt_big(1_500_000)
        '1.5M'
        >>> fmt_big(450)
        '450'
    """
    if pd.isna(n):
        return "N/A"
    n_float = float(n)
    if n_float >= 1e12:
        return f"{n_float / 1e12:.1f}T"
    if n_float >= 1e9:
        return f"{n_float / 1e9:.1f}B"
    if n_float >= 1e6:
        return f"{n_float / 1e6:.1f}M"
    if n_float >= 1e3:
        return f"{n_float / 1e3:.1f}K"
    return f"{n_float:.0f}"


def get_track_col(df: pd.DataFrame) -> str | None:
    """Return the track-name column ('Track' or 'Track Name'), or None if absent.

    Different variants of the Kaggle dataset name this column either 'Track'
    or 'Track Name'. This helper handles both seamlessly.
    """
    for name in ("Track", "Track Name"):
        if name in df.columns:
            return name
    return None
