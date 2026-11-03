"""
scripts/capture_screenshots.py — Capture real screenshots of the live Streamlit dashboard.

Uses Chrome in headless mode against a live local Streamlit instance with demo data.
"""

from __future__ import annotations

import os
import subprocess
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = REPO_ROOT / "images"
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
STREAMLIT_EXE = str(REPO_ROOT / ".venv" / "Scripts" / "streamlit.exe")


def wait_for_server(url: str, timeout: int = 30) -> bool:
    """Poll health endpoint until Streamlit is ready."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(1)
    return False


def capture(url: str, filename: str, width: int = 1400, height: int = 1200, budget: int = 15000) -> None:
    """Capture a screenshot using headless Chrome."""
    out_file = IMAGES_DIR / filename
    time.sleep(2)
    cmd = (
        f'cmd.exe /c "start /wait "" "{CHROME_PATH}" '
        f'--headless=new --disable-gpu --hide-scrollbars '
        f'--virtual-time-budget={budget} '
        f'--window-size={width},{height} '
        f'--screenshot="{out_file}" "{url}""'
    )
    subprocess.run(cmd, shell=True, check=True)
    size = out_file.stat().st_size if out_file.exists() else 0
    print(f"Captured {filename} ({width}x{height}) -> {size:,} bytes")


def main() -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    print("Starting Streamlit application...")
    server = subprocess.Popen(
        [
            STREAMLIT_EXE,
            "run",
            str(REPO_ROOT / "app.py"),
            "--server.headless=true",
            "--server.port=8501",
            "--browser.gatherUsageStats=false",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    try:
        health_url = "http://localhost:8501/_stcore/health"
        if not wait_for_server(health_url, timeout=25):
            raise RuntimeError("Streamlit failed to start within timeout.")
        print("Streamlit server is healthy.")

        # Warm up the server
        time.sleep(4)

        # 1. First-run landing page (zero downloads / missing dataset)
        capture("http://localhost:8501", "landing_page.png", width=1400, height=950, budget=16000)

        # 2. Main Dashboard Overview with Demo sample
        capture("http://localhost:8501/?demo=true", "dashboard_overview.png", width=1400, height=1300, budget=16000)

        # 3. Artist Analytics section
        capture("http://localhost:8501/?demo=true", "artist_analytics.png", width=1400, height=1800, budget=16000)

        # 4. Cross-Platform Insights & Correlation Heatmap
        capture("http://localhost:8501/?demo=true", "correlation_heatmap.png", width=1400, height=2800, budget=16000)

        # 5. Full Dashboard View (Header down to Distribution Explorer & Footer)
        capture("http://localhost:8501/?demo=true", "distribution_explorer.png", width=1400, height=4400, budget=18000)

        print("All screenshots successfully captured!")
    finally:
        server.terminate()
        server.wait()
        print("Streamlit server stopped.")


if __name__ == "__main__":
    main()
