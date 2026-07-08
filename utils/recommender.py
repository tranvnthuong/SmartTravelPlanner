"""
Content-based recommendation using TF-IDF and cosine similarity.
Combined with weighted scoring formula for personalized ranking.
"""
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Interest keys from form map to dataset categories/tags
INTEREST_TO_CATEGORIES = {
    "nature": ["nature", "beach"],
    "cafe": ["cafe"],
    "museum": ["museum"],
    "food": ["food"],
    "nightlife": ["nightlife"],
    "photography": ["nature", "beach", "museum"],
    "adventure": ["adventure", "nature"],
}

STYLE_BUDGET_MULTIPLIER = {
    "budget": 0.6,
    "normal": 1.0,
    "luxury": 1.8,
}


class AttractionRecommender:
    """Content-based recommender with TF-IDF and composite scoring."""

    def __init__(self, attractions_df):
        # Reset index so TF-IDF row positions align with DataFrame rows
        self.df = attractions_df.copy().reset_index(drop=True)
        self._build_tfidf()

    def _build_tfidf(self):
        """Build TF-IDF matrix from category, tags, and description."""
        self.df["text_features"] = (
            self.df["category"].astype(str)
            + " "
            + self.df["tags"].astype(str)
            + " "
            + self.df["description"].astype(str)
        )
        self.vectorizer = TfidfVectorizer(stop_words="english", max_features=500)
        self.tfidf_matrix = self.vectorizer.fit_transform(self.df["text_features"])

    def _user_profile_text(self, interests):
        """Convert user interests into a text profile for similarity."""
        cats = []
        for interest in interests:
            key = interest.lower().strip()
            cats.extend(INTEREST_TO_CATEGORIES.get(key, [key]))
        return " ".join(set(cats))

    def _interest_match(self, row, interests):
        """Score 0-1 based on category/tag overlap with user interests."""
        if not interests:
            return 0.5
        user_cats = set()
        for interest in interests:
            key = interest.lower().strip()
            user_cats.update(INTEREST_TO_CATEGORIES.get(key, [key]))
        row_cat = str(row["category"]).lower()
        row_tags = set(str(row["tags"]).lower().replace(",", " ").split())
        match = 0
        if row_cat in user_cats:
            match += 0.7
        overlap = len(user_cats & row_tags) / max(len(user_cats), 1)
        match += 0.3 * min(overlap, 1.0)
        return min(match, 1.0)

    def _rating_score(self, rating):
        """Normalize rating to 0-1 (assuming max 5)."""
        return float(rating) / 5.0

    def _budget_fit(self, cost, daily_budget, style):
        """Score how well attraction cost fits remaining daily budget."""
        multiplier = STYLE_BUDGET_MULTIPLIER.get(style.lower(), 1.0)
        adjusted_budget = daily_budget * multiplier
        if adjusted_budget <= 0:
            return 0.5
        ratio = cost / adjusted_budget
        if ratio <= 0.3:
            return 1.0
        if ratio <= 0.6:
            return 0.8
        if ratio <= 1.0:
            return 0.5
        return max(0.1, 1.0 - (ratio - 1.0))

    def compute_scores(
        self,
        interests,
        total_budget,
        num_days,
        style="normal",
        city_filter=None,
    ):
        """
        Compute composite recommendation score for each attraction.

        score = 0.4 * interest_match + 0.3 * rating_score + 0.2 * budget_fit + 0.1 * popularity
        """
        df = self.df
        if city_filter:
            df = df[df["city"].str.lower().str.contains(city_filter.lower(), na=False)]

        if df.empty:
            return pd.DataFrame()

        daily_budget = total_budget / max(num_days, 1)
        profile = self._user_profile_text(interests)
        profile_vec = self.vectorizer.transform([profile])
        indices = df.index.tolist()
        sub_matrix = self.tfidf_matrix[indices]
        cos_scores = cosine_similarity(profile_vec, sub_matrix).flatten()

        scores = []
        for i, (idx, row) in enumerate(df.iterrows()):
            interest_m = self._interest_match(row, interests)
            # Blend TF-IDF cosine with rule-based interest match
            interest_m = 0.6 * interest_m + 0.4 * float(cos_scores[i])
            rating_s = self._rating_score(row["rating"])
            budget_f = self._budget_fit(row["estimated_cost"], daily_budget, style)
            pop = float(row["popularity"])
            composite = (
                0.4 * interest_m
                + 0.3 * rating_s
                + 0.2 * budget_f
                + 0.1 * pop
            )
            scores.append(composite)

        result = df.copy()
        result["recommendation_score"] = scores
        result = result.sort_values("recommendation_score", ascending=False)
        return result

    def recommend(self, interests, total_budget, num_days, style, city, top_n=30):
        """Return top-N recommended attractions for a city."""
        scored = self.compute_scores(interests, total_budget, num_days, style, city)
        return scored.head(top_n)

    def recommend(self, interests, total_budget, num_days, style, city, top_n=30, regenerate_seed=0):
        """Return top-N recommended attractions for a city."""
        scored = self.compute_scores(interests, total_budget, num_days, style, city)

        if scored.empty:
            return scored

        if regenerate_seed:
            pool_size = min(len(scored), max(top_n * 2, 30))

            return (
                scored
                .head(pool_size)
                .sample(n=min(top_n, pool_size), random_state=int(regenerate_seed))
                .sort_values("recommendation_score", ascending=False)
                .reset_index(drop=True)
            )

        return scored.head(top_n).reset_index(drop=True)
