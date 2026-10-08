from flask import Blueprint, request, jsonify
from database.db import expenses, income
from datetime import datetime
from collections import defaultdict


analytics = Blueprint(
    "analytics",
    __name__
)


# =========================================================
# SAFE FLOAT
# =========================================================

def safe_float(value):
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


# =========================================================
# MONTH RANGE
# =========================================================

def get_month_range(year, month):
    start_date = f"{year:04d}-{month:02d}-01"

    if month == 12:
        next_year = year + 1
        next_month = 1
    else:
        next_year = year
        next_month = month + 1

    end_date = (
        f"{next_year:04d}-{next_month:02d}-01"
    )

    return start_date, end_date


# =========================================================
# PREVIOUS MONTH
# =========================================================

def previous_month(year, month):
    if month == 1:
        return year - 1, 12

    return year, month - 1


# =========================================================
# FINANCIAL HEALTH SCORE
# =========================================================

def calculate_financial_health(
    total_income,
    total_expenses,
    previous_expenses
):
    health_explanation = []

    if total_income <= 0:
        return {
            "score": None,
            "label": "Not Available",
            "expenseRatio": 0.0,
            "savingsRate": 0.0,
            "savingsScore": 0,
            "budgetScore": 0,
            "trendScore": 0,
            "stabilityScore": 0,
            "explanation": [
                "Add income to calculate your Financial Health Score."
            ]
        }

    total_savings = (
        total_income -
        total_expenses
    )

    savings_rate = (
        total_savings /
        total_income
    ) * 100.0

    expense_ratio = (
        total_expenses /
        total_income
    ) * 100.0

    # -----------------------------------------------------
    # SAVINGS - 30 POINTS
    # -----------------------------------------------------

    if savings_rate >= 30:
        savings_score = 30
        health_explanation.append(
            "Excellent savings rate."
        )

    elif savings_rate >= 20:
        savings_score = 25
        health_explanation.append(
            "Healthy savings rate."
        )

    elif savings_rate >= 10:
        savings_score = 18
        health_explanation.append(
            "Moderate savings rate."
        )

    elif savings_rate >= 0:
        savings_score = 10
        health_explanation.append(
            "Savings rate could be improved."
        )

    else:
        savings_score = 0
        health_explanation.append(
            "Expenses are higher than income."
        )

    # -----------------------------------------------------
    # EXPENSE CONTROL - 30 POINTS
    # -----------------------------------------------------

    if expense_ratio <= 60:
        budget_score = 30

    elif expense_ratio <= 70:
        budget_score = 25

    elif expense_ratio <= 80:
        budget_score = 20

    elif expense_ratio <= 90:
        budget_score = 12

    elif expense_ratio <= 100:
        budget_score = 5

    else:
        budget_score = 0

    if expense_ratio <= 70:
        health_explanation.append(
            "Expenses are well controlled relative to income."
        )

    elif expense_ratio <= 90:
        health_explanation.append(
            "Expenses are taking a significant portion of income."
        )

    else:
        health_explanation.append(
            "Expenses are very high compared with income."
        )

    # -----------------------------------------------------
    # SPENDING TREND - 20 POINTS
    # -----------------------------------------------------

    if previous_expenses > 0:

        spending_change = (
            (
                total_expenses -
                previous_expenses
            )
            /
            previous_expenses
        ) * 100.0

        if spending_change <= -10:
            trend_score = 20
            health_explanation.append(
                "Spending decreased compared with last month."
            )

        elif spending_change <= 0:
            trend_score = 17
            health_explanation.append(
                "Spending is stable or slightly lower."
            )

        elif spending_change <= 10:
            trend_score = 13
            health_explanation.append(
                "Spending has increased slightly."
            )

        elif spending_change <= 25:
            trend_score = 8
            health_explanation.append(
                "Spending has increased noticeably."
            )

        else:
            trend_score = 3
            health_explanation.append(
                "Spending has increased significantly."
            )

    else:

        spending_change = 0.0
        trend_score = 15

        health_explanation.append(
            "Not enough previous-month data for a strong trend comparison."
        )

    # -----------------------------------------------------
    # FINANCIAL STABILITY - 20 POINTS
    # -----------------------------------------------------

    if savings_rate >= 20:
        stability_score = 20

    elif savings_rate >= 0:
        stability_score = 15

    else:
        stability_score = 5

    # -----------------------------------------------------
    # FINAL SCORE
    # -----------------------------------------------------

    financial_score = (
        savings_score +
        budget_score +
        trend_score +
        stability_score
    )

    financial_score = max(
        0,
        min(
            100,
            financial_score
        )
    )

    # -----------------------------------------------------
    # LABEL
    # -----------------------------------------------------

    if financial_score >= 80:
        financial_label = "Excellent"

    elif financial_score >= 65:
        financial_label = "Good"

    elif financial_score >= 50:
        financial_label = "Fair"

    else:
        financial_label = "Needs Attention"

    return {
        "score": financial_score,
        "label": financial_label,
        "expenseRatio": round(
            expense_ratio,
            2
        ),
        "savingsRate": round(
            savings_rate,
            2
        ),
        "spendingChange": round(
            spending_change,
            2
        ),
        "savingsScore": savings_score,
        "budgetScore": budget_score,
        "trendScore": trend_score,
        "stabilityScore": stability_score,
        "explanation": health_explanation
    }


# =========================================================
# ANALYTICS
# =========================================================

@analytics.route(
    "/analytics",
    methods=["GET"]
)
def get_analytics():

    try:

        user_email = request.args.get(
            "userEmail"
        )

        month = request.args.get(
            "month"
        )

        if not user_email:
            return jsonify({
                "success": False,
                "message": "User email is required."
            }), 400

        user_email = (
            str(user_email)
            .strip()
            .lower()
        )

        # -------------------------------------------------
        # SELECTED MONTH
        # -------------------------------------------------

        if not month:
            month = datetime.now().strftime(
                "%Y-%m"
            )

        try:
            selected_date = datetime.strptime(
                month,
                "%Y-%m"
            )

        except ValueError:
            return jsonify({
                "success": False,
                "message": "Invalid month format. Use YYYY-MM."
            }), 400

        year = selected_date.year
        month_number = selected_date.month

        start_date, end_date = get_month_range(
            year,
            month_number
        )

        # -------------------------------------------------
        # PREVIOUS MONTH
        # -------------------------------------------------

        previous_year, previous_month_number = previous_month(
            year,
            month_number
        )

        previous_start, previous_end = get_month_range(
            previous_year,
            previous_month_number
        )

        # -------------------------------------------------
        # CURRENT MONTH EXPENSES
        # -------------------------------------------------

        current_expenses = list(
            expenses.find({
                "userEmail": user_email,
                "date": {
                    "$gte": start_date,
                    "$lt": end_date
                }
            })
        )

        # -------------------------------------------------
        # CURRENT MONTH INCOME
        # -------------------------------------------------

        current_income = list(
            income.find({
                "userEmail": user_email,
                "date": {
                    "$gte": start_date,
                    "$lt": end_date
                }
            })
        )

        # -------------------------------------------------
        # PREVIOUS MONTH EXPENSES
        # -------------------------------------------------

        previous_expense_data = list(
            expenses.find({
                "userEmail": user_email,
                "date": {
                    "$gte": previous_start,
                    "$lt": previous_end
                }
            })
        )

        # -------------------------------------------------
        # PREVIOUS MONTH INCOME
        # -------------------------------------------------

        previous_income_data = list(
            income.find({
                "userEmail": user_email,
                "date": {
                    "$gte": previous_start,
                    "$lt": previous_end
                }
            })
        )

        # -------------------------------------------------
        # TOTALS
        # -------------------------------------------------

        total_expenses = sum(
            safe_float(
                item.get("amount", 0)
            )
            for item in current_expenses
        )

        total_income = sum(
            safe_float(
                item.get("amount", 0)
            )
            for item in current_income
        )

        previous_expenses = sum(
            safe_float(
                item.get("amount", 0)
            )
            for item in previous_expense_data
        )

        previous_income = sum(
            safe_float(
                item.get("amount", 0)
            )
            for item in previous_income_data
        )

        # -------------------------------------------------
        # SAVINGS
        # -------------------------------------------------

        total_savings = (
            total_income -
            total_expenses
        )

        if total_income > 0:
            savings_rate = (
                total_savings /
                total_income
            ) * 100.0
        else:
            savings_rate = 0.0

        # -------------------------------------------------
        # CATEGORIES
        # -------------------------------------------------

        categories = defaultdict(float)

        for item in current_expenses:

            category = (
                item.get(
                    "category",
                    "Others"
                )
                or "Others"
            )

            categories[
                str(category)
            ] += safe_float(
                item.get("amount", 0)
            )

        # -------------------------------------------------
        # PAYMENT METHODS
        # -------------------------------------------------

        payment_methods = defaultdict(float)

        for item in current_expenses:

            payment = (
                item.get(
                    "payment",
                    item.get(
                        "paymentMethod",
                        "Unknown"
                    )
                )
                or "Unknown"
            )

            payment_methods[
                str(payment)
            ] += safe_float(
                item.get("amount", 0)
            )

        # -------------------------------------------------
        # MONTHLY TREND
        # -------------------------------------------------

        monthly_totals = defaultdict(float)

        all_expenses = list(
            expenses.find({
                "userEmail": user_email
            })
        )

        for item in all_expenses:

            date_value = str(
                item.get(
                    "date",
                    ""
                )
            )[:10]

            if len(date_value) >= 7:

                month_key = date_value[:7]

                monthly_totals[
                    month_key
                ] += safe_float(
                    item.get(
                        "amount",
                        0
                    )
                )

        monthly_trend = []

        for month_key in sorted(
            monthly_totals
        ):

            monthly_trend.append({
                "month": month_key,
                "amount": round(
                    monthly_totals[
                        month_key
                    ],
                    2
                )
            })

        # -------------------------------------------------
        # TRANSACTION STATISTICS
        # -------------------------------------------------

        transaction_count = len(
            current_expenses
        )

        if transaction_count > 0:
            average_transaction = (
                total_expenses /
                transaction_count
            )
        else:
            average_transaction = 0.0

        if current_expenses:
            highest_expense = max(
                safe_float(
                    item.get(
                        "amount",
                        0
                    )
                )
                for item in current_expenses
            )

            lowest_expense = min(
                safe_float(
                    item.get(
                        "amount",
                        0
                    )
                )
                for item in current_expenses
            )

        else:
            highest_expense = 0.0
            lowest_expense = 0.0

        # -------------------------------------------------
        # SPENDING CHANGE
        # -------------------------------------------------

        if previous_expenses > 0:

            spending_change = (
                (
                    total_expenses -
                    previous_expenses
                )
                /
                previous_expenses
            ) * 100.0

        else:
            spending_change = 0.0

        # -------------------------------------------------
        # FINANCIAL HEALTH
        # -------------------------------------------------

        health = calculate_financial_health(
            total_income,
            total_expenses,
            previous_expenses
        )

        # -------------------------------------------------
        # AI INSIGHTS
        # -------------------------------------------------

        ai_insights = []

        if total_income <= 0:

            ai_insights.append({
                "type": "warning",
                "title": "Add your income",
                "message": (
                    "Add your monthly income so "
                    "SmartSpend AI can calculate "
                    "your savings rate and "
                    "financial health score."
                )
            })

        else:

            if savings_rate >= 30:

                ai_insights.append({
                    "type": "success",
                    "title": "Excellent savings",
                    "message": (
                        f"You are saving "
                        f"{savings_rate:.1f}% "
                        "of your income this month."
                    )
                })

            elif savings_rate >= 20:

                ai_insights.append({
                    "type": "success",
                    "title": "Healthy savings",
                    "message": (
                        f"Your current savings rate "
                        f"is {savings_rate:.1f}%."
                    )
                })

            elif savings_rate >= 0:

                ai_insights.append({
                    "type": "warning",
                    "title": "Increase your savings",
                    "message": (
                        f"Your savings rate is "
                        f"{savings_rate:.1f}%."
                    )
                })

            else:

                ai_insights.append({
                    "type": "danger",
                    "title": "Spending exceeds income",
                    "message": (
                        "Your expenses are higher "
                        "than your income this month."
                    )
                })

            if categories and total_expenses > 0:

                top_category = max(
                    categories,
                    key=categories.get
                )

                top_amount = categories[
                    top_category
                ]

                category_percentage = (
                    top_amount /
                    total_expenses
                ) * 100.0

                ai_insights.append({
                    "type": "info",
                    "title": "Largest spending category",
                    "message": (
                        f"{top_category} is your largest "
                        f"expense category at "
                        f"{category_percentage:.1f}% "
                        "of total spending."
                    )
                })

            if previous_expenses > 0:

                if spending_change > 20:

                    ai_insights.append({
                        "type": "warning",
                        "title": "Spending increased",
                        "message": (
                            f"Your spending increased by "
                            f"{spending_change:.1f}% "
                            "compared with last month."
                        )
                    })

                elif spending_change < -20:

                    ai_insights.append({
                        "type": "success",
                        "title": "Spending improved",
                        "message": (
                            f"Your spending decreased by "
                            f"{abs(spending_change):.1f}% "
                            "compared with last month."
                        )
                    })

        # -------------------------------------------------
        # DEBUG
        # -------------------------------------------------

        print("\n==========================================")
        print("SMARTSPEND ANALYTICS")
        print("User:", user_email)
        print("Month:", month)
        print("Income:", total_income)
        print("Expenses:", total_expenses)
        print("Savings:", total_savings)
        print("Savings Rate:", savings_rate)
        print("Previous Expenses:", previous_expenses)
        print("Spending Change:", spending_change)
        print("Financial Score:", health["score"])
        print("Financial Label:", health["label"])
        print("==========================================\n")

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return jsonify({

            "success": True,

            "month": month,

            "totalIncome": round(
                total_income,
                2
            ),

            "totalExpenses": round(
                total_expenses,
                2
            ),

            "totalSavings": round(
                total_savings,
                2
            ),

            "savingsRate": round(
                savings_rate,
                2
            ),

            "financialScore":
                health["score"],

            "financialLabel":
                health["label"],

            "healthExplanation":
                health["explanation"],

            "expenseRatio":
                health["expenseRatio"],

            "healthBreakdown": {
                "savingsScore":
                    health["savingsScore"],
                "budgetScore":
                    health["budgetScore"],
                "trendScore":
                    health["trendScore"],
                "stabilityScore":
                    health["stabilityScore"]
            },

            "transactionCount":
                transaction_count,

            "averageTransaction":
                round(
                    average_transaction,
                    2
                ),

            "highestExpense":
                round(
                    highest_expense,
                    2
                ),

            "lowestExpense":
                round(
                    lowest_expense,
                    2
                ),

            "previousMonthExpenses":
                round(
                    previous_expenses,
                    2
                ),

            "previousMonthIncome":
                round(
                    previous_income,
                    2
                ),

            "spendingChange":
                round(
                    spending_change,
                    2
                ),

            "categories": {
                key: round(
                    value,
                    2
                )
                for key, value
                in categories.items()
            },

            "paymentMethods": {
                key: round(
                    value,
                    2
                )
                for key, value
                in payment_methods.items()
            },

            "monthlyTrend":
                monthly_trend,

            "aiInsights":
                ai_insights

        }), 200

    except Exception as error:

        print(
            "ANALYTICS ERROR:",
            error
        )

        return jsonify({
            "success": False,
            "message": "Unable to generate analytics.",
            "error": str(error)
        }), 500
