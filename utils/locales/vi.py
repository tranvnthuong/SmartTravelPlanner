"""Vietnamese UI strings."""

MESSAGES = {
    # Meta & nav
    "app.name": "Smart Travel Planner",
    "nav.plan_trip": "Lên lịch chuyến đi",
    "nav.features": "Tính năng",
    "lang.en": "Tiếng Anh",
    "lang.vi": "Tiếng Việt",
    "footer.tagline": "Lịch trình AI — không dùng API bên ngoài",

    # Index hero
    "index.title": "Smart Travel Planner — Lên kế hoạch",
    "index.badge": "AI + Machine Learning",
    "index.hero.title": "Lập kế hoạch du lịch Việt Nam cá nhân hóa",
    "index.hero.subtitle": "Tạo lịch trình từng ngày với gợi ý TF-IDF, phân cụm KMeans và dự đoán ngân sách Random Forest.",
    "index.stat.cities": "5 thành phố",
    "index.stat.places": "120+ địa điểm",
    "index.stat.no_api": "Không API ngoài",
    "index.ml.title": "Nền tảng ML",
    "index.ml.tfidf": "Gợi ý TF-IDF",
    "index.ml.route": "Tối ưu lộ trình Greedy",
    "index.ml.budget": "Dự đoán ngân sách",
    "index.ml.persona": "Nhận diện hồ sơ du khách",

    # Form
    "form.section.title": "Lên kế hoạch chuyến đi",
    "form.section.subtitle": "Cho chúng tôi biết sở thích — chúng tôi sẽ tạo lịch trình phù hợp",
    "form.city": "Thành phố",
    "form.city.placeholder": "Chọn thành phố...",
    "form.days": "Số ngày",
    "form.style": "Phong cách",
    "form.budget": "Ngân sách (VND)",
    "form.interests": "Sở thích",
    "form.submit": "Tạo lịch trình",
    "form.preview": "Xem gợi ý trước",
    "form.preview.hint": "Nhấn \"Xem gợi ý trước\" để xem địa điểm được ML xếp hạng.",
    "form.loading.title": "Đang tạo lịch trình...",
    "form.loading.subtitle": "Chạy gợi ý và tối ưu lộ trình",
    "features.title": "Cách hoạt động",
    "features.filter.title": "Lọc theo nội dung",
    "features.filter.desc": "TF-IDF + cosine similarity khớp địa điểm với sở thích và đánh giá.",
    "features.route.title": "Tối ưu lộ trình",
    "features.route.desc": "Greedy gần nhất giữ các điểm gần nhau và đa dạng danh mục.",
    "features.budget.title": "Thông minh ngân sách",
    "features.budget.desc": "Random Forest dự đoán tổng chi phí và cảnh báo thông minh.",
    "features.stats": "Đã lên {count} chuyến đi",

    # Styles & interests
    "style.budget": "Tiết kiệm",
    "style.normal": "Bình thường",
    "style.luxury": "Cao cấp",
    "interest.nature": "Thiên nhiên",
    "interest.cafe": "Cà phê",
    "interest.museum": "Bảo tàng",
    "interest.food": "Ẩm thực",
    "interest.nightlife": "Vui chơi đêm",
    "interest.photography": "Nhiếp ảnh",
    "interest.adventure": "Phiêu lưu",

    # Categories
    "category.cafe": "Cà phê",
    "category.nature": "Thiên nhiên",
    "category.museum": "Bảo tàng",
    "category.food": "Ẩm thực",
    "category.nightlife": "Vui chơi đêm",
    "category.beach": "Biển",
    "category.shopping": "Mua sắm",
    "category.adventure": "Phiêu lưu",

    # Personas
    "persona.backpacker": "Phượt thủ",
    "persona.explorer": "Nhà thám hiểm",
    "persona.luxury_traveler": "Du lịch cao cấp",
    "persona.foodie": "Sành ăn",

    # Periods
    "period.morning": "Buổi sáng",
    "period.afternoon": "Buổi chiều",
    "period.evening": "Buổi tối",

    # Result page
    "result.title": "Chuyến đi — {city}",
    "result.new_plan": "Kế hoạch mới",
    "result.adventure": "Khám phá {city}",
    "result.meta": "{days} ngày · phong cách {style} · {interests}",
    "result.trip_score": "Điểm chuyến đi",
    "result.traveler_type": "Loại du khách",
    "result.your_budget": "Ngân sách của bạn",
    "result.predicted_total": "Dự đoán tổng",
    "result.attractions_cost": "Chi phí điểm đến",
    "result.budget_analysis": "Phân tích ngân sách",
    "result.category_breakdown": "Phân bổ danh mục",
    "result.actions": "Thao tác",
    "result.regenerate": "Tạo lại lịch trình",
    "result.plan_another": "Lên chuyến khác",
    "result.top_recommendations": "Gợi ý hàng đầu",
    "result.your_itinerary": "Lịch trình của bạn",
    "result.day": "Ngày {n}",
    "result.cost": "Chi phí:",
    "result.duration": "Thời lượng:",
    "result.hours": "giờ",
    "result.score": "Điểm",

    # Charts
    "chart.your_budget": "Ngân sách",
    "chart.predicted_total": "Dự đoán tổng",
    "chart.attractions_only": "Chỉ điểm đến",

    # Preview (JS)
    "preview.select_city": "Chọn thành phố và ít nhất một sở thích.",
    "preview.loading": "Đang tải gợi ý ML...",
    "preview.persona": "Hồ sơ:",
    "preview.predicted": "Dự đoán:",
    "preview.trip_score": "Điểm chuyến đi:",
    "preview.error": "Yêu cầu thất bại.",

    # Validation errors
    "error.city_required": "Vui lòng chọn thành phố.",
    "error.city_invalid": "Thành phố không hợp lệ.",
    "error.days_range": "Số ngày phải từ 1 đến 14.",
    "error.budget_min": "Ngân sách tối thiểu 500.000 VND.",
    "error.style_invalid": "Phong cách không hợp lệ.",
    "error.interests_required": "Chọn ít nhất một sở thích.",
    "error.interests_invalid": "Sở thích không hợp lệ.",
    "error.plan_failed": "Không tạo được lịch trình: {detail}",
    "error.not_found": "Không tìm thấy trang.",
    "error.server": "Lỗi máy chủ. Vui lòng thử lại.",
    "error.no_attractions": "Không có địa điểm cho thành phố: {city}",

    # Budget warnings
    "budget.over": "Chi phí dự đoán ({cost:,.0f} VND) vượt ngân sách. Hãy chọn phong cách Tiết kiệm hoặc giảm số ngày.",
    "budget.near": "Bạn sắp chạm trần ngân sách. Nên dự phòng thêm.",
}
