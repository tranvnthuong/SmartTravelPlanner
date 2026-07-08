/**
 * Chart.js visualizations for result page (i18n-aware)
 */
function chartT(key) {
    if (typeof window.APP_I18N !== "undefined" && window.APP_I18N[key]) {
        return window.APP_I18N[key];
    }
    return key;
}

function localizeCategory(cat) {
    if (typeof categoryLabels !== "undefined" && categoryLabels[cat]) {
        return categoryLabels[cat];
    }
    const key = "category." + String(cat).toLowerCase();
    const label = chartT(key);
    return label !== key ? label : cat.charAt(0).toUpperCase() + cat.slice(1);
}

document.addEventListener("DOMContentLoaded", function () {
    if (typeof categoryData === "undefined" || typeof budgetData === "undefined") {
        return;
    }

    const catLabels = Object.keys(categoryData).map(localizeCategory);
    const catValues = Object.values(categoryData);
    const catColors = [
        "#023e8a", "#0077b6", "#0096c7", "#00b4d8",
        "#48cae4", "#90e0ef", "#005f8a", "#2ec4b6",
    ];

    if (document.getElementById("categoryChart") && catLabels.length) {
        new Chart(document.getElementById("categoryChart"), {
            type: "doughnut",
            data: {
                labels: catLabels,
                datasets: [{
                    data: catValues,
                    backgroundColor: catColors.slice(0, catLabels.length),
                    borderWidth: 2,
                }],
            },
            options: {
                responsive: true,
                plugins: { legend: { position: "bottom" } },
            },
        });
    }

    if (document.getElementById("budgetChart")) {
        const locale = window.APP_LANG === "vi" ? "vi-VN" : "en-US";
        new Chart(document.getElementById("budgetChart"), {
            type: "bar",
            data: {
                labels: [
                    chartT("chart.your_budget"),
                    chartT("chart.predicted_total"),
                    chartT("chart.attractions_only"),
                ],
                datasets: [{
                    label: "VND",
                    data: [
                        budgetData.budget,
                        budgetData.predicted,
                        budgetData.planned_attractions,
                    ],
                    backgroundColor: ["#0077b6", "#00b4d8", "#48cae4"],
                    borderRadius: 8,
                }],
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function (ctx) {
                                return new Intl.NumberFormat(locale, {
                                    maximumFractionDigits: 0
                                }).format(ctx.raw) + " ₫";
                            }
                        },
                    },
                },
                scales: {
                    y: {
                        ticks: {
                            callback: function (v) {
                                return (v / 1e6).toFixed(1) + "M";
                            },
                        },
                    },
                },
            },
        });
    }
});
