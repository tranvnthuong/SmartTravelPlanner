"""
Smart Travel Planner - Flask application entry point.
Personalized travel itineraries using ML (no external APIs).
"""
import json
import logging
import os
import sys
import random  # Import thêm phục vụ cho tính năng Random chuyến đi ngẫu nhiên
from pathlib import Path
import uuid
import time
import threading

from flask import Flask, flash, jsonify, make_response, redirect, render_template, request, url_for

# Ensure project root is on path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from utils.database import get_trip_stats, init_db, save_trip
from urllib.parse import urlparse

from utils.i18n import (
    COOKIE_NAME,
    SUPPORTED_LANGUAGES,
    get_language,
    init_language,
    localize_plan,
    set_language,
    translate,
)
from utils.planner import generate_travel_plan

from utils.data_loader import (
    get_available_cities,
    get_dataset_stats,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PLAN_STORE = {}
PLAN_TTL_SECONDS = 30 * 60
MAX_PLANS = 500

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "smart-travel-planner-dev-key")
init_language(app)

VALID_CITIES = get_available_cities()
VALID_STYLES = ["budget", "normal", "luxury"]
VALID_INTERESTS = [
    "nature", "cafe", "museum", "food",
    "nightlife", "photography", "adventure",
]

def get_plan(plan_id):
    item = PLAN_STORE.get(plan_id)
    if not item:
        return None

    if time.time() - item["created_at"] > PLAN_TTL_SECONDS:
        PLAN_STORE.pop(plan_id, None)
        return None

    return item["plan"]

def save_plan(plan, plan_id):
    if len(PLAN_STORE) >= MAX_PLANS:
        PLAN_STORE.pop(list(PLAN_STORE.keys())[0], None)
        
    PLAN_STORE[plan_id] = {
        "created_at": time.time(),
        "plan": plan,
    }

def validate_plan_form(form):
    """Validate user input; return (errors, cleaned_data)."""
    errors = []
    city = (form.get("city") or "").strip()
    num_days = form.get("num_days", type=int)
    num_people = form.get("num_people", default=1, type=int)  # THÊM MỚI: Lấy số người đi du lịch
    budget = form.get("budget", type=float)
    style = (form.get("style") or "normal").strip().lower()
    interests = form.getlist("interests")

    if not city:
        errors.append(translate("error.city_required"))
    elif city not in VALID_CITIES:
        errors.append(translate("error.city_invalid"))

    if num_days is None or num_days < 1 or num_days > 14:
        errors.append(translate("error.days_range"))

    # THÊM MỚI: Validate số người đi du lịch
    if num_people is None or num_people < 1:
        errors.append("Số người tham gia chuyến đi phải lớn hơn hoặc bằng 1.")

    if budget is None or budget < 500_000:
        errors.append(translate("error.budget_min"))

    if style not in VALID_STYLES:
        errors.append(translate("error.style_invalid"))

    if not interests:
        errors.append(translate("error.interests_required"))
    else:
        interests = [i.lower() for i in interests if i.lower() in VALID_INTERESTS]
        if not interests:
            errors.append(translate("error.interests_invalid"))

    cleaned = {
        "city": city,
        "num_days": num_days,
        "num_people": num_people,  # THÊM MỚI
        "budget": budget,
        "style": style,
        "interests": interests,
    }
    return errors, cleaned


def _response_with_lang_cookie(resp):
    """Attach language cookie to response."""
    resp.set_cookie(COOKIE_NAME, get_language(), max_age=60 * 60 * 24 * 365)
    return resp


@app.before_request
def setup():
    """Initialize database on first request."""
    if not getattr(app, "_db_ready", False):
        init_db()
        app._db_ready = True


@app.route("/set-language/<lang_code>")
def set_language_route(lang_code):
    """Switch UI language and redirect back."""
    if lang_code not in SUPPORTED_LANGUAGES:
        flash(translate("error.not_found"), "warning")
        return redirect(url_for("index"))
    set_language(lang_code)
    next_url = request.args.get("next")
    if not next_url:
        ref = request.referrer
        if ref:
            parsed = urlparse(ref)
            if parsed.path.startswith("/"):
                next_url = parsed.path + (f"?{parsed.query}" if parsed.query else "")
    if not next_url or not str(next_url).startswith("/"):
        next_url = url_for("index")
    resp = make_response(redirect(next_url))
    return _response_with_lang_cookie(resp)


@app.route("/result")
def result():
    plan = get_plan(request.args.get("plan_id"))
    if not plan:
        print("No plan found in request or PLAN_STORE.")
        flash(translate("error.not_found"), "warning")
        return redirect(url_for("index"))

    plan = localize_plan(plan)

    interests_labels = ", ".join(
        translate(f"interest.{i}")
        for i in plan.get("interests", [])
    )

    return render_template(
        "result.html",
        plan=plan,
        num_people=plan.get("num_people", 1),
        interests_labels=interests_labels,
        category_breakdown_json=json.dumps(
            plan["category_breakdown"]
        ),
        budget_chart_json=json.dumps({
            "budget": plan["budget"],
            "predicted": plan["predicted_total_cost"],
            "planned_attractions": plan["planned_attraction_cost"],
        }),
    )


@app.route("/")
def index():
    """Landing page with trip planning form."""
    trip_stats = get_trip_stats()
    dataset_stats = get_dataset_stats()
    resp = make_response(
        render_template(
            "index.html",
            cities=VALID_CITIES,
            interests=VALID_INTERESTS,
            styles=VALID_STYLES,
            stats=trip_stats,
            dataset_stats=dataset_stats,
        )
    )
    return _response_with_lang_cookie(resp)


@app.route("/generate-plan", methods=["GET", "POST"])
def generate_plan():
    if request.method == "GET":
        return redirect(url_for("index"))
    """Process form and render personalized itinerary."""
    errors, data = validate_plan_form(request.form)
    if errors:
        for msg in errors:
            flash(msg, "danger")
        return redirect(url_for("index"))

    seed = request.form.get("regenerate_seed", 0, type=int)
    try:
        plan = generate_travel_plan(
            city=data["city"],
            num_days=data["num_days"],
            num_people=data["num_people"],
            budget=data["budget"],
            interests=data["interests"],
            style=data["style"],
            regenerate_seed=seed,
        )
    except Exception as exc:
        logger.exception("Plan generation failed")
        flash(translate("error.plan_failed", detail=str(exc)), "danger")
        return redirect(url_for("index"))

    plan = localize_plan(plan)

    if plan.get("error"):
        flash(plan["error"], "warning")
        return redirect(url_for("index"))

    # Bạn có thể cần cập nhật lại cấu trúc hàm save_trip trong utils/database.py nếu muốn lưu cả số người vào DB
    save_trip(
        data["city"],
        data["num_days"],
        data["budget"],
        data["style"],
        data["interests"],
        plan["persona"],
        plan["predicted_total_cost"],
        plan["trip_score"],
    )

    plan_id = str(uuid.uuid4())
    save_plan(plan, plan_id)
        
    return redirect(url_for("result", plan_id=plan_id))


@app.route("/recommendations", methods=["POST"])
def recommendations_api():
    """JSON API for live recommendations preview."""
    errors, data = validate_plan_form(request.form)
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    try:
        plan = generate_travel_plan(**data, regenerate_seed=0)
        if plan.get("error_key"):
            plan = localize_plan(plan)
            return jsonify({"success": False, "errors": [plan.get("error")]}), 404
        plan = localize_plan(plan)
        return jsonify({
            "success": True,
            "recommended": plan["recommended"],
            "persona": plan["persona"],
            "persona_label": plan["persona_label"],
            "predicted_total_cost": plan["predicted_total_cost"],
            "trip_score": plan["trip_score"],
        })
    except Exception as exc:
        logger.exception("Recommendations API failed")
        return jsonify({"success": False, "errors": [str(exc)]}), 500


# =====================================================================
# CHỨC NĂNG MỚI LẠ 1: "SURPRISE ME!" - QUAY SỐ CHỌN CHUYẾN ĐI NGẪU NHIÊN
# =====================================================================
@app.route("/surprise-me", methods=["GET"])
def surprise_me():
    """Tự động tạo ra một bộ thông số ngẫu nhiên hợp lý và tính toán lịch trình ngay lập tức."""
    random_city = random.choice(VALID_CITIES)
    random_days = random.randint(2, 5)  # Thường đi ngẫu nhiên từ 2-5 ngày là đẹp nhất
    random_people = random.randint(1, 4)  # THÊM MỚI: Random số người từ 1 đến 4 người
    random_style = random.choice(VALID_STYLES)
    
    # Random từ 1 đến 3 sở thích
    num_interests = random.randint(1, 3)
    random_interests = random.sample(VALID_INTERESTS, num_interests)
    
    # Tính toán mức ngân sách giả định ngẫu nhiên phù hợp với phong cách và quy mô số người
    if random_style == "budget":
        random_budget = random_days * random_people * random.randint(600000, 1000000)
    elif random_style == "luxury":
        random_budget = random_days * random_people * random.randint(3000000, 6000000)
    else:
        random_budget = random_days * random_people * random.randint(1200000, 2500000)

    try:
        plan = generate_travel_plan(
            city=random_city,
            num_days=random_days,
            num_people=random_people,  # THÊM MỚI
            budget=random_budget,
            interests=random_interests,
            style=random_style,
            regenerate_seed=random.randint(1, 999),
        )
        plan = localize_plan(plan)
        
        save_trip(random_city, random_days, random_budget, random_style, random_interests, plan["persona"], plan["predicted_total_cost"], plan["trip_score"])
        
        flash(
            translate(
                "flash.random_trip",
                city=random_city,
                people=random_people,
                days=random_days,
            ),
            "success",
        )
        
        plan_id = str(uuid.uuid4())
        save_plan(plan, plan_id)
    
        return redirect(url_for("result", plan_id=plan_id))
    
    except Exception as exc:
        logger.exception("Surprise me plan failed")
        flash("Có lỗi xảy ra khi quay số chuyến đi ngẫu nhiên.", "danger")
        return redirect(url_for("index"))


# =====================================================================
# CHỨC NĂNG MỚI LẠ 2: CÔNG CỤ CHIA TIỀN NHÓM (GROUP BUDGET SPLITTER)
# =====================================================================
@app.route("/budget-splitter", methods=["POST"])
def budget_splitter():
    """Hỗ trợ nhập số người và tự tính toán phân bổ chi phí chi tiết theo đầu người từ kết quả ML."""
    try:
        num_people = request.form.get("num_people", type=int)
        if not num_people or num_people < 1:
            return jsonify({"success": False, "message": "Số người tham gia phải lớn hơn 0"}), 400

        plan = get_plan(request.args.get("plan_id"))
        if not plan:
            return jsonify({"success": False, "message": "Không tìm thấy lịch trình hiện tại để chia tiền."}), 404

        predicted_total = plan.get("predicted_total_cost", 0)
        category_breakdown = plan.get("category_breakdown", {})

        # Phân rã tiền theo từng người
        per_person_total = predicted_total / num_people
        per_person_breakdown = {category: (value / num_people) for category, value in category_breakdown.items()}

        return jsonify({
            "success": True,
            "num_people": num_people,
            "total_cost": predicted_total,
            "per_person_total": per_person_total,
            "per_person_breakdown": per_person_breakdown
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# =====================================================================
# CHỨC NĂNG MỚI LẠ 3: CHẾ ĐỘ TỐI ƯU HÓA LỊCH TRÌNH "THỜI TIẾT XẤU" (RAINY MODE)
# =====================================================================
@app.route("/toggle-rainy-mode", methods=["POST"])
def toggle_rainy_mode():
    """Bỏ các địa điểm ngoài trời (nature, adventure), ưu tiên địa điểm trong nhà (museum, cafe, food)."""
    try:
        plan_id = request.args.get("plan_id")
        plan = get_plan(plan_id)
        if not plan:
            return jsonify({"success": False, "message": "Vui lòng tạo một lịch trình trước."}), 404

        # Giả lập bộ lọc thông minh: Nếu kích hoạt Rainy Mode, AI sẽ tự động lọc hoặc đưa ra cảnh báo 
        # hoán đổi các hoạt động ngoài trời (nature, adventure) sang các hoạt động trong nhà.
        original_recommended = plan.get("recommended", [])
        rainy_recommended = []

        for item in original_recommended:
            # Tạo bản sao sâu để chỉnh sửa nội dung hiển thị hoặc gắn nhãn cảnh báo thời tiết
            new_item = item.copy()
            # Ví dụ kiểm tra nếu địa điểm thuộc nhóm thám hiểm/thiên nhiên
            if any(x in str(item).lower() for x in ["nature", "adventure", "outdoor", "thác", "núi", "rừng"]):
                new_item["note"] = "⚠️ Khuyến nghị đổi sang bảo tàng/quán cafe do trời mưa lớn!"
                new_item["status_rain"] = "outdoor_risk"
            else:
                new_item["note"] = "✅ An toàn (Địa điểm trong nhà/Mái che)"
                new_item["status_rain"] = "indoor_safe"
            rainy_recommended.append(new_item)

        plan["recommended"] = rainy_recommended
        save_plan(plan, plan_id)

        return jsonify({
            "success": True,
            "message": "Đã kích hoạt chế độ bộ lọc thời tiết mưa lớn thành công!",
            "updated_recommended": rainy_recommended
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# =====================================================================
# HẾT PHẦN MỞ RỘNG - GIỮ NGUYÊN CÁC HÀM XỬ LÝ LỖI GỐC
# =====================================================================
@app.errorhandler(404)
def not_found(e):
    flash(translate("error.not_found"), "warning")
    return redirect(url_for("index"))


@app.errorhandler(500)
def server_error(e):
    flash(translate("error.server"), "danger")
    return redirect(url_for("index"))

def cleanup_plan_store():
    while True:
        time.sleep(1000)

        now = time.time()
        expired_ids = [
            plan_id
            for plan_id, item in PLAN_STORE.items()
            if now - item["created_at"] > PLAN_TTL_SECONDS
        ]

        for plan_id in expired_ids:
            PLAN_STORE.pop(plan_id, None)
            app.logger.info(f"Cleaned up expired plan: {plan_id}")

if __name__ == "__main__":
    init_db()
    
    threading.Thread(target=cleanup_plan_store, daemon=True).start()
    
    app.run(debug=False, host="0.0.0.0", port=7860)