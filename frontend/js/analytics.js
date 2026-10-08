/* =====================================================
   SMARTSPEND AI - ANALYTICS
===================================================== */

document.addEventListener("DOMContentLoaded", () => {

    loadAnalytics();

    generatePrediction();

});


/* =====================================================
   LOAD ANALYTICS
===================================================== */

async function loadAnalytics() {

    try {

        const email = getUserEmail();

        if (!email) {

            console.error(
                "User email not found in localStorage/sessionStorage."
            );

            return;

        }


        const now = new Date();

        const month =
            `${now.getFullYear()}-${String(
                now.getMonth() + 1
            ).padStart(2, "0")}`;


        const url =
            `/api/analytics` +
            `?userEmail=${encodeURIComponent(email)}` +
            `&month=${month}`;


        const response =
            await fetch(
                url,
                {
                    cache: "no-store"
                }
            );


        const data =
            await response.json();


        console.log(
            "Analytics Data:",
            data
        );


        if (
            !response.ok ||
            data.success === false
        ) {

            throw new Error(
                data.message ||
                `Analytics API failed: ${response.status}`
            );

        }


        updateSummary(data);

        updateMonthlyTrend(
            data.monthlyTrend || []
        );

        updateCategories(
            data.categories || {}
        );

        updateInsights(
            data.aiInsights || []
        );


    } catch (error) {

        console.error(
            "Analytics loading error:",
            error
        );

    }

}


/* =====================================================
   SUMMARY CARDS
===================================================== */

function updateSummary(data) {

    const cards =
        document.querySelectorAll(
            ".cards-grid .card"
        );


    if (!cards.length) {

        return;

    }


    cards.forEach(card => {

        const titleElement =
            card.querySelector("h4");


        const valueElement =
            card.querySelector(
                ".empty-text"
            );


        if (
            !titleElement ||
            !valueElement
        ) {

            return;

        }


        const title =
            titleElement.textContent
                .trim()
                .toLowerCase();


        /* TOTAL INCOME */

        if (
            title === "total income"
        ) {

            valueElement.textContent =
                formatINR(
                    data.totalIncome
                );

        }


        /* TOTAL EXPENSES */

        else if (
            title === "total expenses"
        ) {

            valueElement.textContent =
                formatINR(
                    data.totalExpenses
                );

        }


        /* TOTAL SAVINGS */

        else if (
            title === "total savings"
        ) {

            valueElement.textContent =
                formatINR(
                    data.totalSavings
                );

        }


        /* FINANCIAL SCORE */

        else if (
            title === "financial score"
        ) {

            const score =
                Number(
                    data.financialScore
                );


            if (
                Number.isFinite(score)
            ) {

                valueElement.textContent =
                    `${score}/100`;

            } else {

                valueElement.textContent =
                    "--";

            }

        }

    });

}


/* =====================================================
   MONTHLY SPENDING TREND
===================================================== */

function updateMonthlyTrend(
    monthlyTrend
) {

    const boxes =
        document.querySelectorAll(
            ".chart-placeholder"
        );


    if (!boxes.length) {

        return;

    }


    const trendBox =
        boxes[0];


    if (
        !monthlyTrend ||
        monthlyTrend.length === 0
    ) {

        trendBox.innerHTML = `

            <i class="fa-solid fa-chart-line"></i>

            <h4>
                No Expense Data
            </h4>

            <p>
                Your monthly expense trend will appear here
                after adding transactions.
            </p>

        `;

        return;

    }


    const maxAmount =
        Math.max(
            ...monthlyTrend.map(
                item =>
                    Number(
                        item.amount
                    ) || 0
            ),
            1
        );


    let html = `

        <div class="analytics-bar-chart">

    `;


    monthlyTrend.forEach(
        item => {

            const amount =
                Number(
                    item.amount
                ) || 0;


            const height =
                Math.max(
                    (
                        amount /
                        maxAmount
                    ) * 100,
                    5
                );


            html += `

                <div class="bar-item">

                    <div class="bar-value">

                        ${formatINR(amount)}

                    </div>


                    <div
                        class="bar"
                        style="height:${height}%">

                    </div>


                    <div class="bar-label">

                        ${escapeHTML(
                            formatMonth(
                                item.month
                            )
                        )}

                    </div>

                </div>

            `;

        }
    );


    html += `

        </div>

    `;


    trendBox.innerHTML =
        html;


    addChartStyles();

}


/* =====================================================
   CATEGORY ANALYTICS
===================================================== */

function updateCategories(
    categories
) {

    const boxes =
        document.querySelectorAll(
            ".chart-placeholder"
        );


    if (
        boxes.length < 2
    ) {

        return;

    }


    const categoryBox =
        boxes[1];


    const entries =
        Object.entries(
            categories || {}
        )
        .map(
            ([name, amount]) => [
                name,
                Number(amount) || 0
            ]
        )
        .sort(
            (a, b) =>
                b[1] - a[1]
        )
        .slice(
            0,
            6
        );


    if (
        !entries.length
    ) {

        categoryBox.innerHTML = `

            <i class="fa-solid fa-chart-pie"></i>

            <h4>
                No Categories Yet
            </h4>

            <p>
                Category-wise expense distribution
                will be displayed here.
            </p>

        `;

        return;

    }


    const total =
        entries.reduce(
            (
                sum,
                [, amount]
            ) =>
                sum + amount,
            0
        );


    let html = `

        <div class="category-chart">

    `;


    entries.forEach(
        ([name, amount]) => {

            const percentage =
                total > 0
                    ? (
                        amount /
                        total
                    ) * 100
                    : 0;


            html += `

                <div class="category-item">

                    <div class="category-header">

                        <span>
                            ${escapeHTML(name)}
                        </span>

                        <strong>
                            ${formatINR(amount)}
                        </strong>

                    </div>


                    <div class="category-progress">

                        <div
                            class="category-progress-fill"
                            style="width:${percentage}%">

                        </div>

                    </div>


                    <small>

                        ${percentage.toFixed(1)}%

                    </small>

                </div>

            `;

        }
    );


    html += `

        </div>

    `;


    categoryBox.innerHTML =
        html;


    addChartStyles();

}


/* =====================================================
   AI INSIGHTS
===================================================== */

function updateInsights(
    insights
) {

    const heading =
        [
            ...document.querySelectorAll(
                "h2, h3, h4"
            )
        ]
        .find(
            element =>
                element.textContent
                    .trim()
                    .includes(
                        "AI Insights"
                    )
        );


    if (!heading) {

        return;

    }


    const widget =
        heading.closest(
            ".dashboard-widget"
        );


    if (!widget) {

        return;

    }


    let body =
        widget.querySelector(
            ".widget-body"
        );


    if (!body) {

        body =
            document.createElement(
                "div"
            );


        body.className =
            "widget-body";


        const empty =
            widget.querySelector(
                ".empty-state"
            );


        if (empty) {

            empty.replaceWith(
                body
            );

        } else {

            widget.appendChild(
                body
            );

        }

    }


    if (
        !Array.isArray(insights) ||
        !insights.length
    ) {

        body.innerHTML = `

            <div class="empty-state">

                <i class="fa-solid fa-robot"></i>

                <h4>
                    No Insights Available
                </h4>

                <p>
                    SmartSpend AI will analyze your spending
                    patterns and generate personalized
                    financial recommendations.
                </p>

            </div>

        `;

        return;

    }


    body.innerHTML = `

        <div class="insights-list">

            ${insights.map(
                insight => `

                    <div
                        class="insight-item
                        ${escapeHTML(
                            insight.type ||
                            "info"
                        )}">

                        <div class="insight-icon">

                            <i
                                class="fa-solid
                                ${getInsightIcon(
                                    insight.type
                                )}">

                            </i>

                        </div>


                        <div class="insight-content">

                            <h4>

                                ${escapeHTML(
                                    insight.title ||
                                    "AI Insight"
                                )}

                            </h4>


                            <p>

                                ${escapeHTML(
                                    insight.message ||
                                    ""
                                )}

                            </p>

                        </div>

                    </div>

                `
            ).join("")}

        </div>

    `;


    addChartStyles();

}


function getInsightIcon(
    type
) {

    if (
        type === "success"
    ) {

        return "fa-circle-check";

    }


    if (
        type === "warning"
    ) {

        return "fa-triangle-exclamation";

    }


    if (
        type === "danger"
    ) {

        return "fa-circle-exclamation";

    }


    return "fa-lightbulb";

}


/* =====================================================
   NEXT MONTH PREDICTION
===================================================== */

async function generatePrediction() {

    const predictionElement =
        document.getElementById(
            "nextMonthPrediction"
        );


    const currentExpenseElement =
        document.getElementById(
            "currentMonthExpense"
        );


    const changeElement =
        document.getElementById(
            "predictionChange"
        );


    const messageElement =
        document.getElementById(
            "predictionMessage"
        );


    if (!predictionElement) {

        return;

    }


    const email =
        getUserEmail();


    if (!email) {

        predictionElement.textContent =
            "Unavailable";


        if (messageElement) {

            messageElement.textContent =
                "User email was not found. Please login again.";

        }


        return;

    }


    predictionElement.textContent =
        "Calculating...";


    if (messageElement) {

        messageElement.textContent =
            "Analyzing your expense history...";

    }


    if (changeElement) {

        changeElement.textContent =
            "--";

    }


    try {

        const response =
            await fetch(
                `/api/ml/predict?userEmail=${encodeURIComponent(email)}`,
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json",

                        "Accept":
                            "application/json"

                    },

                    cache:
                        "no-store",

                    body:
                        JSON.stringify({

                            userEmail:
                                email,

                            email:
                                email

                        })

                }
            );


        const result =
            await response.json();


        console.log(
            "Prediction response:",
            result
        );


        if (
            !response.ok ||
            result.success !== true
        ) {

            throw new Error(

                result.message ||
                result.error ||
                `Prediction API failed: ${response.status}`

            );

        }


        const prediction =
            Number(
                result.prediction ??
                result.predictedNextMonthExpenses
            );


        if (
            !Number.isFinite(
                prediction
            )
        ) {

            throw new Error(
                "Backend returned an invalid prediction."
            );

        }


        predictionElement.textContent =
            formatINR(
                prediction
            );


        const current =
            Number(
                result.currentMonthExpenses
            ) || 0;


        if (
            currentExpenseElement
        ) {

            currentExpenseElement.textContent =
                formatINR(
                    current
                );

        }


        const change =
            Number(
                result.expectedChangePercent
            );


        if (
            Number.isFinite(
                change
            )
        ) {

            const rounded =
                Math.abs(
                    change
                ).toFixed(1);


            if (
                change > 0
            ) {

                changeElement.textContent =
                    `↑ ${rounded}%`;


                changeElement.style.color =
                    "#EF4444";


                if (
                    messageElement
                ) {

                    messageElement.textContent =
                        "AI predicts higher expenses next month based on your spending pattern.";

                }

            }


            else if (
                change < 0
            ) {

                changeElement.textContent =
                    `↓ ${rounded}%`;


                changeElement.style.color =
                    "#10B981";


                if (
                    messageElement
                ) {

                    messageElement.textContent =
                        "AI predicts lower expenses next month based on your spending pattern.";

                }

            }


            else {

                changeElement.textContent =
                    "No Change";


                changeElement.style.color =
                    "#64748B";


                if (
                    messageElement
                ) {

                    messageElement.textContent =
                        "AI predicts spending similar to the current month.";

                }

            }

        }


        updateExplainableAI(
            result
        );


    } catch (error) {

        console.error(
            "Prediction error:",
            error
        );


        predictionElement.textContent =
            "Unavailable";


        if (
            messageElement
        ) {

            messageElement.textContent =
                error.message ||
                "Unable to generate prediction. Check the ML model and API.";

        }


        if (
            changeElement
        ) {

            changeElement.textContent =
                "--";

        }

    }

}


/* =====================================================
   EXPLAINABLE AI - SHAP
===================================================== */

function updateExplainableAI(
    result
) {

    const baseElement =
        document.getElementById(
            "shapBaseValue"
        );


    const predictionElement =
        document.getElementById(
            "shapPredictionValue"
        );


    const positiveElement =
        document.getElementById(
            "shapPositiveFactors"
        );


    const negativeElement =
        document.getElementById(
            "shapNegativeFactors"
        );


    if (
        !baseElement ||
        !predictionElement ||
        !positiveElement ||
        !negativeElement
    ) {

        console.warn(
            "SHAP Explainable AI elements not found."
        );

        return;

    }


    const baseValue =
        Number(
            result.shapBaseValue
        );


    const prediction =
        Number(
            result.prediction ??
            result.predictedNextMonthExpenses
        );


    const explanation =
        Array.isArray(
            result.shapExplanation
        )
            ? result.shapExplanation
            : [];


    if (
        Number.isFinite(
            baseValue
        )
    ) {

        baseElement.textContent =
            formatINR(
                baseValue
            );

    } else {

        baseElement.textContent =
            "--";

    }


    if (
        Number.isFinite(
            prediction
        )
    ) {

        predictionElement.textContent =
            formatINR(
                prediction
            );

    } else {

        predictionElement.textContent =
            "--";

    }


    if (
        explanation.length === 0
    ) {

        positiveElement.innerHTML = `

            <p class="xai-loading">

                SHAP explanation is not available.

            </p>

        `;


        negativeElement.innerHTML = `

            <p class="xai-loading">

                SHAP explanation is not available.

            </p>

        `;


        return;

    }


    const positiveFactors =
        explanation
            .filter(
                item =>
                    Number(
                        item.contribution
                    ) > 0
            )
            .sort(
                (a, b) =>
                    Number(
                        b.absoluteContribution
                    ) -
                    Number(
                        a.absoluteContribution
                    )
            )
            .slice(
                0,
                5
            );


    const negativeFactors =
        explanation
            .filter(
                item =>
                    Number(
                        item.contribution
                    ) < 0
            )
            .sort(
                (a, b) =>
                    Number(
                        b.absoluteContribution
                    ) -
                    Number(
                        a.absoluteContribution
                    )
            )
            .slice(
                0,
                5
            );


    if (
        positiveFactors.length
    ) {

        positiveElement.innerHTML =
            positiveFactors
                .map(
                    item =>
                        createShapFactor(
                            item,
                            "positive"
                        )
                )
                .join("");

    } else {

        positiveElement.innerHTML = `

            <p class="xai-loading">

                No factors are increasing the prediction.

            </p>

        `;

    }


    if (
        negativeFactors.length
    ) {

        negativeElement.innerHTML =
            negativeFactors
                .map(
                    item =>
                        createShapFactor(
                            item,
                            "negative"
                        )
                )
                .join("");

    } else {

        negativeElement.innerHTML = `

            <p class="xai-loading">

                No factors are decreasing the prediction.

            </p>

        `;

    }

}


/* =====================================================
   SHAP FACTOR
===================================================== */

function createShapFactor(
    item,
    type
) {

    const feature =
        String(
            item.feature ||
            ""
        );


    const contribution =
        Number(
            item.contribution
        ) || 0;


    const featureValue =
        Number(
            item.value
        ) || 0;


    const sign =
        contribution >= 0
            ? "+"
            : "−";


    const cssClass =
        type === "positive"
            ? "shap-positive"
            : "shap-negative";


    const icon =
        type === "positive"
            ? "fa-arrow-trend-up"
            : "fa-arrow-trend-down";


    return `

        <div class="shap-factor ${cssClass}">


            <div class="shap-factor-main">


                <div class="shap-factor-icon">

                    <i
                        class="fa-solid ${icon}">
                    </i>

                </div>


                <div class="shap-factor-info">

                    <strong>

                        ${escapeHTML(
                            formatShapFeatureName(
                                feature
                            )
                        )}

                    </strong>


                    <span>

                        Feature value:

                        ${formatShapValue(
                            feature,
                            featureValue
                        )}

                    </span>

                </div>

            </div>


            <div class="shap-contribution">

                ${sign}${formatINR(
                    Math.abs(
                        contribution
                    )
                )}

            </div>


        </div>

    `;

}


/* =====================================================
   SHAP FEATURE NAMES
===================================================== */

function formatShapFeatureName(
    feature
) {

    const names = {

        total_expenses:
            "Total Expenses",

        expense_transactions:
            "Expense Transactions",

        avg_expense:
            "Average Expense",

        max_expense:
            "Maximum Expense",

        total_income:
            "Total Income",

        monthly_budget:
            "Monthly Budget",

        monthly_income_reference:
            "Monthly Income Reference",

        savings:
            "Savings",

        previous_month_expenses:
            "Previous Month Expenses",

        previous_2_month_expenses:
            "Previous 2-Month Expenses",

        previous_3_month_expenses:
            "Previous 3-Month Expenses",

        three_month_avg_expenses:
            "3-Month Average Expenses",

        expense_change:
            "Expense Change",

        expense_change_pct:
            "Expense Change Percentage"

    };


    if (
        names[feature]
    ) {

        return names[feature];

    }


    return feature

        .replaceAll(
            "_",
            " "
        )

        .replace(
            /\b\w/g,
            char =>
                char.toUpperCase()
        );

}


/* =====================================================
   SHAP FEATURE VALUE
===================================================== */

function formatShapValue(
    feature,
    value
) {

    const moneyFeatures = [

        "total_expenses",

        "avg_expense",

        "max_expense",

        "total_income",

        "monthly_budget",

        "monthly_income_reference",

        "savings",

        "previous_month_expenses",

        "previous_2_month_expenses",

        "previous_3_month_expenses",

        "three_month_avg_expenses",

        "expense_change"

    ];


    if (
        moneyFeatures.includes(
            feature
        )
    ) {

        return formatINR(
            value
        );

    }


    if (
        feature ===
        "expense_change_pct"
    ) {

        return `${value.toFixed(2)}%`;

    }


    if (
        feature ===
        "expense_transactions"
    ) {

        return value.toLocaleString(
            "en-IN",
            {
                maximumFractionDigits: 0
            }
        );

    }


    return value.toLocaleString(
        "en-IN",
        {
            maximumFractionDigits: 2
        }
    );

}


/* =====================================================
   GET USER EMAIL
===================================================== */

function getUserEmail() {

    const keys = [

        "userEmail",

        "email",

        "user_email",

        "loggedInUserEmail",

        "user_email_address"

    ];


    const storages = [

        localStorage,

        sessionStorage

    ];


    for (
        const storage
        of storages
    ) {

        for (
            const key
            of keys
        ) {

            const value =
                storage.getItem(
                    key
                );


            if (
                value &&
                value !== "null" &&
                value !== "undefined"
            ) {

                return value
                    .trim()
                    .toLowerCase();

            }

        }

    }


    return "";

}


/* =====================================================
   FORMAT INR
===================================================== */

function formatINR(
    amount
) {

    return new Intl.NumberFormat(
        "en-IN",
        {

            style:
                "currency",

            currency:
                "INR",

            minimumFractionDigits:
                2,

            maximumFractionDigits:
                2

        }
    ).format(
        Number(amount) || 0
    );

}


/* =====================================================
   FORMAT MONTH
===================================================== */

function formatMonth(
    value
) {

    if (!value) {

        return "";

    }


    const parts =
        String(
            value
        ).split(
            "-"
        );


    if (
        parts.length < 2
    ) {

        return String(
            value
        );

    }


    const year =
        Number(
            parts[0]
        );


    const month =
        Number(
            parts[1]
        );


    const date =
        new Date(
            year,
            month - 1,
            1
        );


    return date.toLocaleDateString(
        "en-US",
        {

            month:
                "short",

            year:
                "numeric"

        }
    );

}


/* =====================================================
   ESCAPE HTML
===================================================== */

function escapeHTML(
    value
) {

    return String(
        value ?? ""
    )

        .replace(
            /&/g,
            "&amp;"
        )

        .replace(
            /</g,
            "&lt;"
        )

        .replace(
            />/g,
            "&gt;"
        )

        .replace(
            /"/g,
            "&quot;"
        )

        .replace(
            /'/g,
            "&#039;"
        );

}


/* =====================================================
   DYNAMIC CHART STYLES
===================================================== */

function addChartStyles() {

    if (
        document.getElementById(
            "smartspendAnalyticsDynamicStyles"
        )
    ) {

        return;

    }


    const style =
        document.createElement(
            "style"
        );


    style.id =
        "smartspendAnalyticsDynamicStyles";


    style.textContent = `

        .analytics-bar-chart {

            display: flex;

            align-items: flex-end;

            gap: 28px;

            min-height: 320px;

            overflow-x: auto;

            padding: 30px 24px 12px;

        }


        .bar-item {

            min-width: 82px;

            height: 260px;

            display: flex;

            flex-direction: column;

            justify-content: flex-end;

            align-items: center;

            position: relative;

        }


        .bar-value {

            font-size: 12px;

            font-weight: 700;

            margin-bottom: 8px;

            white-space: nowrap;

        }


        .bar {

            width: 56px;

            min-height: 8px;

            background: #2563EB;

            border-radius: 9px 9px 0 0;

        }


        .bar-label {

            font-size: 12px;

            margin-top: 9px;

            white-space: nowrap;

        }


        .category-chart {

            padding: 18px 8px;

        }


        .category-item {

            margin-bottom: 18px;

        }


        .category-header {

            display: flex;

            justify-content: space-between;

            gap: 10px;

            margin-bottom: 8px;

        }


        .category-progress {

            height: 12px;

            background: #e8edf5;

            border-radius: 20px;

            overflow: hidden;

        }


        .category-progress-fill {

            height: 100%;

            background: #2563EB;

            border-radius: 20px;

        }


        .category-item small {

            display: block;

            text-align: center;

            margin-top: 6px;

            color: #64748b;

        }


        .widget-body {

            padding: 12px 0;

        }


        .insights-list {

            display: flex;

            flex-direction: column;

            gap: 12px;

        }


        .insight-item {

            display: flex;

            gap: 12px;

            padding: 14px;

            border-radius: 12px;

            background: #f8fafc;

        }


        .insight-icon {

            width: 36px;

            height: 36px;

            border-radius: 10px;

            display: flex;

            align-items: center;

            justify-content: center;

            flex-shrink: 0;

        }


        .insight-item.success
        .insight-icon {

            background: #ecfdf5;

            color: #10b981;

        }


        .insight-item.warning
        .insight-icon {

            background: #fffbeb;

            color: #f59e0b;

        }


        .insight-item.danger
        .insight-icon {

            background: #fef2f2;

            color: #ef4444;

        }


        .insight-item.info
        .insight-icon {

            background: #eff6ff;

            color: #2563eb;

        }


        .insight-content h4 {

            margin: 0 0 4px;

        }


        .insight-content p {

            margin: 0;

            color: #64748b;

            line-height: 1.5;

        }

    `;


    document.head.appendChild(
        style
    );

}