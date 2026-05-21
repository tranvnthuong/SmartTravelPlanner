"""
Budget prediction using RandomForestRegressor.
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

from utils.clustering import INTEREST_KEYS, STYLE_MAP


class BudgetPredictor:
    """Predict total trip cost from user preferences and planned attractions."""

    def __init__(self, model=None):
        self.model = model
        self.feature_names = None

    def _build_features_from_user(self, interests, budget, num_days, style, num_places=9):
        """Feature vector for inference aligned with training."""
        vec = []
        interest_set = {i.lower().strip() for i in interests}
        for key in INTEREST_KEYS:
            vec.append(1.0 if key in interest_set else 0.0)
        vec.append(float(num_days))
        vec.append(float(STYLE_MAP.get(style.lower(), 1)))
        vec.append(float(num_places))
        vec.append(float(budget))  # user stated budget as anchor feature
        return np.array(vec).reshape(1, -1)

    def predict(self, interests, budget, num_days, style, planned_cost=0, num_places=9):
        """Predict total trip cost in VND."""
        if self.model is None:
            # Heuristic: base daily spend by style + planned attraction costs
            daily_base = {"budget": 800_000, "normal": 1_500_000, "luxury": 3_500_000}
            base = daily_base.get(style.lower(), 1_500_000) * num_days
            return float(planned_cost * 0.7 + base * 0.3)

        X = self._build_features_from_user(interests, budget, num_days, style, num_places)
        cols = [f"int_{k}" for k in INTEREST_KEYS] + [
            "num_days", "style", "num_places", "stated_budget"
        ]
        X_df = pd.DataFrame(X, columns=cols)
        pred = float(self.model.predict(X_df)[0])
        # Blend with actual planned costs for realism
        if planned_cost > 0:
            pred = 0.6 * pred + 0.4 * planned_cost
        return max(pred, 0)

    @staticmethod
    def train_from_attractions(attractions_df, n_samples=800, random_state=42):
        """
        Train RandomForest on synthetic trips derived from attractions statistics.
        """
        rng = np.random.default_rng(random_state)
        rows = []

        for _ in range(n_samples):
            interests = list(rng.choice(INTEREST_KEYS, size=rng.integers(2, 6), replace=False))
            style = rng.choice(["budget", "normal", "luxury"])
            days = int(rng.integers(1, 8))
            stated_budget = float(rng.integers(3_000_000, 40_000_000))
            city_df = attractions_df.sample(min(30, len(attractions_df)))
            sample_places = city_df.sample(min(days * 3, len(city_df)))
            planned = sample_places["estimated_cost"].sum()
            transport = days * rng.integers(100_000, 400_000)
            lodging = days * {"budget": 400_000, "normal": 900_000, "luxury": 2_500_000}[style]
            food_extra = days * rng.integers(150_000, 500_000)
            actual_total = planned + transport + lodging + food_extra

            vec = []
            for key in INTEREST_KEYS:
                vec.append(1.0 if key in interests else 0.0)
            vec.extend([days, float(STYLE_MAP[style]), len(sample_places), stated_budget])
            vec.append(actual_total)
            rows.append(vec)

        cols = [f"int_{k}" for k in INTEREST_KEYS] + [
            "num_days", "style", "num_places", "stated_budget", "total_cost"
        ]
        data = pd.DataFrame(rows, columns=cols)
        X = data.drop(columns=["total_cost"])
        y = data["total_cost"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=random_state
        )
        model = RandomForestRegressor(
            n_estimators=100, max_depth=12, random_state=random_state, n_jobs=-1
        )
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        metrics = {
            "mae": mean_absolute_error(y_test, preds),
            "r2": r2_score(y_test, preds),
        }
        return model, metrics
