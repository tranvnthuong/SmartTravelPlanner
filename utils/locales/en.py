"""English UI strings."""

MESSAGES = {
    # Meta & nav
    "app.name": "Smart Travel Planner",
    "nav.plan_trip": "Plan Trip",
    "nav.features": "Features",
    "lang.en": "English",
    "lang.vi": "Vietnamese",
    "footer.tagline": "AI-powered itineraries without external APIs",

    # Index hero
    "index.title": "Smart Travel Planner — Plan Your Trip",
    "index.badge": "AI + Machine Learning",
    "index.hero.title": "Your Personalized Vietnam Travel Planner",
    "index.hero.subtitle": "Build day-by-day itineraries with content-based recommendations, KMeans traveler clustering, and Random Forest budget prediction.",
    "index.stat.cities": "{count} Cities",
    "index.stat.places": "{count} Places",
    "index.stat.internal_data": "Internal data",
    "index.ml.title": "ML-Powered",
    "index.ml.tfidf": "TF-IDF Recommendations",
    "index.ml.route": "Greedy Route Optimization",
    "index.ml.budget": "Budget Prediction",
    "index.ml.persona": "Traveler Persona Detection",

    # Form
    "form.section.title": "Plan Your Journey",
    "form.section.subtitle": "Tell us your preferences and we'll craft your perfect itinerary",
    "form.city": "Destination City",
    "form.city.placeholder": "Select city...",
    "form.days": "Days",
    "form.style": "Style",
    "form.number.of.people": "People",
    "form.budget": "Budget (VND)",
    "form.interests": "Interests",
    "form.submit": "Generate Itinerary",
    "form.random": "Generate random",
    "form.preview": "Preview Recommendations",
    "form.preview.title": "Quick Preview",
    "form.preview.hint": "Click \"Preview Recommendations\" to see ML-ranked places.",
    "form.loading.title": "Crafting your itinerary...",
    "form.loading.subtitle": "Running recommendations & route optimization",

    # Features
    "features.title": "How It Works",
    "features.filter.title": "Content-Based Filtering",
    "features.filter.desc": "TF-IDF + cosine similarity match places to your interests and ratings.",
    "features.route.title": "Route Optimization",
    "features.route.desc": "Greedy nearest-neighbor routing keeps stops close and categories diverse.",
    "features.budget.title": "Budget Intelligence",
    "features.budget.desc": "Random Forest predicts total trip cost with smart warnings.",
    "features.stats": "The system has successfully generated {count} trips for users.",

    # Styles & interests
    "style.budget": "Budget",
    "style.normal": "Normal",
    "style.luxury": "Luxury",
    "interest.nature": "Nature",
    "interest.cafe": "Café",
    "interest.museum": "Museum",
    "interest.food": "Food",
    "interest.nightlife": "Nightlife",
    "interest.photography": "Photography",
    "interest.adventure": "Adventure",

    # Categories
    "category.cafe": "Café",
    "category.nature": "Nature",
    "category.museum": "Museum",
    "category.food": "Food",
    "category.nightlife": "Nightlife",
    "category.beach": "Beach",
    "category.shopping": "Shopping",
    "category.adventure": "Adventure",

    # Personas
    "persona.backpacker": "Backpacker",
    "persona.explorer": "Explorer",
    "persona.luxury_traveler": "Luxury Traveler",
    "persona.foodie": "Foodie",

    # Periods
    "period.morning": "Morning",
    "period.afternoon": "Afternoon",
    "period.evening": "Evening",

    # Result page
    "result.title": "Your Trip — {city}",
    "result.new_plan": "New Plan",
    "result.adventure": "{city} Adventure",
    "result.meta": "{days} days · {style} style · {interests}",
    "result.trip_score": "Trip Score",
    "result.traveler_type": "Traveler Type",
    "result.your_budget": "Your Budget",
    "result.predicted_total": "Predicted Total",
    "result.attractions_cost": "Attractions Cost",
    "result.budget_analysis": "Budget Analysis",
    "result.category_breakdown": "Category Breakdown",
    "result.actions": "Actions",
    "result.regenerate": "Regenerate Itinerary",
    "result.plan_another": "Plan Another Trip",
    "result.top_recommendations": "Top Recommendations",
    "result.your_itinerary": "Your Itinerary",
    "result.day": "Day {n}",
    "result.cost": "Cost:",
    "result.duration": "Duration:",
    "result.hours": "hours",
    "result.score": "Score",
    "result.rain_warning": "Outdoor risk during rain! It is recommended to switch to an indoor shelter.",
    "result.per_person": "Per person",
    "result.budget_set": "Budget set",
    "result.expected_spending": "Expected spending",
    "result.amount_vnd": "Amount (VND)",

    # Charts
    "chart.your_budget": "Your Budget",
    "chart.predicted_total": "Predicted Total",
    "chart.attractions_only": "Attractions Only",

    # Preview (JS)
    "preview.select_city": "Select a city and at least one interest.",
    "preview.loading": "Loading ML recommendations...",
    "preview.persona": "Persona:",
    "preview.predicted": "Predicted:",
    "preview.trip_score": "Trip Score:",
    "preview.error": "Request failed.",

    # Validation errors
    "error.city_required": "Please select a destination city.",
    "error.city_invalid": "Invalid city selected.",
    "error.days_range": "Number of days must be between 1 and 14.",
    "error.budget_min": "Budget must be at least 500,000 VND.",
    "error.style_invalid": "Invalid travel style.",
    "error.interests_required": "Select at least one interest.",
    "error.interests_invalid": "Invalid interests selected.",
    "error.plan_failed": "Could not generate plan: {detail}",
    "error.not_found": "Page not found.",
    "error.server": "Internal server error. Please try again.",
    "error.no_attractions": "No attractions found for city: {city}",

    # Budget warnings
    "budget.over": "Predicted cost ({cost:,.0f} VND) exceeds your budget. Consider Budget style or fewer days.",
    "budget.near": "You are very close to your budget limit. Plan extra buffer.",

    # flash
    "flash.random_trip": "🎲 AI randomly selected a trip to {city} for {people} people over {days} days!",

    "rain_enabled": "Rain mode is enabled",
    "rain_description": "High-risk outdoor attractions are highlighted in red. You should prioritize indoor attractions!",
    "rain_mode": "Rain mode",
    "divide_fees": "Split costs among the group",
    "go_in_group": "Travel in a group",
    "of_person": "people"
}
