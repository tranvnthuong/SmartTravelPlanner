"""
Train KMeans and RandomForest models and save to models/trained_models.pkl.
Run: python scripts/train_models.py
"""
import sys
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from utils.clustering import UserClusterer
from utils.data_loader import load_attractions
from utils.predictor import BudgetPredictor


def train_and_save():
    """Train all models and persist with joblib."""
    attractions = load_attractions()
    kmeans, scaler, label_map = UserClusterer.train_synthetic_kmeans()
    budget_model, metrics = BudgetPredictor.train_from_attractions(attractions)

    bundle = {
        "kmeans": kmeans,
        "scaler": scaler,
        "label_map": label_map,
        "budget_model": budget_model,
        "metrics": metrics,
    }
    out = ROOT / "models" / "trained_models.pkl"
    out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, out)
    print(f"Budget model metrics: {metrics}")
    print(f"Cluster label map: {label_map}")
    print(f"Models saved to {out}")
    print("Training complete.")
    return bundle


if __name__ == "__main__":
    train_and_save()
