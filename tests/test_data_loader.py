"""
tests/test_data_loader.py — Comprehensive unit tests for data loading & cleaning.
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from data_loader import (
    AUDIO_FEATURES,
    clean_data,
    generate_demo_dataframe,
    load_data,
    load_uploaded_file,
    validate_required_columns,
    _read_csv_from_zip,
)


class MockUpload:
    """Mock Streamlit UploadedFile interface for testing."""

    def __init__(self, name: str, data: bytes):
        self.name = name
        self._data = data

    def read(self) -> bytes:
        return self._data


def test_whitespace_stripping():
    """String columns must have leading and trailing whitespace stripped."""
    raw = pd.DataFrame({
        "Track": ["  Song A  ", "Song B\t", "\nSong C "],
        "Artist": [" Artist 1 ", "Artist 2  ", "  Artist 3"],
    })
    cleaned = clean_data(raw)
    assert cleaned["Track"].tolist() == ["Song A", "Song B", "Song C"]
    assert cleaned["Artist"].tolist() == ["Artist 1", "Artist 2", "Artist 3"]


def test_audio_pct_normalisation():
    """Alternative column names ('Danceability %' and 'danceability_%') must map to canonical names."""
    raw_pct = pd.DataFrame({
        "Track": ["Track 1"],
        "Artist": ["Artist 1"],
        "Danceability %": [75.5],
        "Energy %": [80.0],
        "Valence %": [60.0],
    })
    cleaned_pct = clean_data(raw_pct)
    assert "Danceability" in cleaned_pct.columns
    assert "Energy" in cleaned_pct.columns
    assert "Valence" in cleaned_pct.columns
    assert "Danceability %" not in cleaned_pct.columns
    assert cleaned_pct["Danceability"].iloc[0] == 75.5

    raw_underscore = pd.DataFrame({
        "Track": ["Track 2"],
        "Artist": ["Artist 2"],
        "danceability_%": [65.0],
        "speechiness_%": [12.0],
    })
    cleaned_underscore = clean_data(raw_underscore)
    assert "Danceability" in cleaned_underscore.columns
    assert "Speechiness" in cleaned_underscore.columns
    assert cleaned_underscore["Danceability"].iloc[0] == 65.0


def test_numeric_coercion_with_commas():
    """Numbers with commas and strings must be coerced to numeric."""
    raw = pd.DataFrame({
        "Track": ["Track 1", "Track 2", "Track 3"],
        "Artist": ["Artist 1", "Artist 2", "Artist 3"],
        "Spotify Streams": ["1,500,000", "2,345,678", "invalid_number"],
        "YouTube Views": [1000, "5,000", None],
    })
    cleaned = clean_data(raw)
    # The invalid_number becomes NaN, then gets filled by median of [1.5M, 2.345678M]
    expected_median = (1500000 + 2345678) / 2
    assert cleaned["Spotify Streams"].iloc[0] == 1500000.0
    assert cleaned["Spotify Streams"].iloc[1] == 2345678.0
    assert cleaned["Spotify Streams"].iloc[2] == expected_median


def test_date_parsing_and_release_year():
    """Release Date must be parsed and Release Year extracted as integer."""
    raw = pd.DataFrame({
        "Track": ["Track 1", "Track 2", "Track 3"],
        "Artist": ["Artist 1", "Artist 2", "Artist 3"],
        "Release Date": ["2023-05-14", "1/15/2021", "invalid-date"],
    })
    cleaned = clean_data(raw)
    assert "Release Year" in cleaned.columns
    assert cleaned["Release Year"].iloc[0] == 2023
    assert cleaned["Release Year"].iloc[1] == 2021
    assert pd.isna(cleaned["Release Year"].iloc[2])


def test_median_fill_for_nans():
    """NaNs in numeric columns should be imputed using column median."""
    raw = pd.DataFrame({
        "Track": ["Track 1", "Track 2", "Track 3"],
        "Artist": ["Artist 1", "Artist 2", "Artist 3"],
        "Spotify Popularity": [10.0, np.nan, 30.0],
    })
    cleaned = clean_data(raw)
    assert cleaned["Spotify Popularity"].iloc[1] == 20.0


def test_all_null_row_dropping():
    """Rows that are entirely null must be dropped from the dataset."""
    raw = pd.DataFrame({
        "Track": ["Track 1", None, "Track 2"],
        "Artist": ["Artist 1", None, "Artist 2"],
        "Spotify Streams": [100, None, 200],
    })
    raw.loc[1] = None  # Ensure row 1 is completely NaN
    cleaned = clean_data(raw)
    assert len(cleaned) == 2
    assert cleaned["Track"].tolist() == ["Track 1", "Track 2"]


def test_zip_loading(tmp_path: Path):
    """Reading a CSV inside a ZIP archive must succeed."""
    csv_content = (
        "Track,Artist,Spotify Streams\n"
        "Zip Song 1,Zip Artist 1,12345\n"
        "Zip Song 2,Zip Artist 2,67890\n"
    )
    zip_path = tmp_path / "test_spotify.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("spotify_data.csv", csv_content)

    df = _read_csv_from_zip(zip_path)
    assert len(df) == 2
    assert "Track" in df.columns
    assert df["Track"].iloc[0] == "Zip Song 1"


def test_demo_dataframe_cleanable():
    """Demo sample dataframe must pass clean_data without errors and meet expected schema."""
    demo_raw = generate_demo_dataframe()
    assert len(demo_raw) == 16
    assert "Track" in demo_raw.columns
    assert "Artist" in demo_raw.columns

    cleaned = clean_data(demo_raw)
    assert len(cleaned) == 16
    assert "Release Year" in cleaned.columns
    assert cleaned["Release Year"].notna().all()

    missing = validate_required_columns(cleaned)
    assert missing == []

    for feat in AUDIO_FEATURES:
        assert feat in cleaned.columns


def test_validate_required_columns():
    """Validation must identify missing Track or Artist columns."""
    valid_df = pd.DataFrame({"Track": ["A"], "Artist": ["B"]})
    assert validate_required_columns(valid_df) == []

    alt_track_df = pd.DataFrame({"Track Name": ["A"], "Artist": ["B"]})
    assert validate_required_columns(alt_track_df) == []

    missing_artist = pd.DataFrame({"Track": ["A"]})
    assert validate_required_columns(missing_artist) == ["Artist"]

    missing_both = pd.DataFrame({"Other": [1]})
    missing = validate_required_columns(missing_both)
    assert "Artist" in missing
    assert "Track (or Track Name)" in missing


def test_corrupt_upload_handling():
    """Corrupt upload inputs must raise informative ValueErrors."""
    # Corrupt zip bytes
    with pytest.raises(ValueError, match="not a valid ZIP archive"):
        load_uploaded_file(MockUpload("corrupt.zip", b"not-a-zip-stream"))

    # Empty upload
    with pytest.raises(ValueError, match="empty"):
        load_uploaded_file(MockUpload("empty.csv", b""))

    # ZIP with no CSV
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("readme.txt", "No csv here")
    with pytest.raises(ValueError, match="does not contain any CSV"):
        load_uploaded_file(MockUpload("no_csv.zip", buf.getvalue()))

