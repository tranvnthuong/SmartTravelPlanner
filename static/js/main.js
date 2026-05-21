/**
 * Smart Travel Planner - Main frontend interactions (i18n-aware)
 */
function t(key) {
    if (window.APP_I18N && window.APP_I18N[key]) {
        return window.APP_I18N[key];
    }
    return key;
}

function personaLabel(persona, personaLabelFromApi) {
    if (personaLabelFromApi) {
        return personaLabelFromApi;
    }
    const map = (window.APP_I18N && window.APP_I18N.persona_map) || {};
    const msgKey = map[persona];
    return msgKey ? t(msgKey) : persona;
}

function categoryLabel(cat) {
    const key = "category." + String(cat).toLowerCase();
    return t(key) !== key ? t(key) : cat;
}

$(document).ready(function () {
    $("#tripForm").on("submit", function () {
        const city = $("select[name='city']").val();
        const interests = $("input[name='interests']:checked").length;
        if (!city || interests === 0) {
            return true;
        }
        $("#loadingOverlay").removeClass("d-none");
        $("#loadingTitle").text(t("form.loading.title"));
        $("#loadingSubtitle").text(t("form.loading.subtitle"));
        $("#submitBtn").prop("disabled", true);
    });

    $("#previewBtn").on("click", function (e) {
        e.preventDefault();
        const form = $("#tripForm");
        const interests = form.find("input[name='interests']:checked").length;
        if (!form.find("select[name='city']").val() || interests === 0) {
            $("#previewPanel").html(
                '<p class="text-danger"><i class="bi bi-exclamation-circle"></i> ' +
                    escapeHtml(t("preview.select_city")) +
                    "</p>"
            );
            return;
        }

        $("#previewPanel").html(
            '<div class="text-center py-4"><div class="spinner-border text-primary"></div>' +
                '<p class="mt-2 small text-muted">' +
                escapeHtml(t("preview.loading")) +
                "</p></div>"
        );

        $.ajax({
            url: "/recommendations",
            method: "POST",
            data: form.serialize(),
            success: function (res) {
                if (!res.success) {
                    $("#previewPanel").html(
                        '<p class="text-danger">' +
                            (res.errors || [t("preview.error")]).join("<br>") +
                            "</p>"
                    );
                    return;
                }
                let html = '<div class="mb-3 p-2 rounded bg-light">';
                html +=
                    "<strong>" +
                    escapeHtml(t("preview.persona")) +
                    "</strong> " +
                    escapeHtml(personaLabel(res.persona, res.persona_label)) +
                    "<br>";
                html +=
                    "<strong>" +
                    escapeHtml(t("preview.predicted")) +
                    "</strong> " +
                    formatVnd(res.predicted_total_cost) +
                    "<br>";
                html +=
                    "<strong>" +
                    escapeHtml(t("preview.trip_score")) +
                    "</strong> " +
                    res.trip_score;
                html += "</div>";
                res.recommended.slice(0, 6).forEach(function (p) {
                    html += '<div class="preview-place">';
                    html += "<h6>" + escapeHtml(p.name) + "</h6>";
                    html +=
                        '<span class="category-tag">' +
                        escapeHtml(categoryLabel(p.category)) +
                        "</span> ";
                    html +=
                        '<span class="rating-badge"><i class="bi bi-star-fill"></i> ' +
                        p.rating +
                        "</span>";
                    html +=
                        '<p class="small text-muted mb-0 mt-1">' +
                        formatVnd(p.estimated_cost) +
                        " · " +
                        p.duration_hours +
                        "h</p>";
                    html += "</div>";
                });
                $("#previewPanel").html(html);
            },
            error: function (xhr) {
                const msg =
                    xhr.responseJSON && xhr.responseJSON.errors
                        ? xhr.responseJSON.errors.join("<br>")
                        : t("preview.error");
                $("#previewPanel").html('<p class="text-danger">' + msg + "</p>");
            },
        });
    });

    function formatVnd(n) {
        const locale = window.APP_LANG === "vi" ? "vi-VN" : "en-US";
        return new Intl.NumberFormat(locale).format(Math.round(n)) + " ₫";
    }

    function escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }
});
