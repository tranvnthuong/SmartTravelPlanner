"""
Smart Travel Planner - Flask application entry point.
Personalized travel itineraries using ML (no external APIs).
"""
import json
import logging
import os
import sys
from pathlib import Path

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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "smart-travel-planner-dev-key")
init_language(app)

VALID_CITIES = ["Da Lat", "Ho Chi Minh", "Ha Noi", "Da Nang", "Nha Trang"]
VALID_STYLES = ["budget", "normal", "luxury"]
VALID_INTERESTS = [
    "nature", "cafe", "museum", "food",
    "nightlife", "photography", "adventure",
]


def validate_plan_form(form):
    """Validate user input; return (errors, cleaned_data)."""
    errors = []
    city = (form.get("city") or "").strip()
    num_days = form.get("num_days", type=int)
    budget = form.get("budget", type=float)
    style = (form.get("style") or "normal").strip().lower()
    interests = form.getlist("interests")

    if not city:
        errors.append(translate("error.city_required"))
    elif city not in VALID_CITIES:
        errors.append(translate("error.city_invalid"))

    if num_days is None or num_days < 1 or num_days > 14:
        errors.append(translate("error.days_range"))

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


@app.route("/")
def index():
    """Landing page with trip planning form."""
    stats = get_trip_stats()
    resp = make_response(
        render_template(
            "index.html",
            cities=VALID_CITIES,
            interests=VALID_INTERESTS,
            styles=VALID_STYLES,
            stats=stats,
        )
    )
    return _response_with_lang_cookie(resp)


@app.route("/generate-plan", methods=["POST"])
def generate_plan():
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

    interests_labels = ", ".join(translate(f"interest.{i}") for i in data["interests"])

    resp = make_response(
        render_template(
            "result.html",
            plan=plan,
            interests_labels=interests_labels,
            category_breakdown_json=json.dumps(plan["category_breakdown"]),
            budget_chart_json=json.dumps({
                "budget": data["budget"],
                "predicted": plan["predicted_total_cost"],
                "planned_attractions": plan["planned_attraction_cost"],
            }),
        )
    )
    return _response_with_lang_cookie(resp)


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


@app.errorhandler(404)
def not_found(e):
    flash(translate("error.not_found"), "warning")
    return redirect(url_for("index"))


@app.errorhandler(500)
def server_error(e):
    flash(translate("error.server"), "danger")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
