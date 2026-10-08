// ============================================================
// SMARTSPEND AI - DASHBOARD.JS
// FINAL CLEAN VERSION
// ============================================================

document.addEventListener("DOMContentLoaded", function () {

    console.log("====================================");
    console.log("SMARTSPEND AI DASHBOARD LOADED");
    console.log("====================================");

    setupSidebar();
    setupSearch();
    setupNotifications();
    setupProfile();

    loadDashboardData();
});


// ============================================================
// LOAD DASHBOARD DATA
// ============================================================

async function loadDashboardData() {

    const userEmail =
        localStorage.getItem("userEmail") ||
        localStorage.getItem("email") ||
        localStorage.getItem("user_email");

    console.log("Dashboard User:", userEmail);

    if (!userEmail) {

        console.error(
            "Dashboard: User email not found in localStorage."
        );

        showDashboardEmpty();

        return;
    }


    const now = new Date();

    const year = now.getFullYear();

    const month =
        String(now.getMonth() + 1).padStart(2, "0");

    const selectedMonth =
        `${year}-${month}`;


    const apiURL =
        `http://127.0.0.1:5000/api/analytics` +
        `?userEmail=${encodeURIComponent(userEmail)}` +
        `&month=${selectedMonth}`;


    console.log("Dashboard API:");
    console.log(apiURL);


    try {

        const response =
            await fetch(apiURL, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json"
                }
            });


        console.log(
            "Dashboard API Status:",
            response.status
        );


        if (!response.ok) {

            throw new Error(
                `API returned status ${response.status}`
            );
        }


        const data =
            await response.json();


        console.log(
            "===================================="
        );

        console.log(
            "DASHBOARD DATA RECEIVED:"
        );

        console.log(data);

        console.log(
            "===================================="
        );


        // ----------------------------------------
        // UPDATE ALL DASHBOARD SECTIONS
        // ----------------------------------------

        updateSummaryCards(data);

        updateFinancialHealth(data);

        updateAIInsight(data);
        updateDashboardMonthlyTrend(data.monthlyTrend);
        
        updateDashboardCategories(data.categories);

        updateSpendingAnalytics(data);

        updateMonthlyBudget(data);

        updateRecentTransactions(data);

        updateUpcomingBills(data);


    }

    catch (error) {

        console.error(
            "===================================="
        );

        console.error(
            "DASHBOARD ERROR:",
            error
        );

        console.error(
            "===================================="
        );

        showDashboardEmpty();
    }
}


// ============================================================
// SUMMARY CARDS
// ============================================================

function updateSummaryCards(data) {

    const cards =
        document.querySelectorAll(
            ".cards-grid .card"
        );


    if (!cards.length) {

        console.warn(
            "Summary cards not found."
        );

        return;
    }


    /*
       HTML ORDER:

       0 = Current Balance
       1 = Total Income
       2 = Total Expenses
       3 = Savings
    */


    // ----------------------------------------
    // CURRENT BALANCE
    // ----------------------------------------

    const balance =
        getNumber(
            data.currentBalance,
            data.balance,
            data.totalSavings,
            0
        );


    setCardText(
        cards[0],
        formatCurrency(balance)
    );


    // ----------------------------------------
    // TOTAL INCOME
    // ----------------------------------------

    const income =
        getNumber(
            data.totalIncome,
            data.income,
            0
        );


    setCardText(
        cards[1],
        formatCurrency(income)
    );


    // ----------------------------------------
    // TOTAL EXPENSES
    // ----------------------------------------

    const expenses =
        getNumber(
            data.totalExpenses,
            data.expenses,
            data.totalExpense,
            0
        );


    setCardText(
        cards[2],
        formatCurrency(expenses)
    );


    // ----------------------------------------
    // SAVINGS
    // ----------------------------------------

    const savings =
        income - expenses;


    setCardText(
        cards[3],
        formatCurrency(savings)
    );


    console.log(
        "SUMMARY:",
        {
            balance: balance,
            income: income,
            expenses: expenses,
            savings: savings
        }
    );
}


// ============================================================
// FINANCIAL HEALTH
// ============================================================

function updateFinancialHealth(data) {

    const scoreCircle =
        document.querySelector(
            ".score-circle"
        );


    if (!scoreCircle) {

        console.warn(
            "Financial health score circle not found."
        );

        return;
    }


    const income =
        getNumber(
            data.totalIncome,
            data.income,
            0
        );


    const expenses =
        getNumber(
            data.totalExpenses,
            data.expenses,
            data.totalExpense,
            0
        );


    /*
       IMPORTANT:

       Do NOT blindly use another count from the API.

       Financial health is calculated ONLY from:
       income + expenses.

       This prevents transaction count,
       category count, etc. from appearing
       as the health score.
    */


    if (income <= 0) {

        scoreCircle.textContent = "--";

        updateHealthText(
            "Waiting for Analysis",
            "Add income and expenses to generate your Financial Health Score."
        );

        return;
    }


    // ----------------------------------------
    // CALCULATE SAVINGS RATE
    // ----------------------------------------

    const savings =
        income - expenses;


    const savingsRate =
        (savings / income) * 100;


    // ----------------------------------------
    // EXPENSE RATIO
    // ----------------------------------------

    const expenseRatio =
        (expenses / income) * 100;


    // ----------------------------------------
    // HEALTH SCORE
    // ----------------------------------------

    let score = 100;


    // Spending above income
    if (expenses > income) {

        score -= 40;

    }

    else if (expenseRatio > 90) {

        score -= 30;

    }

    else if (expenseRatio > 80) {

        score -= 20;

    }

    else if (expenseRatio > 70) {

        score -= 10;
    }


    // Savings
    if (savingsRate >= 30) {

        score += 0;

    }

    else if (savingsRate >= 20) {

        score -= 5;

    }

    else if (savingsRate >= 10) {

        score -= 10;

    }

    else if (savingsRate > 0) {

        score -= 15;

    }

    else {

        score -= 20;
    }


    // Keep score between 0 and 100
    score =
        Math.max(
            0,
            Math.min(
                100,
                Math.round(score)
            )
        );


    scoreCircle.textContent =
        score;


    // ----------------------------------------
    // MESSAGE
    // ----------------------------------------

    let title =
        "Needs Attention";

    let message =
        "Your spending pattern needs attention.";


    if (score >= 80) {

        title =
            "Excellent";

        message =
            "Your income and spending pattern are well balanced.";
    }

    else if (score >= 65) {

        title =
            "Good";

        message =
            "Your financial position is generally healthy.";
    }

    else if (score >= 50) {

        title =
            "Fair";

        message =
            "Consider reducing unnecessary expenses and increasing savings.";
    }


    updateHealthText(
        title,
        message
    );


    console.log(
        "FINANCIAL HEALTH:",
        {
            income: income,
            expenses: expenses,
            savings: savings,
            expenseRatio: expenseRatio,
            savingsRate: savingsRate,
            score: score
        }
    );
}


// ============================================================
// HEALTH TEXT
// ============================================================

function updateHealthText(
    title,
    message
) {

    const scoreCircle =
        document.querySelector(
            ".score-circle"
        );


    if (!scoreCircle) {
        return;
    }


    const widget =
        scoreCircle.closest(
            ".dashboard-widget"
        );


    if (!widget) {
        return;
    }


    const heading =
        widget.querySelector(
            "h4"
        );


    const paragraph =
        widget.querySelector(
            "p"
        );


    if (heading) {

        heading.textContent =
            title;
    }


    if (paragraph) {

        paragraph.textContent =
            message;
    }
}


// ============================================================
// AI FINANCIAL INSIGHT
// ============================================================

function updateAIInsight(data) {

    const widget =
        document.querySelector(
            ".ai-widget"
        );


    if (!widget) {

        console.log(
            "AI widget not found."
        );

        return;
    }


    const body =
        widget.querySelector(
            ".widget-body"
        );


    if (!body) {
        return;
    }


    const insights =
        data.aiInsights ||
        data.insights ||
        [];


    if (
        Array.isArray(insights) &&
        insights.length > 0
    ) {

        let html = "";


        insights.forEach(
            function (insight) {

                html += `

                    <div class="ai-insight">

                        <h4>
                            🤖
                            ${escapeHtml(
                                insight.title ||
                                "AI Financial Insight"
                            )}
                        </h4>

                        <p>
                            ${escapeHtml(
                                insight.message ||
                                "SmartSpend AI analyzed your financial activity."
                            )}
                        </p>

                    </div>

                `;
            }
        );


        body.innerHTML =
            html;

        return;
    }


    body.innerHTML = `

        <div class="empty-state">

            <i class="fa-solid fa-robot"></i>

            <h4>
                No AI Insights Yet
            </h4>

            <p>
                Add your income and expenses.
                SmartSpend AI will analyze your
                financial habits and generate
                personalized insights.
            </p>

        </div>

    `;
}


// ============================================================
// SPENDING ANALYTICS
// ============================================================

function updateSpendingAnalytics(data) {

    const analytics =
        document.querySelector(
            ".spending-analytics"
        );


    if (!analytics) {
        return;
    }


    const expenses =
        getNumber(
            data.totalExpenses,
            data.expenses,
            0
        );


    if (expenses <= 0) {

        analytics.innerHTML = `

            <div class="empty-state">

                <i class="fa-solid fa-chart-line"></i>

                <h4>
                    No Analytics Available
                </h4>

                <p>
                    Your charts will appear here
                    once expenses are recorded.
                </p>

            </div>

        `;

        return;
    }


    analytics.innerHTML = `

        <div class="empty-state">

            <i class="fa-solid fa-chart-line"></i>

            <h4>
                Spending Analysis
            </h4>

            <p>
                Total spending this month:
                <strong>
                    ${formatCurrency(expenses)}
                </strong>
            </p>

        </div>

    `;
}


// ============================================================
// MONTHLY BUDGET
// ============================================================

function updateMonthlyBudget(data) {

    const budget =
        document.querySelector(
            ".monthly-budget"
        );


    if (!budget) {
        return;
    }


    const budgetAmount =
        getNumber(
            data.monthlyBudget,
            data.budget,
            0
        );


    const expenses =
        getNumber(
            data.totalExpenses,
            data.expenses,
            0
        );


    if (budgetAmount <= 0) {

        budget.innerHTML = `

            <div class="empty-state">

                <h4>
                    Monthly Budget
                </h4>

                <p>
                    Create your first budget
                    to begin tracking.
                </p>

            </div>

        `;

        return;
    }


    const percentage =
        Math.min(
            100,
            Math.round(
                (expenses / budgetAmount) * 100
            )
        );


    budget.innerHTML = `

        <div class="widget-header">

            <h3>
                Monthly Budget
            </h3>

        </div>

        <div class="progress">

            <div
                class="progress-fill"
                style="width:${percentage}%;">
            </div>

        </div>

        <p>
            ${formatCurrency(expenses)}
            /
            ${formatCurrency(budgetAmount)}
        </p>

        <p>
            ${percentage}% used
        </p>

    `;
}


// ============================================================
// RECENT TRANSACTIONS
// ============================================================

function updateRecentTransactions(data) {

    const container =
        document.querySelector(
            ".recent-transactions"
        );


    if (!container) {
        return;
    }


    const transactions =
        data.recentTransactions ||
        data.transactions ||
        [];


    if (
        !Array.isArray(transactions) ||
        transactions.length === 0
    ) {

        container.innerHTML = `

            <div class="empty-state">

                <i class="fa-solid fa-folder-open"></i>

                <h4>
                    No Transactions
                </h4>

                <p>
                    Your latest transactions
                    will be displayed here.
                </p>

            </div>

        `;

        return;
    }


    let html = "";


    transactions
        .slice(0, 5)
        .forEach(
            function (transaction) {

                const title =
                    transaction.title ||
                    transaction.description ||
                    transaction.category ||
                    "Transaction";


                const amount =
                    getNumber(
                        transaction.amount,
                        0
                    );


                html += `

                    <div class="transaction-row">

                        <div>

                            <strong>
                                ${escapeHtml(title)}
                            </strong>

                        </div>

                        <div>
                            ${formatCurrency(amount)}
                        </div>

                    </div>

                `;
            }
        );


    container.innerHTML =
        html;
}


// ============================================================
// UPCOMING BILLS
// ============================================================

function updateUpcomingBills(data) {

    const container =
        document.querySelector(
            ".upcoming-bills"
        );


    if (!container) {
        return;
    }


    const bills =
        data.upcomingBills ||
        data.bills ||
        [];


    if (
        !Array.isArray(bills) ||
        bills.length === 0
    ) {

        container.innerHTML = `

            <div class="empty-state">

                <i class="fa-solid fa-calendar"></i>

                <h4>
                    No Bills Added
                </h4>

                <p>
                    Bills and reminders
                    will appear here.
                </p>

            </div>

        `;

        return;
    }


    let html = "";


    bills.slice(0, 5)
        .forEach(
            function (bill) {

                html += `

                    <div class="bill-row">

                        <strong>
                            ${escapeHtml(
                                bill.title ||
                                bill.name ||
                                "Bill"
                            )}
                        </strong>

                        <span>
                            ${formatCurrency(
                                getNumber(
                                    bill.amount,
                                    0
                                )
                            )}
                        </span>

                    </div>

                `;
            }
        );


    container.innerHTML =
        html;
}


// ============================================================
// EMPTY DASHBOARD
// ============================================================

function showDashboardEmpty() {

    const cards =
        document.querySelectorAll(
            ".cards-grid .card"
        );


    cards.forEach(
        function (card) {

            const element =
                card.querySelector(
                    ".empty-text"
                );


            if (element) {

                element.textContent =
                    "No data available.";
            }
        }
    );


    const score =
        document.querySelector(
            ".score-circle"
        );


    if (score) {

        score.textContent =
            "--";
    }
}


// ============================================================
// CARD TEXT
// ============================================================

function setCardText(
    card,
    text
) {

    if (!card) {
        return;
    }


    const element =
        card.querySelector(
            ".empty-text"
        );


    if (element) {

        element.textContent =
            text;
    }
}


// ============================================================
// SAFE NUMBER
// ============================================================

function getNumber() {

    const values =
        Array.from(arguments);


    for (
        let i = 0;
        i < values.length;
        i++
    ) {

        const value =
            Number(values[i]);


        if (
            Number.isFinite(value)
        ) {

            return value;
        }
    }


    return 0;
}


// ============================================================
// CURRENCY
// ============================================================

function formatCurrency(
    amount
) {

    return new Intl.NumberFormat(
        "en-IN",
        {
            style: "currency",
            currency: "INR",
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }
    ).format(
        Number(amount) || 0
    );
}


// ============================================================
// SIDEBAR
// ============================================================

function setupSidebar() {

    const items =
        document.querySelectorAll(
            ".sidebar-menu li"
        );


    items.forEach(
        function (item) {

            item.addEventListener(
                "click",
                function () {

                    items.forEach(
                        function (i) {

                            i.classList.remove(
                                "active"
                            );
                        }
                    );


                    item.classList.add(
                        "active"
                    );
                }
            );
        }
    );
}


// ============================================================
// SEARCH
// ============================================================

function setupSearch() {

    const search =
        document.querySelector(
            ".search-box input"
        );


    if (!search) {
        return;
    }


    search.addEventListener(
        "keyup",
        function () {

            console.log(
                "Searching:",
                this.value
            );

        }
    );
}


// ============================================================
// NOTIFICATIONS
// ============================================================

function setupNotifications() {

    const button =
        document.querySelector(
            ".notification-btn"
        );


    if (!button) {
        return;
    }


    button.addEventListener(
        "click",
        function () {

            alert(
                "No notifications available."
            );

        }
    );
}


// ============================================================
// PROFILE
// ============================================================

function setupProfile() {

    const profile =
        document.querySelector(
            ".avatar"
        );


    if (!profile) {
        return;
    }


    profile.addEventListener(
        "click",
        function () {

            window.location.href =
                "profile.html";

        }
    );
}


// ============================================================
// HTML SAFETY
// ============================================================

function escapeHtml(value) {

    return String(value)

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
// ==========================================
// DASHBOARD MONTHLY SPENDING TREND
// ==========================================

function updateDashboardMonthlyTrend(
    monthlyTrend
) {

    const placeholders =
        document.querySelectorAll(
            ".chart-placeholder"
        );

    if (!placeholders.length) {
        return;
    }

    const chartBox =
        placeholders[0];

    if (
        !monthlyTrend ||
        monthlyTrend.length === 0
    ) {

        return;
    }

    const maxAmount =
        Math.max(
            ...monthlyTrend.map(
                item =>
                    Number(item.amount) || 0
            )
        );

    let html = `
        <div class="analytics-bar-chart">
    `;

    monthlyTrend.forEach(
        item => {

            const amount =
                Number(item.amount) || 0;

            let height = 5;

            if (maxAmount > 0) {

                height =
                    Math.max(
                        (
                            amount /
                            maxAmount
                        ) * 100,
                        5
                    );

            }

            html += `
                <div class="bar-item">

                    <div class="bar-value">
                        ${formatCurrency(amount)}
                    </div>

                    <div
                        class="bar"
                        style="height:${height}%"
                    ></div>

                    <div class="bar-label">
                        ${formatDashboardMonth(
                            item.month
                        )}
                    </div>

                </div>
            `;
        }
    );

    html += `
        </div>
    `;

    chartBox.innerHTML = html;
}


// ==========================================
// DASHBOARD CATEGORIES
// ==========================================

function updateDashboardCategories(
    categories
) {

    const placeholders =
        document.querySelectorAll(
            ".chart-placeholder"
        );

    if (placeholders.length < 2) {
        return;
    }

    const categoryBox =
        placeholders[1];

    if (
        !categories ||
        Object.keys(categories).length === 0
    ) {

        return;
    }

    const sortedCategories =
        Object.entries(categories)
        .sort(
            (a, b) =>
                Number(b[1]) -
                Number(a[1])
        );

    const total =
        sortedCategories.reduce(
            (sum, item) =>
                sum +
                Number(item[1]),
            0
        );

    let html = `
        <div class="category-chart">
    `;

    sortedCategories.forEach(
        ([category, amount]) => {

            const numericAmount =
                Number(amount) || 0;

            const percentage =
                total > 0
                    ? (
                        numericAmount /
                        total
                    ) * 100
                    : 0;

            html += `
                <div class="category-item">

                    <div class="category-header">

                        <span>
                            ${escapeHtml(category)}
                        </span>

                        <strong>
                            ${formatCurrency(
                                numericAmount
                            )}
                        </strong>

                    </div>

                    <div class="category-progress">

                        <div
                            class="category-progress-fill"
                            style="
                                width:${percentage}%
                            "
                        ></div>

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

    categoryBox.innerHTML = html;
}


// ==========================================
// MONTH FORMAT
// ==========================================

function formatDashboardMonth(
    value
) {

    if (!value) {
        return "";
    }

    const parts =
        String(value).split("-");

    if (parts.length !== 2) {
        return value;
    }

    const year =
        Number(parts[0]);

    const month =
        Number(parts[1]);

    const date =
        new Date(
            year,
            month - 1,
            1
        );

    return date.toLocaleDateString(
        "en-IN",
        {
            month: "short",
            year: "numeric"
        }
    );
}