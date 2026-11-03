# 90-Second Demo Video Script

> **Note:** This document is a production script for demonstrating the Spotify Multi-Platform Analytics Dashboard. It outlines camera timing, audio narration, and on-screen interactions.

---

## Video Specifications
- **Target Duration:** 90 seconds (1 minute, 30 seconds)
- **Resolution:** 1080p (1920x1080) / 60fps
- **Format:** Screencast with voiceover audio

---

## Storyboard & Timing

### Scene 1: Introduction & Zero-Download Onboarding (0:00 – 0:15)
- **Visual:** Browser opens to the dashboard at `http://localhost:8501`. The landing screen shows "Dataset Not Found" with clean instructions and the prominent **"Load demo sample"** button.
- **Action:** Cursor moves to click the **"Load demo sample"** button.
- **Audio (Voiceover):**
  > *"Welcome to the Spotify Multi-Platform Analytics Dashboard. Whether you have the full Kaggle dataset or want to test the application immediately with zero setup, you can launch straight into Demo Mode in a single click."*

---

### Scene 2: High-Level KPIs & Interactive Filtering (0:15 – 0:30)
- **Visual:** Dashboard populates instantly with dark Spotify styling. Metric cards display: Total Tracks (16), Total Streams (43.5M), Average Popularity (62.0), and Unique Artists (4). Persistent demo banner appears at the top.
- **Action:** Open the sidebar, adjust the Release Year slider from `2021–2024` to `2022–2024`, showing track count update reactively to 12.
- **Audio (Voiceover):**
  > *"All metrics are computed on the fly through vectorized Pandas transformations. The KPI cards summarize total catalog stream volume, mean popularity, and artist diversity. The sidebar filters let you slice by artist or release year with instant reactive updates."*

---

### Scene 3: Head-to-Head Artist Analytics (0:30 – 0:48)
- **Visual:** Scroll down to **Artist Analytics**. The Artist Performance Table lists tracks, total streams, and playlist reach.
- **Action:** In the "Artist Head-to-Head Comparison", pick **Demo Artist A** and **Demo Artist B**. The grouped bar chart animates, showing relative percentages across streams, reach, popularity, and track counts.
- **Audio (Voiceover):**
  > *"In the Artist Analytics section, we compare artists head-to-head. Our normalized multi-metric chart scales different metrics like streams and popularity onto a standard 0-to-100 baseline, making cross-dimensional artist comparisons intuitive and direct."*

---

### Scene 4: Cross-Platform Synergy & Market Insights (0:48 – 1:08)
- **Visual:** Scroll to **Cross-Platform & Market Insights**.
- **Action:** Highlight the **Strongest Platform Predictor** card showing Pearson correlation coefficient ($r = +0.35$), then point to the **Playlist Efficiency** ranking and **Release Year Trajectory** chart.
- **Audio (Voiceover):**
  > *"Moving beyond Spotify alone, our analytical engine automatically detects the strongest external streaming predictor—revealing which platform's metrics correlate most tightly with Spotify streams. We also compute playlist efficiency, measuring streams generated per playlist placement."*

---

### Scene 5: Feature Correlation Heatmap & Data Export (1:08 – 1:22)
- **Visual:** Scroll to the **Feature Correlation Heatmap** and sidebar export button.
- **Action:** Hover over the correlation matrix showing pairwise Pearson $r$ values. In the sidebar, click **"Download filtered data (CSV)"**; the file downloads immediately to the browser.
- **Audio (Voiceover):**
  > *"The lower-triangle correlation matrix lets you explore deep pairwise interactions across all platforms. And when you've sliced the data to your target cohort, one click exports the exact filtered subset as a clean CSV."*

---

### Scene 6: Outro & Next Steps (1:22 – 1:30)
- **Visual:** Return to the top of the dashboard. Show GitHub repo link and deploy instructions.
- **Action:** Cursor hovers over the GitHub badge / footer.
- **Audio (Voiceover):**
  > *"Ready to deploy on Streamlit Community Cloud with zero configuration. Clone the repo, run pytest, or explore the live dashboard today. Thanks for watching!"*
