"""
Greedy route optimization and diversity-aware itinerary builder.
"""
import math

import pandas as pd

# Max distance (km) between consecutive stops — avoids far-apart pairs
MAX_LEG_KM = 12.0
SLOTS_PER_DAY = ["Morning", "Afternoon", "Evening"]


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance between two coordinates in kilometers."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dlon / 2) ** 2
    )
    return 2 * r * math.asin(math.sqrt(min(a, 1.0)))


def attraction_to_dict(row):
    """Serialize a pandas row to API/template-friendly dict."""
    return {
        "id": int(row["id"]),
        "name": str(row["name"]),
        "category": str(row["category"]),
        "rating": float(row["rating"]),
        "estimated_cost": int(row["estimated_cost"]),
        "duration_hours": float(row["duration_hours"]),
        "description": str(row["description"]),
        "latitude": float(row["latitude"]),
        "longitude": float(row["longitude"]),
        "recommendation_score": float(row.get("recommendation_score", 0)),
    }


class ItineraryOptimizer:
    """
    Builds multi-day itineraries with greedy routing and category diversity.
    """

    def __init__(self, max_leg_km=MAX_LEG_KM):
        self.max_leg_km = max_leg_km

    def _greedy_select(self, candidates, start_lat, start_lon, count, last_category=None):
        """Pick `count` attractions using greedy nearest-neighbor with diversity."""
        selected = []
        remaining = candidates.copy()
        cur_lat, cur_lon = start_lat, start_lon
        prev_cat = last_category

        for _ in range(count):
            if remaining.empty:
                break
            best_idx = None
            best_score = -1.0

            for idx, row in remaining.iterrows():
                dist = haversine_km(cur_lat, cur_lon, row["latitude"], row["longitude"])
                if dist > self.max_leg_km and len(selected) > 0:
                    continue
                # Higher recommendation score, penalize distance and repeat category
                rec = float(row.get("recommendation_score", 0.5))
                dist_penalty = min(dist / self.max_leg_km, 1.0) * 0.25
                diversity_bonus = 0.15 if prev_cat and row["category"] != prev_cat else 0.0
                repeat_penalty = 0.3 if prev_cat and row["category"] == prev_cat else 0.0
                score = rec - dist_penalty + diversity_bonus - repeat_penalty

                if score > best_score:
                    best_score = score
                    best_idx = idx

            if best_idx is None:
                # Relax distance constraint — pick highest score
                best_idx = remaining["recommendation_score"].idxmax()

            chosen = remaining.loc[best_idx]
            selected.append(chosen)
            prev_cat = chosen["category"]
            cur_lat, cur_lon = chosen["latitude"], chosen["longitude"]
            remaining = remaining.drop(best_idx)

        return selected, prev_cat

    def build_itinerary(
        self,
        recommended_df,
        num_days,
        city_center_lat,
        city_center_lon,
        regenerate_seed=0,
    ):
        """
        Build itinerary: each day has Morning, Afternoon, Evening slots.
        `regenerate_seed` shuffles candidate order for variety on re-roll.
        """
        df = recommended_df.copy()
        if regenerate_seed:
            df = df.sample(frac=1, random_state=regenerate_seed).reset_index(drop=True)

        # Need up to 3 * num_days attractions
        needed = min(len(df), num_days * 3)
        pool = df.head(max(needed * 2, 15))

        itinerary = []
        last_cat = None
        cur_lat, cur_lon = city_center_lat, city_center_lon

        for day in range(1, num_days + 1):
            day_plan = {"day": day, "slots": []}
            day_selected = []

            for slot in SLOTS_PER_DAY:
                slot_candidates = pool[~pool["id"].isin([r["id"] for r in day_selected])]
                if slot_candidates.empty:
                    slot_candidates = pool

                picks, last_cat = self._greedy_select(
                    slot_candidates,
                    cur_lat,
                    cur_lon,
                    count=1,
                    last_category=last_cat,
                )
                if not picks:
                    continue
                row = picks[0]
                place = attraction_to_dict(row)
                day_selected.append(place)
                day_plan["slots"].append({"period": slot, "place": place})
                cur_lat, cur_lon = row["latitude"], row["longitude"]
                pool = pool[pool["id"] != row["id"]]

            itinerary.append(day_plan)

        return itinerary


def compute_trip_score(itinerary, budget, predicted_cost, persona):
    """Overall trip quality score 0-100."""
    if not itinerary:
        return 50.0
    total_places = sum(len(d["slots"]) for d in itinerary)
    target_places = len(itinerary) * 3
    completeness = min(total_places / max(target_places, 1), 1.0) * 30

    ratings = []
    categories = set()
    for day in itinerary:
        for slot in day["slots"]:
            ratings.append(slot["place"]["rating"])
            categories.add(slot["place"]["category"])
    avg_rating = (sum(ratings) / len(ratings) / 5.0) * 35 if ratings else 15
    diversity = min(len(categories) / 5.0, 1.0) * 20

    budget_ratio = predicted_cost / max(budget, 1)
    if 0.7 <= budget_ratio <= 1.0:
        budget_fit = 15
    elif budget_ratio < 0.7:
        budget_fit = 12
    else:
        budget_fit = max(0, 15 - (budget_ratio - 1) * 20)

    persona_bonus = {"Explorer": 3, "Foodie": 2, "Luxury Traveler": 2, "Backpacker": 2}.get(
        persona, 0
    )
    return round(min(completeness + avg_rating + diversity + budget_fit + persona_bonus, 100), 1)
