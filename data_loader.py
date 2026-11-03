"""
data_loader.py — Vectorized data loading & cleaning for Spotify 2024 dataset.

Responsibilities:
- Read CSV/ZIP files with encoding fallback
- Normalise column names and coerce types
- Provide a synthetic demo dataset for zero-download first-run experience
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import streamlit as st

if TYPE_CHECKING:
    from streamlit.runtime.uploaded_file_manager import UploadedFile

# ─── Column Constants ─────────────────────────────────────────────────────────

AUDIO_FEATURES: list[str] = [
    "Danceability", "Energy", "Valence", "Acousticness",
    "Instrumentalness", "Liveness", "Speechiness",
]

# Alternate column names (some Kaggle CSVs use % suffix)
AUDIO_FEATURES_PCT: list[str] = [f"{f} %" for f in AUDIO_FEATURES]
AUDIO_FEATURES_UNDERSCORE: list[str] = [f"{f.lower()}_%" for f in AUDIO_FEATURES]

PLATFORM_METRICS: dict[str, list[str]] = {
    "spotify": [
        "Spotify Streams", "Spotify Playlist Count",
        "Spotify Playlist Reach", "Spotify Popularity",
    ],
    "youtube": [
        "YouTube Views", "YouTube Likes", "YouTube Playlist Reach",
    ],
    "tiktok": [
        "TikTok Posts", "TikTok Likes", "TikTok Views",
    ],
    "apple_music": [
        "Apple Music Playlist Count",
    ],
    "deezer": [
        "Deezer Playlist Count", "Deezer Playlist Reach",
    ],
    "amazon": [
        "Amazon Playlist Count",
    ],
    "shazam": [
        "Shazam Counts",
    ],
}

ALL_PLATFORM_COLS: list[str] = [c for cols in PLATFORM_METRICS.values() for c in cols]

NUMERIC_COLS: list[str] = ALL_PLATFORM_COLS + AUDIO_FEATURES

ID_COLS: list[str] = ["Track", "Album Name", "Artist", "Release Date", "ISRC"]

REQUIRED_COLS: list[str] = ["Track", "Artist"]
"""Columns that *must* be present for the dashboard to function."""


# ─── Internal Helpers ─────────────────────────────────────────────────────────

def _normalise_audio_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Map alternate audio-feature column names to canonical names.

    Different versions of the Kaggle CSV use suffixes like " %" or
    "danceability_%" — this maps them all to the plain canonical names
    (e.g. "Danceability") so downstream code can use a single set of
    column names.
    """
    for canon, pct, uscore in zip(
        AUDIO_FEATURES, AUDIO_FEATURES_PCT, AUDIO_FEATURES_UNDERSCORE
    ):
        if canon not in df.columns:
            for alt in (pct, uscore):
                if alt in df.columns:
                    df = df.rename(columns={alt: canon})
                    break
    return df


def _coerce_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Vectorised coercion of object columns to numeric.

    Handles comma-separated numbers (e.g. "1,234,567") by stripping commas
    before conversion.  Non-convertible values become NaN.
    """
    present = [c for c in cols if c in df.columns]
    for c in present:
        if df[c].dtype == object:
            df[c] = df[c].astype(str).str.replace(",", "", regex=False)
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def _read_csv_from_zip(path: Path) -> pd.DataFrame:
    """Open a ZIP, find the first CSV inside, and read it."""
    with zipfile.ZipFile(path, "r") as zf:
        csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not csv_names:
            raise ValueError(f"No CSV file found inside {path}")
        with zf.open(csv_names[0]) as f:
            raw = f.read()
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            return pd.read_csv(io.BytesIO(raw), encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode CSV inside {path} with any known encoding.")


# ─── Validation ───────────────────────────────────────────────────────────────

def validate_required_columns(df: pd.DataFrame) -> list[str]:
    """Return a list of required columns that are missing from *df*.

    The dashboard needs at least a track-name column and an artist column to
    render any meaningful view.  Everything else degrades gracefully.
    """
    has_track = "Track" in df.columns or "Track Name" in df.columns
    missing: list[str] = []
    if not has_track:
        missing.append("Track (or Track Name)")
    if "Artist" not in df.columns:
        missing.append("Artist")
    return missing


# ─── Public API ───────────────────────────────────────────────────────────────

@st.cache_data(show_spinner="Loading dataset …")
def load_data(path: str | Path) -> pd.DataFrame:
    """Read CSV (or ZIP containing a CSV) with encoding fallback."""
    path = Path(path)
    if path.suffix.lower() == ".zip":
        return _read_csv_from_zip(path)
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            return pd.read_csv(path, encoding=enc)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not decode {path} with any known encoding.")


def load_uploaded_file(uploaded_file: UploadedFile) -> pd.DataFrame:
    """Read an uploaded file (CSV or ZIP) from Streamlit's file_uploader.

    Raises ``ValueError`` with a user-friendly message for corrupt ZIPs,
    unreadable CSVs, or ZIPs that contain no CSV files.
    """
    name = uploaded_file.name.lower()
    try:
        if name.endswith(".zip"):
            raw_bytes = uploaded_file.read()
            with zipfile.ZipFile(io.BytesIO(raw_bytes), "r") as zf:
                csv_names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
                if not csv_names:
                    raise ValueError(
                        "The uploaded ZIP does not contain any CSV files. "
                        "Please upload a ZIP that includes a .csv file, "
                        "or upload the CSV directly."
                    )
                with zf.open(csv_names[0]) as f:
                    csv_bytes = f.read()
            for enc in ("utf-8", "latin-1", "cp1252"):
                try:
                    return pd.read_csv(io.BytesIO(csv_bytes), encoding=enc)
                except UnicodeDecodeError:
                    continue
            raise ValueError(
                "Could not decode the CSV inside the uploaded ZIP. "
                "Try re-downloading the dataset from Kaggle."
            )
        else:
            return pd.read_csv(uploaded_file)
    except zipfile.BadZipFile:
        raise ValueError(
            "The uploaded file is not a valid ZIP archive. "
            "Please upload a valid .csv or .zip file."
        )
    except pd.errors.ParserError as exc:
        raise ValueError(
            f"Could not parse the uploaded CSV: {exc}. "
            "Make sure the file is a valid comma-separated CSV."
        )


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Vectorised cleaning pipeline.

    Steps:
    1. Strip whitespace from string columns
    2. Normalise audio-feature column names (handle % variants)
    3. Coerce numeric columns (handle commas, non-numeric values)
    4. Parse release dates → derive Release Year
    5. Drop rows that are entirely null
    6. Fill remaining NaN numerics with column median
    """
    df = df.copy()

    # 1. Strip whitespace
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].apply(lambda s: s.str.strip())

    # 2. Normalise audio feature column names
    df = _normalise_audio_cols(df)

    # 3. Coerce numeric
    df = _coerce_numeric(df, NUMERIC_COLS)

    # 4. Parse dates
    if "Release Date" in df.columns:
        df["Release Date"] = pd.to_datetime(
            df["Release Date"], errors="coerce", format="mixed"
        )
        df["Release Year"] = df["Release Date"].dt.year.astype("Int64")

    # 5. Drop all-null rows
    df = df.dropna(how="all")

    # 6. Fill missing numerics with median
    num_present = [c for c in NUMERIC_COLS if c in df.columns]
    df[num_present] = df[num_present].fillna(df[num_present].median())

    return df


# ─── Demo Data ─────────────────────────────────────────────────────────────────

# 16 tracks across 4 artists and 4 years gives enough spread to populate every
# chart section meaningfully.
_DEMO_TRACK_COUNT: int = 16


def generate_demo_dataframe() -> pd.DataFrame:
    """Build a small, self-contained demo DataFrame with illustrative data.

    The dataset uses generic names ("Demo Track 1", "Demo Artist A") so it is
    obvious the numbers are synthetic.  Every column that ``clean_data()``
    expects is included so all dashboard sections render correctly.

    Returns a *raw* DataFrame — callers should still pass it through
    ``clean_data()`` to exercise the full cleaning pipeline.
    """
    rng = np.random.RandomState(42)  # deterministic for reproducibility

    artists = ["Demo Artist A", "Demo Artist B", "Demo Artist C", "Demo Artist D"]
    years = [2021, 2022, 2023, 2024]

    rows: list[dict[str, object]] = []
    for i in range(1, _DEMO_TRACK_COUNT + 1):
        artist = artists[(i - 1) % len(artists)]
        year = years[(i - 1) % len(years)]
        rows.append({
            # Identity columns
            "Track": f"Demo Track {i}",
            "Album Name": f"Demo Album {((i - 1) // 4) + 1}",
            "Artist": artist,
            "Release Date": f"{year}-{rng.randint(1, 13):02d}-{rng.randint(1, 29):02d}",
            "ISRC": f"DEMO{i:08d}",
            # Spotify metrics — varied enough to make charts interesting
            "Spotify Streams": int(rng.randint(50_000, 5_000_000)),
            "Spotify Playlist Count": int(rng.randint(10, 500)),
            "Spotify Playlist Reach": int(rng.randint(100_000, 10_000_000)),
            "Spotify Popularity": int(rng.randint(30, 95)),
            # YouTube
            "YouTube Views": int(rng.randint(10_000, 50_000_000)),
            "YouTube Likes": int(rng.randint(500, 500_000)),
            "YouTube Playlist Reach": int(rng.randint(1_000, 1_000_000)),
            # TikTok
            "TikTok Posts": int(rng.randint(5, 5_000)),
            "TikTok Likes": int(rng.randint(1_000, 2_000_000)),
            "TikTok Views": int(rng.randint(10_000, 100_000_000)),
            # Other platforms
            "Apple Music Playlist Count": int(rng.randint(1, 200)),
            "Deezer Playlist Count": int(rng.randint(1, 150)),
            "Deezer Playlist Reach": int(rng.randint(1_000, 500_000)),
            "Amazon Playlist Count": int(rng.randint(1, 100)),
            "Shazam Counts": int(rng.randint(100, 500_000)),
            # Audio features (0–100 scale before cleaning)
            "Danceability": round(rng.uniform(20, 95), 1),
            "Energy": round(rng.uniform(15, 98), 1),
            "Valence": round(rng.uniform(5, 90), 1),
            "Acousticness": round(rng.uniform(1, 80), 1),
            "Instrumentalness": round(rng.uniform(0, 30), 1),
            "Liveness": round(rng.uniform(3, 40), 1),
            "Speechiness": round(rng.uniform(2, 50), 1),
        })

    return pd.DataFrame(rows)
