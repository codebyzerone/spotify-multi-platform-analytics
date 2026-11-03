# Upgrade Plan — spotify-multi-platform-analytics

## Audit Findings

### What exists and works (conceptually)
- **app.py** (660 lines): monolith with page config, CSS, KPI row, artist analytics
  (performance table, top-N chart, artist comparison, artist insights), correlation
  heatmap, distribution explorer (histogram/violin + top-N rankings), sidebar filters
  (artist, release year), and a `main()` that loads from `data/spotify_2024.csv|.zip`
  or file upload.
- **data_loader.py** (169 lines): `load_data()`, `load_uploaded_file()`, `clean_data()`
  with column constants, audio feature normalisation, numeric coercion, date parsing,
  all-null row dropping, median fill. Defines `PLATFORM_METRICS`, `AUDIO_FEATURES`,
  `ALL_PLATFORM_COLS`, `NUMERIC_COLS`, `ID_COLS`.
- **.streamlit/config.toml**: dark theme already configured (primaryColor=#1ed760, dark
  backgrounds), maxUploadSize=200.
- **.gitignore**: correctly excludes venv, `__pycache__`, data CSV/ZIP.
- **requirements.txt**: unpinned (`streamlit>=1.30`, `pandas>=2.0`, `numpy>=1.24`,
  `plotly>=5.18`).
- **spotify_eda.ipynb**: standalone EDA notebook (not used by the dashboard).
- **environment.py**: single-line pip install — unused artifact.
- **implementation_plan.md**: original build plan — historical reference.

### What is broken
1. **Dead end on fresh clone**: No `data/spotify_2024.csv`, no demo mode. User sees
   "Dataset Not Found" with no way forward except downloading from Kaggle.
2. **Broken README images**: Links to `images/dashboard.png` etc. but `images/` folder
   does not exist. There is an `images.py/` directory (with one unrelated PNG) that is
   untracked and appears to be mistakenly named.
3. **No tests**: zero pytest files, no CI.
4. **No demo data**: no `load_demo_sample()` function exists anywhere.
5. **requirements.txt unpinned**: fine for dev, but risky for Streamlit Cloud deploy.
6. **README tech stack table lists Matplotlib/Seaborn**: the app only uses Plotly.
7. **No error handling**: `load_uploaded_file()` does not catch `zipfile.BadZipFile`,
   corrupt CSVs, or missing required columns.
8. **app.py is a monolith**: 660 lines, all rendering in one file. Harder to maintain
   and test.
9. **No "Track Score" column**: referenced in `_AGG_SPEC` but may not exist in the
   Kaggle dataset. Handled gracefully (column check), but the README mentions it.

### What is NOT broken (do not rebuild)
- Artist comparison (normalised grouped bar) — exists and works correctly.
- Artist insights (highest streamed, avg tracks/artist, best-of, #1 vs #2 gap) — exists
  and is data-driven.
- Correlation heatmap with multiselect — exists and works.
- Distribution explorer with histogram/violin tabs — exists and works.
- Top-N rankings — exists and works.
- Sidebar filters — correct mask logic.
- `clean_data()` pipeline — thorough and vectorised.

---

## Phase Plan

### Phase 1 — First-run experience + demo mode
**Changes:**
- Add `generate_demo_dataframe()` to `data_loader.py` — returns a 16-row DataFrame with
  generic track/artist names and realistic-looking (but clearly fake) numbers covering
  all columns that `clean_data()` expects.
- Add demo-mode toggle in `app.py main()`: session-state flag, "Load demo sample"
  button, persistent banner, one-click replacement via upload.
- Fix README: remove all broken `images/*.png` links, leave a placeholder Screenshots
  section.

**Risks:** Demo data must pass through `clean_data()` without error and produce
meaningful charts (enough variance, multiple artists, multiple years).

**Files:** `app.py`, `data_loader.py`, `README.md`

### Phase 2 — Deploy-ready + robustness
**Changes:**
- Verify `.streamlit/config.toml` (already exists, looks good).
- Add deploy instructions to README.
- Document tested package versions in `requirements.txt` (pin to what is installed:
  streamlit==1.55.0, pandas==2.2.2, numpy==1.26.4, plotly==6.6.0, plus pytest>=7.0 as
  a dev dependency).
- Harden `data_loader.py`: catch `BadZipFile`, `ParserError`, validate required columns
  (Track/Artist), add user-facing error messages.
- Add empty-filter-state messages in app.py.

**Files:** `data_loader.py`, `app.py`, `requirements.txt`, `README.md`,
`.streamlit/config.toml`

### Phase 3 — Refactor + tests
**Changes:**
- Extract app.py into thin entry point + component modules:
  - `components/kpis.py` — `render_kpis()`
  - `components/artist.py` — `render_artist_analytics()` + helpers
  - `components/correlation.py` — `render_correlation_heatmap()`
  - `components/distributions.py` — `render_distributions()`
  - `components/insights.py` — enhanced insights (moved from artist section)
  - `utils/formatting.py` — `fmt_big()`, `get_track_col()`
  - `utils/theme.py` — `PLOTLY_LAYOUT`, `SPOTIFY_COLORS`, CSS string
  - `utils/charts.py` — `horizontal_bar()`
- `app.py` becomes: imports → page config → CSS → load → clean → sidebar → render.
- Add `tests/test_data_loader.py` with pytest.
- Add `.github/workflows/ci.yml`.

**Risks:** Must not change visible behaviour. Incremental extraction + run checks.

**Files:** `app.py`, new `components/`, new `utils/`, new `tests/`, new `.github/`

### Phase 4 — Analytics depth
**Changes:**
- Platform efficiency: streams per playlist, reach per playlist count.
- Year-over-year trend: streams/popularity grouped by Release Year.
- Cross-platform correlation insight: which platform metric has the highest Pearson r
  with Spotify Streams.
- "Download filtered data as CSV" button.
- All insights computed, with units, handling missing columns gracefully.

**Files:** `components/insights.py`, `components/artist.py`, `app.py`

### Phase 5 — Polish, docs, screenshots
**Changes:**
- Full README rewrite.
- Capture real screenshots from demo mode, save to `images/`.
- Write `docs/demo-script.md` (video script only, no actual video).

**Files:** `README.md`, `images/`, `docs/demo-script.md`

---

## What will NOT change
- **spotify_eda.ipynb**: standalone notebook, out of scope.
- **environment.py**: historical artifact, will not delete but will not modify.
- **implementation_plan.md**: historical, will not modify.
- **walkthrough.spotifyEDA**: unknown format, will not touch.
- **images.py/**: untracked, appears to be a naming mistake. Will not touch.
- **No new dependencies** beyond pytest (dev-only).

