"""
Orchestrates recommendation, clustering, optimization, and budget prediction.
"""
from utils.data_loader import get_city_attractions, load_attractions
from utils.model_loader import get_budget_predictor, get_clusterer
from utils.optimizer import ItineraryOptimizer, compute_trip_score
from utils.recommender import AttractionRecommender

CITY_CENTERS = {
    "da lat": (11.9404, 108.4583),
    "ho chi minh": (10.8231, 106.6297),
    "ha noi": (21.0285, 105.8542),
    "da nang": (16.0544, 108.2022),
    "nha trang": (12.2388, 109.1967),
}


def resolve_city_center(city):
    """Get default map center for a city."""
    key = city.strip().lower()
    for name, coords in CITY_CENTERS.items():
        if name in key or key in name:
            return coords
    return (16.0, 108.0)


def generate_travel_plan(
    city,
    num_days,
    budget,
    interests,
    style,
    num_people=1,  # THÊM MỚI: Nhận tham số số người từ app.py (mặc định là 1)
    regenerate_seed=0,
):
    """
    Full pipeline: recommend -> cluster user -> build itinerary -> predict budget.
    Returns dict ready for templates / JSON.
    """
    all_df = load_attractions()
    city_df = get_city_attractions(city, all_df)

    if city_df.empty:
        return {
            "error_key": "error.no_attractions",
            "error_params": {"city": city},
        }

    # Tính toán chi phí quy đổi cho 1 người để đưa vào các mô hình ML (vì ML vốn train cho 1 người)
    per_person_budget = float(budget) / max(1, int(num_people))

    recommender = AttractionRecommender(city_df)

    recommended = recommender.recommend(
        interests=interests,
        total_budget=per_person_budget,
        num_days=int(num_days),
        style=style,
        city=city,
        top_n=max(int(num_days) * 6, 18),
        regenerate_seed=regenerate_seed,
    )

    clusterer = get_clusterer()
    persona = clusterer.predict_persona(interests, per_person_budget, int(num_days), style)

    lat, lon = resolve_city_center(city)
    optimizer = ItineraryOptimizer()
    itinerary = optimizer.build_itinerary(
        recommended,
        num_days=int(num_days),
        city_center_lat=lat,
        city_center_lon=lon,
        regenerate_seed=regenerate_seed,
    )

    # Tính toán chi phí vé/tham quan cơ sở (Có thể nhân với num_people nếu estimated_cost là giá vé đơn lẻ cho 1 người)
    planned_cost = sum(
        slot["place"]["estimated_cost"] * int(num_people)  # CẬP NHẬT: Nhân với số lượng người
        for day in itinerary
        for slot in day["slots"]
    )
    num_places = sum(len(day["slots"]) for day in itinerary)

    # Tương tự, quy đổi chi phí dự kiến các điểm tham quan về 1 người
    per_person_planned_cost = planned_cost / max(1, int(num_people))

    predictor = get_budget_predictor()
    predicted_cost_per_person = predictor.predict(
        interests, per_person_budget, int(num_days), style, per_person_planned_cost, num_places
    )
    # Nhân ngược lại để lấy tổng dự đoán cho cả nhóm
    predicted_cost = predicted_cost_per_person * int(num_people)

    trip_score = compute_trip_score(itinerary, float(budget), predicted_cost, persona)

    # Category breakdown for charts
    category_breakdown = {}
    for day in itinerary:
        for slot in day["slots"]:
            cat = slot["place"]["category"]
            category_breakdown[cat] = category_breakdown.get(cat, 0) + 1

    budget_warning_key = None
    budget_warning_params = {}
    if predicted_cost > float(budget) * 1.1:
        budget_warning_key = "budget.over"
        budget_warning_params = {"cost": predicted_cost}
    elif predicted_cost > float(budget) * 0.95:
        budget_warning_key = "budget.near"

    recommended_list = [
        {
            "id": int(r["id"]),
            "name": str(r["name"]),
            "category": str(r["category"]),
            "rating": float(r["rating"]),
            "estimated_cost": int(r["estimated_cost"]),
            "duration_hours": float(r["duration_hours"]),
            "description": str(r["description"]),
            "recommendation_score": round(float(r["recommendation_score"]), 3),
        }
        for _, r in recommended.head(12).iterrows()
    ]

    return {
        "city": city,
        "num_days": int(num_days),
        "num_people": int(num_people),  # THÊM MỚI: Trả về để lưu trữ và hiển thị ngoài giao diện
        "budget": float(budget),
        "style": style,
        "interests": interests,
        "persona": persona,
        "itinerary": itinerary,
        "recommended": recommended_list,
        "planned_attraction_cost": planned_cost,
        "predicted_total_cost": round(predicted_cost, 0),
        "trip_score": trip_score,
        "category_breakdown": category_breakdown,
        "budget_warning_key": budget_warning_key,
        "budget_warning_params": budget_warning_params,
        "regenerate_seed": regenerate_seed,
    }