"""
User clustering with KMeans to classify traveler personas.
"""
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Cluster labels assigned by training (order may vary; map by centroid profile)
TRAVELER_TYPES = ["Backpacker", "Explorer", "Luxury Traveler", "Foodie"]

INTEREST_KEYS = [
    "nature", "cafe", "museum", "food",
    "nightlife", "photography", "adventure",
]

STYLE_MAP = {"budget": 0, "normal": 1, "luxury": 2}


class UserClusterer:
    """KMeans-based user persona classifier."""

    def __init__(self, model=None, scaler=None, label_map=None):
        self.model = model
        self.scaler = scaler
        # Maps cluster id -> traveler type name
        self.label_map = label_map or {0: "Backpacker", 1: "Explorer", 2: "Luxury Traveler", 3: "Foodie"}

    def build_feature_vector(self, interests, budget, num_days, style):
        """Encode user preferences into a numeric feature vector."""
        vec = []
        interest_set = {i.lower().strip() for i in interests}
        for key in INTEREST_KEYS:
            vec.append(1.0 if key in interest_set else 0.0)
        vec.append(float(budget))
        vec.append(float(num_days))
        vec.append(float(STYLE_MAP.get(style.lower(), 1)))
        daily = budget / max(num_days, 1)
        vec.append(daily)
        return np.array(vec).reshape(1, -1)

    def predict_persona(self, interests, budget, num_days, style):
        """Predict traveler persona from user inputs."""
        if self.model is None or self.scaler is None:
            return self._rule_based_persona(interests, budget, num_days, style)

        features = self.build_feature_vector(interests, budget, num_days, style)
        scaled = self.scaler.transform(features)
        cluster_id = int(self.model.predict(scaled)[0])

        return self.label_map.get(cluster_id, TRAVELER_TYPES[cluster_id % 4])

    @staticmethod
    def _rule_based_persona(interests, budget, num_days, style):
        """Fallback heuristic when ML model is not loaded."""
        style = style.lower()
        daily = budget / max(num_days, 1)
        interest_set = {i.lower() for i in interests}

        if style == "luxury" or daily > 2_000_000:
            return "luxury_traveler"
        if "food" in interest_set and len(interest_set) <= 3:
            return "foodie"
        if style == "budget" or daily < 500_000:
            return "backpacker"
        return "explorer"

    @staticmethod
    def train_synthetic_kmeans(n_samples=500, random_state=42):
        """
        Train KMeans on synthetic user profiles for notebook and init script.
        Returns model, scaler, label_map.
        """
        rng = np.random.default_rng(random_state)
        X = []
        profiles = []

        for _ in range(n_samples):
            interests = rng.choice(INTEREST_KEYS, size=rng.integers(2, 6), replace=False)
            style = rng.choice(["budget", "normal", "luxury"])
            days = int(rng.integers(2, 8))
            if style == "budget":
                budget = float(rng.integers(2_000_000, 8_000_000))
            elif style == "luxury":
                budget = float(rng.integers(15_000_000, 50_000_000))
            else:
                budget = float(rng.integers(5_000_000, 20_000_000))

            vec = []
            for key in INTEREST_KEYS:
                vec.append(1.0 if key in interests else 0.0)
            vec.extend([budget, days, float(STYLE_MAP[style]), budget / days])
            X.append(vec)
            profiles.append((interests, budget, days, style))

        X = np.array(X)
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        kmeans = KMeans(n_clusters=4, random_state=random_state, n_init=10)
        labels = kmeans.fit_predict(X_scaled)

        # Assign persona labels by cluster centroid characteristics
        label_map = {}
        for cid in range(4):
            mask = labels == cid
            cluster = X[mask]

            avg_daily_budget = cluster[:, 10].mean()  # daily_budget
            food_score = cluster[:, 3].mean()
            luxury_score = (cluster[:, 9] == 2).mean()

            if luxury_score > 0.7 or avg_daily_budget > 2_500_000:
                label_map[cid] = "luxury_traveler"
            elif food_score > 0.5:
                label_map[cid] = "foodie"
            elif avg_daily_budget < 700_000:
                label_map[cid] = "backpacker"
            else:
                label_map[cid] = "explorer"
        return kmeans, scaler, label_map
