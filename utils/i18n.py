"""
Lightweight i18n for English (en) and Vietnamese (vi).
Uses Flask session + cookie for language persistence.
"""
from flask import g, request, session

from utils.locales.en import MESSAGES as EN_MESSAGES
from utils.locales.vi import MESSAGES as VI_MESSAGES

SUPPORTED_LANGUAGES = ("en", "vi")
DEFAULT_LANGUAGE = "en"
COOKIE_NAME = "lang"
MESSAGES = {"en": EN_MESSAGES, "vi": VI_MESSAGES}

# Map ML persona names to translation keys
PERSONA_KEYS = {
    "Backpacker": "persona.backpacker",
    "Explorer": "persona.explorer",
    "Luxury Traveler": "persona.luxury_traveler",
    "Foodie": "persona.foodie",
}

PERIOD_KEYS = {
    "Morning": "period.morning",
    "Afternoon": "period.afternoon",
    "Evening": "period.evening",
}


def _normalize_lang(code):
    if not code:
        return DEFAULT_LANGUAGE
    code = str(code).lower().strip()[:2]
    return code if code in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def get_language():
    """Current language from request context."""
    return getattr(g, "lang", DEFAULT_LANGUAGE) if g else DEFAULT_LANGUAGE


def set_language(lang_code):
    """Persist language in session."""
    lang = _normalize_lang(lang_code)
    session["lang"] = lang
    if g:
        g.lang = lang
    return lang


def init_language(app):
    """Register before_request and template context for i18n."""

    @app.before_request
    def load_language():
        # Query param overrides for quick switch links
        if request.args.get("lang"):
            set_language(request.args.get("lang"))
        elif "lang" in session:
            g.lang = _normalize_lang(session["lang"])
        elif request.cookies.get(COOKIE_NAME):
            g.lang = _normalize_lang(request.cookies.get(COOKIE_NAME))
            session["lang"] = g.lang
        else:
            g.lang = DEFAULT_LANGUAGE
            session["lang"] = g.lang

    @app.context_processor
    def inject_translations():
        lang = get_language()
        return {
            "_": translate,
            "current_lang": lang,
            "supported_languages": SUPPORTED_LANGUAGES,
            "other_lang": "vi" if lang == "en" else "en",
            "js_translations": get_js_bundle(lang),
        }

    @app.template_filter("t_category")
    def t_category_filter(cat):
        return translate(f"category.{str(cat).lower()}")

    @app.template_filter("t_interest")
    def t_interest_filter(key):
        return translate(f"interest.{str(key).lower()}")

    @app.template_filter("t_style")
    def t_style_filter(style):
        return translate(f"style.{str(style).lower()}")

    @app.template_filter("t_persona")
    def t_persona_filter(persona):
        key = PERSONA_KEYS.get(persona, "persona.explorer")
        return translate(key)

    @app.template_filter("t_period")
    def t_period_filter(period):
        key = PERIOD_KEYS.get(period, period)
        return translate(key) if key.startswith("period.") else translate(key)


def translate(key, **kwargs):
    """Return translated string; fallback to key if missing."""
    lang = get_language()
    text = MESSAGES.get(lang, EN_MESSAGES).get(key) or MESSAGES["en"].get(key) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, ValueError):
            return text
    return text


def get_js_bundle(lang):
    """Strings needed by frontend JavaScript."""
    keys = [
        "preview.select_city",
        "preview.loading",
        "preview.persona",
        "preview.predicted",
        "preview.trip_score",
        "preview.error",
        "form.loading.title",
        "form.loading.subtitle",
        "chart.your_budget",
        "chart.predicted_total",
        "chart.attractions_only",
        "persona.backpacker",
        "persona.explorer",
        "persona.luxury_traveler",
        "persona.foodie",
        "category.cafe",
        "category.nature",
        "category.museum",
        "category.food",
        "category.nightlife",
        "category.beach",
        "category.shopping",
        "category.adventure",
    ]
    bundle = {}
    msgs = MESSAGES.get(lang, EN_MESSAGES)
    en = MESSAGES["en"]
    for k in keys:
        bundle[k] = msgs.get(k) or en.get(k) or k
    bundle["persona_map"] = PERSONA_KEYS
    return bundle


def localize_plan(plan):
    """Apply translations to plan dict for templates/API."""
    if plan.get("budget_warning_key"):
        plan["budget_warning"] = translate(
            plan["budget_warning_key"],
            **plan.get("budget_warning_params", {}),
        )
    if plan.get("error_key"):
        plan["error"] = translate(plan["error_key"], **plan.get("error_params", {}))
    plan["persona_label"] = translate(
        PERSONA_KEYS.get(plan.get("persona", ""), "persona.explorer")
    )
    # Localize itinerary slot periods
    for day in plan.get("itinerary", []):
        for slot in day.get("slots", []):
            period = slot.get("period", "")
            slot["period_label"] = translate(
                PERIOD_KEYS.get(period, "period.morning")
            )
    return plan
