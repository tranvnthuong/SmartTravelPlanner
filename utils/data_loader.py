"""
Data loading and caching for attractions dataset.
"""
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "datasets" / "attractions.csv"

_attractions_cache = None


def load_attractions(force_reload=False):
    """Load attractions CSV into a pandas DataFrame with caching."""
    global _attractions_cache
    if _attractions_cache is None or force_reload:
        if not DATASET_PATH.exists():
            raise FileNotFoundError(
                f"Dataset not found at {DATASET_PATH}. Run scripts/generate_dataset.py first."
            )
        df = pd.read_csv(DATASET_PATH)
        df["category"] = df["category"].str.lower().str.strip()
        df["city"] = df["city"].str.strip()
        _attractions_cache = df
    return _attractions_cache.copy()


def get_city_attractions(city, df=None):
    """Filter attractions by city name (case-insensitive partial match)."""
    if df is None:
        df = load_attractions()
    city_lower = city.strip().lower()
    mask = df["city"].str.lower().str.contains(city_lower, na=False)
    return df[mask].copy()
