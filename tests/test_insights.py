"""
tests/test_insights.py — Unit tests for computed analytical insights.
"""

from __future__ import annotations

import pandas as pd
import pytest

from components.insights import (
    compute_cross_platform_driver,
    compute_platform_efficiency,
)


def test_cross_platform_driver_computation():
    """Correctly identifies the platform metric with the highest correlation to Spotify Streams."""
    df = pd.DataFrame({
        "Track": [f"Track {i}" for i in range(10)],
        "Artist": ["Artist A"] * 5 + ["Artist B"] * 5,
        # Spotify Streams linearly matched to YouTube Views (r = 1.0)
        "Spotify Streams": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
        "YouTube Views": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        # TikTok Views has weak / negative relationship
        "TikTok Views": [100, 90, 80, 70, 60, 50, 40, 30, 20, 10],
    })

    driver = compute_cross_platform_driver(df)
    assert driver is not None
    assert driver["metric"] == "YouTube Views"
    assert pytest.approx(driver["r"], 0.01) == 1.0
    assert driver["sample_size"] == 10


def test_cross_platform_driver_missing_spotify():
    """Returns None gracefully when Spotify Streams is missing."""
    df = pd.DataFrame({
        "Track": ["T1", "T2"],
        "YouTube Views": [10, 20],
    })
    assert compute_cross_platform_driver(df) is None


def test_platform_efficiency_computation():
    """Calculates streams per playlist and reach per playlist correctly."""
    df = pd.DataFrame({
        "Artist": ["Artist X", "Artist X", "Artist Y"],
        "Spotify Streams": [10_000, 20_000, 50_000],
        "Spotify Playlist Count": [2, 3, 10],
        "Spotify Playlist Reach": [100_000, 200_000, 400_000],
    })

    eff = compute_platform_efficiency(df)
    assert not eff.empty
    assert len(eff) == 2

    # Artist X: (10k + 20k) / (2 + 3) = 30k / 5 = 6000
    row_x = eff[eff["Artist"] == "Artist X"].iloc[0]
    assert row_x["Streams per Playlist"] == 6000.0
    assert row_x["Reach per Playlist"] == 60000.0

    # Artist Y: 50k / 10 = 5000
    row_y = eff[eff["Artist"] == "Artist Y"].iloc[0]
    assert row_y["Streams per Playlist"] == 5000.0
    assert row_y["Reach per Playlist"] == 40000.0


def test_platform_efficiency_zero_playlists():
    """Artists with 0 playlists are safely excluded from division."""
    df = pd.DataFrame({
        "Artist": ["Artist Zero"],
        "Spotify Streams": [10_000],
        "Spotify Playlist Count": [0],
    })
    eff = compute_platform_efficiency(df)
    assert eff.empty
