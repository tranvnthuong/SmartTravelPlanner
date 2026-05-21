"""
Generate synthetic attractions dataset for Smart Travel Planner.
Run once: python scripts/generate_dataset.py
"""
import csv
import random
from pathlib import Path

random.seed(42)

CITIES = {
    "Da Lat": (11.9404, 108.4583),
    "Ho Chi Minh": (10.8231, 106.6297),
    "Ha Noi": (21.0285, 105.8542),
    "Da Nang": (16.0544, 108.2022),
    "Nha Trang": (12.2388, 109.1967),
}

CATEGORIES = {
    "cafe": {
        "names": ["Bloom Coffee", "The Married Beans", "La Viet Coffee", "Cong Caphe",
                  "Highlands Corner", "Morning Brew", "Sunrise Café", "Heritage Roastery",
                  "Garden Sip", "Artisan Latte House"],
        "cost_range": (30000, 150000),
        "duration": (0.5, 2),
        "tags": "cafe,relax,photography",
    },
    "nature": {
        "names": ["Pine Forest Trail", "Waterfall Valley", "Sunrise Peak", "Botanical Garden",
                  "Lake View Park", "Eco Trail", "Misty Hills", "Bamboo Grove", "Wildflower Meadow",
                  "Mountain Lookout"],
        "cost_range": (0, 200000),
        "duration": (2, 5),
        "tags": "nature,adventure,photography",
    },
    "museum": {
        "names": ["History Museum", "Fine Arts Gallery", "War Remnants Exhibit", "Ethnology Center",
                  "Contemporary Art Space", "Heritage House", "Science Discovery", "Cultural Pavilion",
                  "Colonial Archive", "Craft Heritage Museum"],
        "cost_range": (20000, 120000),
        "duration": (1.5, 3),
        "tags": "museum,culture,history",
    },
    "food": {
        "names": ["Street Food Alley", "Night Market Bites", "Local Pho House", "Seafood Harbor",
                  "BBQ Garden", "Riverside Dining", "Traditional Kitchen", "Fusion Bistro",
                  "Farm-to-Table", "Dessert Lane"],
        "cost_range": (50000, 400000),
        "duration": (1, 2.5),
        "tags": "food,local,culture",
    },
    "nightlife": {
        "names": ["Sky Lounge Bar", "Rooftop Jazz Club", "Neon District", "Live Music Venue",
                  "Craft Beer Hub", "Night Bazaar", "Dance Floor Central", "Late Night Bistro",
                  "Cocktail Harbor", "Urban Night Walk"],
        "cost_range": (100000, 600000),
        "duration": (2, 4),
        "tags": "nightlife,entertainment,social",
    },
    "beach": {
        "names": ["Golden Sand Beach", "Coral Bay", "Sunset Shore", "Island Hop Point",
                  "Snorkel Cove", "Palm Beach Walk", "Blue Lagoon", "Coastal Promenade",
                  "Surf Spot", "Hidden Cove"],
        "cost_range": (0, 250000),
        "duration": (2, 6),
        "tags": "beach,nature,photography",
    },
    "shopping": {
        "names": ["Central Market", "Night Street Bazaar", "Craft Village", "Fashion District",
                  "Souvenir Lane", "Local Artisan Mall", "Weekend Fair", "Heritage Shop Street",
                  "Modern Plaza", "Handicraft Corner"],
        "cost_range": (0, 500000),
        "duration": (1, 3),
        "tags": "shopping,souvenir,local",
    },
    "adventure": {
        "names": ["Zip Line Park", "Kayak River Tour", "Canyon Trek", "ATV Trail",
                  "Rock Climbing Wall", "Cave Expedition", "Paragliding Point", "Jungle Trek",
                  "Cable Car Adventure", "Off-road Safari"],
        "cost_range": (150000, 800000),
        "duration": (2, 6),
        "tags": "adventure,thrill,nature",
    },
}

DESCRIPTIONS = {
    "cafe": "Cozy café perfect for coffee lovers and relaxed mornings.",
    "nature": "Scenic natural spot ideal for hiking and fresh air experiences.",
    "museum": "Cultural landmark showcasing local history and art collections.",
    "food": "Authentic local cuisine destination loved by food enthusiasts.",
    "nightlife": "Vibrant evening venue with music, drinks, and city atmosphere.",
    "beach": "Beautiful coastal area for swimming, sunbathing, and water activities.",
    "shopping": "Bustling market area for souvenirs, crafts, and local products.",
    "adventure": "Thrilling outdoor activity for adrenaline seekers and explorers.",
}


def jitter_coords(base_lat, base_lon):
    return round(base_lat + random.uniform(-0.08, 0.08), 6), round(
        base_lon + random.uniform(-0.08, 0.08), 6
    )


def generate_attractions(count=120):
    rows = []
    aid = 1
    per_city = count // len(CITIES)
    extra = count % len(CITIES)

    for city_idx, (city, (lat, lon)) in enumerate(CITIES.items()):
        n = per_city + (1 if city_idx < extra else 0)
        cats = list(CATEGORIES.keys())
        for _ in range(n):
            cat = random.choice(cats)
            info = CATEGORIES[cat]
            name_base = random.choice(info["names"])
            suffix = random.choice(["", " Central", " Premium", " Old Town", " Riverside"])
            name = f"{name_base}{suffix} - {city.split()[0]}"
            cost = random.randint(*info["cost_range"])
            duration = round(random.uniform(*info["duration"]), 1)
            rating = round(random.uniform(3.5, 5.0), 1)
            popularity = round(random.uniform(0.3, 1.0), 2)
            plat, plon = jitter_coords(lat, lon)
            rows.append({
                "id": aid,
                "name": name,
                "city": city,
                "category": cat,
                "rating": rating,
                "estimated_cost": cost,
                "duration_hours": duration,
                "popularity": popularity,
                "tags": info["tags"],
                "description": DESCRIPTIONS[cat],
                "latitude": plat,
                "longitude": plon,
            })
            aid += 1
    return rows


def main():
    out = Path(__file__).resolve().parent.parent / "datasets" / "attractions.csv"
    rows = generate_attractions(120)
    fieldnames = [
        "id", "name", "city", "category", "rating", "estimated_cost",
        "duration_hours", "popularity", "tags", "description", "latitude", "longitude",
    ]
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Generated {len(rows)} attractions -> {out}")


if __name__ == "__main__":
    main()
