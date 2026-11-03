# 🎵 Spotify Multi-Platform Analytics Dashboard

An interactive analytics dashboard built with **Python**, **Streamlit**, and **Plotly** to explore music performance across multiple streaming platforms using the **Spotify Most Streamed Songs 2024** dataset.

Instead of displaying static charts, the dashboard allows users to upload the dataset, filter artists, compare performance metrics, analyze correlations, and discover insights through interactive visualizations.

---

## 📸 Screenshots

> Screenshots will be added after the UI polish phase. Run the app with demo data to see the dashboard in action.

---

## ✨ Features

### 🎵 Demo Mode
- Try the dashboard instantly — no downloads needed.
- Click **"Load demo sample"** to explore with 16 synthetic tracks.
- Demo data is clearly labelled and can be replaced by uploading the real dataset.

### 📂 Dataset Upload
- Upload the **Spotify Most Streamed Songs 2024** dataset (CSV or ZIP).
- Automatically loads and preprocesses the data.

### 🎤 Artist Analytics
- Analyze individual artist performance.
- View:
  - Total Tracks
  - Total Streams
  - Average Track Score
  - Average Popularity
  - Playlist Reach
- Compare artists using interactive tables and charts.

### 📊 Correlation Heatmap
Explore relationships between numerical features such as:
- Track Score
- Spotify Streams
- Playlist Reach
- Playlist Count
- Popularity

This helps identify which metrics are strongly related.

### 📈 Distribution Explorer
Visualize how different ranking metrics are distributed across the dataset.

Supports:
- Histograms
- Violin plots
- Top-N Rankings

### 💡 Artist Insights
Automatically summarizes key observations, including:
- Highest streamed artist
- Average track performance
- Popularity trends
- Playlist reach statistics

### 🎛 Interactive Filters
Filter the dashboard by:
- Artist
- Release Year

---

## 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core programming language |
| Streamlit | Interactive web application |
| Pandas | Data cleaning & analysis |
| Plotly Express | Interactive visualizations |
| NumPy | Numerical operations |

---

## 📂 Project Structure

```text
spotify-multi-platform-analytics/
├── app.py                  # Streamlit application
├── data_loader.py          # Dataset loading & preprocessing
├── data/                   # Dataset location (CSV not committed)
├── requirements.txt
├── README.md
├── LICENSE
└── .streamlit/
    └── config.toml
```

---

## 🚀 Getting Started

### Clone the repository

```bash
git clone https://github.com/codebyzerone/spotify-multi-platform-analytics.git
cd spotify-multi-platform-analytics
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the application

```bash
streamlit run app.py
```

On first run (without the Kaggle CSV), click **"Load demo sample"** to explore the dashboard with synthetic data.

---

## 📊 Dataset

This project uses the **Spotify Most Streamed Spotify Songs 2024** dataset from Kaggle.

**The dataset is NOT included in this repository** because its Kaggle license does not permit redistribution. To use real data:

1. Visit [Kaggle – Most Streamed Spotify Songs 2024](https://www.kaggle.com/datasets/nelgiriyewithana/most-streamed-spotify-songs-2024)
2. Download the CSV file
3. Rename it to `spotify_2024.csv`
4. Place it in the `data/` folder
5. Refresh the dashboard

---

## 📚 What I Learned

While building this project I gained practical experience with:

- Data preprocessing using Pandas
- Interactive dashboard development with Streamlit
- Data visualization using Plotly
- Statistical analysis using correlation matrices
- Aggregation and ranking techniques
- Building reusable and modular Python code
- Designing user-friendly analytical dashboards

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 👨‍💻 Author

**Manodip Bhattacharjee**

Computer Science Engineering Student

GitHub: https://github.com/codebyzerone

LinkedIn: www.linkedin.com/in/manodip-bhattacharjee-651b09360
