"""
Load or train ML models (joblib pickle).
"""
from pathlib import Path

import joblib

from utils.clustering import UserClusterer
from utils.data_loader import load_attractions
from utils.predictor import BudgetPredictor

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "trained_models.pkl"

_models_cache = None


def ensure_models():
    """Train and persist models if pickle does not exist."""
    if MODEL_PATH.exists():
        return
    from scripts.train_models import train_and_save

    train_and_save()


def load_models(force_reload=False):
    """Load KMeans, scaler, RandomForest from pickle."""
    global _models_cache
    if _models_cache is not None and not force_reload:
        return _models_cache

    ensure_models()
    bundle = joblib.load(MODEL_PATH)
    _models_cache = {
        "kmeans": bundle["kmeans"],
        "scaler": bundle["scaler"],
        "label_map": bundle["label_map"],
        "budget_model": bundle["budget_model"],
        "metrics": bundle.get("metrics", {}),
    }
    return _models_cache


def get_clusterer():
    m = load_models()
    return UserClusterer(m["kmeans"], m["scaler"], m["label_map"])


def get_budget_predictor():
    m = load_models()
    return BudgetPredictor(m["budget_model"])
