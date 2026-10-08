# =========================================================
# SMARTSPEND AI
# ML PREDICTION ROUTE
# =========================================================
#
# File:
# backend/routes/ml_prediction.py
#
# Purpose:
# - Load Extra Trees spending model
# - Fetch user expenses from MongoDB
# - Fetch user income from MongoDB
# - Calculate monthly spending features
# - Predict next month's expenses
# - Return prediction to Analytics / Reports frontend
#
# =========================================================


# =========================================================
# IMPORTS
# =========================================================

from flask import Blueprint, request, jsonify

import os
import joblib
import pandas as pd
import shap
from datetime import datetime, date


# =========================================================
# DATABASE
# =========================================================

from database.db import expenses, income, budgets


# =========================================================
# BLUEPRINT
# =========================================================

ml_prediction = Blueprint(
    "ml_prediction",
    __name__
)


# =========================================================
# MODEL PATH
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


MODEL_PATH = os.path.join(
    BASE_DIR,
    "ml_models",
    "extra_trees_spending_model.joblib"
)


# =========================================================
# DEFAULT MODEL FEATURES
# =========================================================
#
# These are the features used by the SmartSpend
# spending prediction model.
#
# If the saved model contains feature_names_in_,
# those names are used automatically.
#
# =========================================================

DEFAULT_MODEL_FEATURES = [

    "total_expenses",

    "expense_transactions",

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

    "expense_change",

    "expense_change_pct"

]


# =========================================================
# MODEL VARIABLES
# =========================================================

model = None

features = []

model_load_error = None


# =========================================================
# LOAD ML MODEL
# =========================================================

try:

    print("\n")
    print("=" * 60)
    print("SMARTSPEND AI - LOADING ML MODEL")
    print("=" * 60)

    print(
        "Model path:",
        MODEL_PATH
    )

    if not os.path.exists(MODEL_PATH):

        raise FileNotFoundError(
            f"Model file not found: {MODEL_PATH}"
        )


    model_bundle = joblib.load(
        MODEL_PATH
    )


    # -----------------------------------------------------
    # MODEL BUNDLE
    # -----------------------------------------------------

    if isinstance(
        model_bundle,
        dict
    ):

        model = model_bundle.get(
            "model"
        )

        features = (
            model_bundle.get(
                "features",
                []
            )
            or []
        )

    else:

        model = model_bundle

        features = []


    # -----------------------------------------------------
    # GET FEATURES FROM MODEL
    # -----------------------------------------------------

    if (
        model is not None
        and hasattr(
            model,
            "feature_names_in_"
        )
    ):

        features = list(
            model.feature_names_in_
        )


    # -----------------------------------------------------
    # FALLBACK FEATURES
    # -----------------------------------------------------

    if (
        model is not None
        and not features
    ):

        features = (
            DEFAULT_MODEL_FEATURES.copy()
        )


    # -----------------------------------------------------
    # MODEL INFORMATION
    # -----------------------------------------------------

    print(
        "Model loaded:",
        model is not None
    )

    print(
        "Model type:",
        (
            type(model).__name__
            if model is not None
            else "None"
        )
    )

    print(
        "Features:",
        features
    )

    print(
        "Feature count:",
        len(features)
    )

    print(
        "Model n_features_in_:",
        getattr(
            model,
            "n_features_in_",
            None
        )
    )

    print("=" * 60)
    print("SMARTSPEND AI ML MODEL READY")
    print("=" * 60)
    print()


except Exception as error:

    model_load_error = str(
        error
    )

    model = None

    features = []

    print("\n")
    print("=" * 60)
    print("SMARTSPEND AI ML MODEL LOAD ERROR")
    print("=" * 60)

    print(
        type(error).__name__,
        ":",
        error
    )

    print(
        "Model path:",
        MODEL_PATH
    )

    print("=" * 60)
    print()


# =========================================================
# SAFE FLOAT
# =========================================================

def safe_float(value):

    try:

        if value is None:
            return 0.0

        if value == "":
            return 0.0

        if isinstance(
            value,
            bool
        ):
            return 0.0

        return float(
            value
        )

    except (
        TypeError,
        ValueError
    ):

        return 0.0


# =========================================================
# PARSE DATE
# =========================================================
#
# Supports:
#
# YYYY-MM-DD
# YYYY-MM-DDTHH:MM:SS
# ISO datetime
# Python datetime
# Python date
#
# =========================================================

def parse_date(value):

    if value is None:
        return None


    try:

        if isinstance(
            value,
            datetime
        ):

            return value


        if isinstance(
            value,
            date
        ):

            return datetime(
                value.year,
                value.month,
                value.day
            )


        text = str(
            value
        ).strip()


        if not text:
            return None


        # -------------------------------------------------
        # ISO DATE
        # -------------------------------------------------

        if "T" in text:

            try:

                return datetime.fromisoformat(
                    text.replace(
                        "Z",
                        "+00:00"
                    )
                ).replace(
                    tzinfo=None
                )

            except Exception:

                pass


        # -------------------------------------------------
        # YYYY-MM-DD
        # -------------------------------------------------

        return datetime.strptime(
            text[:10],
            "%Y-%m-%d"
        )


    except (
        TypeError,
        ValueError
    ):

        return None


# =========================================================
# GET USER EMAIL
# =========================================================
#
# Accepts:
#
# {
#     "userEmail": "..."
# }
#
# OR
#
# {
#     "email": "..."
# }
#
# OR
#
# {
#     "user_email": "..."
# }
#
# Also accepts query parameters.
#
# =========================================================

def get_user_email():

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )


    if not isinstance(
        data,
        dict
    ):

        data = {}


    email = (

        data.get(
            "userEmail"
        )

        or data.get(
            "email"
        )

        or data.get(
            "user_email"
        )

        or request.args.get(
            "userEmail"
        )

        or request.args.get(
            "email"
        )

        or request.args.get(
            "user_email"
        )

    )


    if not email:

        return None


    email = str(
        email
    ).strip().lower()


    if not email:

        return None


    return email


# =========================================================
# GET USER EXPENSES
# =========================================================

def get_user_expenses(
    user_email
):

    records = []


    try:

        # -------------------------------------------------
        # PRIMARY QUERY
        # -------------------------------------------------

        cursor = expenses.find({
            "userEmail": user_email
        })


        for item in cursor:

            amount = safe_float(
                item.get(
                    "amount",
                    0
                )
            )


            # -------------------------------------------------
            # DATE
            # -------------------------------------------------

            raw_date = (
                item.get(
                    "date"
                )
                or item.get(
                    "expenseDate"
                )
                or item.get(
                    "createdAt"
                )
            )


            parsed_date = parse_date(
                raw_date
            )


            if (
                amount > 0
                and parsed_date
            ):

                records.append({

                    "amount":
                        amount,

                    "date":
                        parsed_date

                })


    except Exception as error:

        print(
            "EXPENSE FETCH ERROR:",
            type(error).__name__,
            error
        )


    return records


# =========================================================
# GET USER INCOME
# =========================================================

def get_user_income(
    user_email
):

    records = []


    try:

        cursor = income.find({
            "userEmail": user_email
        })


        for item in cursor:

            amount = safe_float(
                item.get(
                    "amount",
                    0
                )
            )


            raw_date = (
                item.get(
                    "date"
                )
                or item.get(
                    "incomeDate"
                )
                or item.get(
                    "createdAt"
                )
            )


            parsed_date = parse_date(
                raw_date
            )


            if (
                amount > 0
                and parsed_date
            ):

                records.append({

                    "amount":
                        amount,

                    "date":
                        parsed_date

                })


    except Exception as error:

        print(
            "INCOME FETCH ERROR:",
            type(error).__name__,
            error
        )


    return records


# =========================================================
# MONTHLY EXPENSE
# =========================================================

def monthly_expense(
    expense_records,
    year,
    month
):

    total = 0.0


    for item in expense_records:

        item_date = item.get(
            "date"
        )


        if not item_date:
            continue


        if (
            item_date.year == year
            and item_date.month == month
        ):

            total += safe_float(
                item.get(
                    "amount",
                    0
                )
            )


    return total


# =========================================================
# MONTHLY INCOME
# =========================================================

def monthly_income(
    income_records,
    year,
    month
):

    total = 0.0


    for item in income_records:

        item_date = item.get(
            "date"
        )


        if not item_date:
            continue


        if (
            item_date.year == year
            and item_date.month == month
        ):

            total += safe_float(
                item.get(
                    "amount",
                    0
                )
            )


    return total


# =========================================================
# PREVIOUS MONTH
# =========================================================

def previous_month(
    year,
    month
):

    if month == 1:

        return (
            year - 1,
            12
        )


    return (
        year,
        month - 1
    )


# =========================================================
# GET MONTH LABEL
# =========================================================

def month_label(
    year,
    month
):

    try:

        return datetime(
            year,
            month,
            1
        ).strftime(
            "%b %Y"
        )

    except Exception:

        return f"{year}-{month:02d}"


# =========================================================
# BUILD ML FEATURES
# =========================================================

def build_features(
    expense_records,
    income_records,
    user_email
):

    today = datetime.now()


    current_year = (
        today.year
    )

    current_month = (
        today.month
    )


    # =====================================================
    # CURRENT MONTH
    # =====================================================

    current_expenses = monthly_expense(

        expense_records,

        current_year,

        current_month

    )


    # =====================================================
    # PREVIOUS MONTH
    # =====================================================

    prev_year, prev_month = previous_month(

        current_year,

        current_month

    )


    previous_expenses = monthly_expense(

        expense_records,

        prev_year,

        prev_month

    )


    # =====================================================
    # TWO MONTHS AGO
    # =====================================================

    prev2_year, prev2_month = previous_month(

        prev_year,

        prev_month

    )


    previous_2_month_expenses = monthly_expense(

        expense_records,

        prev2_year,

        prev2_month

    )


    # =====================================================
    # THREE MONTHS AGO
    # =====================================================

    prev3_year, prev3_month = previous_month(

        prev2_year,

        prev2_month

    )


    previous_3_month_expenses = monthly_expense(

        expense_records,

        prev3_year,

        prev3_month

    )


    # =====================================================
    # TOTAL EXPENSES
    # =====================================================

    total_expenses = sum(

        safe_float(
            item.get(
                "amount",
                0
            )
        )

        for item in expense_records

    )


    # =====================================================
    # TRANSACTIONS
    # =====================================================

    expense_transactions = len(
        expense_records
    )


    # =====================================================
    # AVERAGE EXPENSE
    # =====================================================

    if expense_transactions > 0:

        avg_expense = (

            total_expenses
            /
            expense_transactions

        )

    else:

        avg_expense = 0.0


    # =====================================================
    # MAX EXPENSE
    # =====================================================

    if expense_records:

        max_expense = max(

            safe_float(
                item.get(
                    "amount",
                    0
                )
            )

            for item in expense_records

        )

    else:

        max_expense = 0.0


    # =====================================================
    # TOTAL INCOME
    # =====================================================

    total_income = sum(

        safe_float(
            item.get(
                "amount",
                0
            )
        )

        for item in income_records

    )


    # =====================================================
    # CURRENT MONTH INCOME
    # =====================================================

    monthly_income_reference = monthly_income(

        income_records,

        current_year,

        current_month

    )


    # =====================================================
    # THREE MONTH AVERAGE
    # =====================================================

    three_month_avg_expenses = (

        previous_expenses

        +

        previous_2_month_expenses

        +

        previous_3_month_expenses

    ) / 3.0


    # =====================================================
    # EXPENSE CHANGE
    # =====================================================

    expense_change = (

        current_expenses

        -

        previous_expenses

    )


    # =====================================================
    # EXPENSE CHANGE %
    # =====================================================

    if previous_expenses > 0:

        expense_change_pct = (

            expense_change
            /
            previous_expenses

        ) * 100.0

    else:

        expense_change_pct = 0.0


    # =====================================================
    # SAVINGS
    # =====================================================

    savings = (

        monthly_income_reference

        -

        current_expenses

    )


    # =====================================================
    # MONTHLY BUDGET
    # =====================================================

    monthly_budget = 0.0


    try:

        budget_record = budgets.find_one({

            "userEmail":
                user_email

        })


        if budget_record:

            monthly_budget = safe_float(

                budget_record.get(

                    "monthlyBudget",

                    budget_record.get(

                        "amount",

                        budget_record.get(

                            "budget",

                            0

                        )

                    )

                )

            )


    except Exception as error:

        print(
            "BUDGET FETCH ERROR:",
            type(error).__name__,
            error
        )


    # =====================================================
    # RETURN FEATURES
    # =====================================================

    return {

        "total_expenses":
            total_expenses,

        "expense_transactions":
            expense_transactions,

        "avg_expense":
            avg_expense,

        "max_expense":
            max_expense,

        "total_income":
            total_income,

        "monthly_budget":
            monthly_budget,

        "monthly_income_reference":
            monthly_income_reference,

        "savings":
            savings,

        "previous_month_expenses":
            previous_expenses,

        "previous_2_month_expenses":
            previous_2_month_expenses,

        "previous_3_month_expenses":
            previous_3_month_expenses,

        "three_month_avg_expenses":
            three_month_avg_expenses,

        "expense_change":
            expense_change,

        "expense_change_pct":
            expense_change_pct

    }


# =========================================================
# CREATE MODEL INPUT
# =========================================================

def create_model_input(
    feature_data
):

    # -----------------------------------------------------
    # DETERMINE MODEL FEATURES
    # -----------------------------------------------------

    if features:

        model_features = list(
            features
        )

    else:

        model_features = (
            DEFAULT_MODEL_FEATURES.copy()
        )


    # -----------------------------------------------------
    # CREATE ROW
    # -----------------------------------------------------

    row = {}


    for feature in model_features:

        row[feature] = safe_float(

            feature_data.get(

                feature,

                0.0

            )

        )


    # -----------------------------------------------------
    # DATAFRAME
    # -----------------------------------------------------

    X = pd.DataFrame(

        [row],

        columns=model_features

    )


    return (
        X,
        model_features
    )


# =========================================================
# PREDICT NEXT MONTH
# =========================================================

@ml_prediction.route(
    "/ml/predict",
    methods=[
        "POST",
        "OPTIONS"
    ]
)
def predict_next_month_expense():

    # =====================================================
    # PREFLIGHT
    # =====================================================

    if request.method == "OPTIONS":

        return jsonify({

            "success":
                True

        }), 200


    try:

        # =================================================
        # CHECK MODEL
        # =================================================

        if model is None:

            print(
                "PREDICTION ERROR: MODEL NOT LOADED"
            )

            return jsonify({

                "success":
                    False,

                "message":
                    "ML model is not loaded.",

                "error":
                    model_load_error,

                "modelPath":
                    MODEL_PATH

            }), 500


        # =================================================
        # REQUEST DATA
        # =================================================

        request_data = (

            request.get_json(
                silent=True
            )

            or {}

        )


        print("\n")
        print("=" * 60)
        print("SMARTSPEND AI PREDICTION REQUEST")
        print("=" * 60)

        print(
            "Request data:",
            request_data
        )

        print(
            "Request method:",
            request.method
        )

        print(
            "Content-Type:",
            request.content_type
        )


        # =================================================
        # USER EMAIL
        # =================================================

        user_email = get_user_email()


        print(
            "User email:",
            repr(user_email)
        )


        if not user_email:

            print(
                "ERROR: USER EMAIL NOT RECEIVED"
            )

            return jsonify({

                "success":
                    False,

                "message":
                    "User email is required for prediction.",

                "error":
                    "MISSING_USER_EMAIL"

            }), 400


        # =================================================
        # FETCH EXPENSES
        # =================================================

        expense_records = get_user_expenses(

            user_email

        )


        # =================================================
        # FETCH INCOME
        # =================================================

        income_records = get_user_income(

            user_email

        )


        print(
            "Expense records:",
            len(expense_records)
        )

        print(
            "Income records:",
            len(income_records)
        )


        # =================================================
        # NO EXPENSE DATA
        # =================================================

        if len(expense_records) == 0:

            return jsonify({

                "success":
                    False,

                "message":
                    "No expense records found for this user.",

                "error":
                    "NO_EXPENSE_DATA",

                "prediction":
                    None,

                "currentMonthExpenses":
                    0,

                "previousMonthExpenses":
                    0,

                "threeMonthAverage":
                    0,

                "expectedChangePercent":
                    0,

                "transactionCount":
                    0

            }), 200


        # =================================================
        # BUILD FEATURES
        # =================================================

        feature_data = build_features(

            expense_records,

            income_records,

            user_email

        )


        print("\nFEATURE DATA")
        print("-" * 60)


        for key, value in feature_data.items():

            print(
                f"{key}: {value}"
            )


        # =================================================
        # MODEL INPUT
        # =================================================

        X, model_features = create_model_input(

            feature_data

        )


        print("\nMODEL FEATURES")
        print("-" * 60)

        print(
            model_features
        )


        print("\nMODEL INPUT")
        print("-" * 60)

        print(
            X.to_string(
                index=False
            )
        )


        # =================================================
        # MODEL FEATURE COUNT
        # =================================================

        expected_count = getattr(

            model,

            "n_features_in_",

            None

        )


        print(
            "Expected feature count:",
            expected_count
        )

        print(
            "Provided feature count:",
            len(model_features)
        )


        if (

            expected_count is not None

            and

            expected_count != len(
                model_features
            )

        ):

            print(
                "ERROR: FEATURE COUNT MISMATCH"
            )


            return jsonify({

                "success":
                    False,

                "message":
                    "ML model feature configuration does not match the backend.",

                "error":
                    "FEATURE_COUNT_MISMATCH",

                "expectedFeatures":
                    expected_count,

                "providedFeatures":
                    len(model_features),

                "featuresUsed":
                    model_features

            }), 500


        # =================================================
        # PREDICTION
        # =================================================

        print("\nRUNNING EXTRA TREES PREDICTION...")


        prediction_result = model.predict(
            X
        )


        prediction = prediction_result[0]


        prediction = safe_float(
            prediction
        )


        # Never allow negative predicted expenses

        prediction = max(
            0.0,
            prediction
        )


        print(
            "Raw prediction:",
            prediction
        )




        # =================================================
        # SHAP EXPLAINABLE AI
        # =================================================

        shap_explanation = []
        shap_base_value = None

        try:
            print("\nCALCULATING SHAP EXPLANATION...")

            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X)

            if isinstance(shap_values, list):
                shap_row = shap_values[0][0]
            else:
                shap_row = shap_values[0]

            base_value = explainer.expected_value

            if hasattr(base_value, "__len__"):
                base_value = base_value[0]

            shap_base_value = safe_float(base_value)

            for index, feature_name in enumerate(model_features):

                feature_value = safe_float(
                    X.iloc[0][feature_name]
                )

                contribution = safe_float(
                    shap_row[index]
                )

                if contribution > 0:
                    direction = "increases_prediction"

                elif contribution < 0:
                    direction = "decreases_prediction"

                else:
                    direction = "neutral"

                shap_explanation.append({
                    "feature": feature_name,
                    "value": round(feature_value, 2),
                    "contribution": round(contribution, 2),
                    "absoluteContribution": round(
                        abs(contribution),
                        2
                    ),
                    "direction": direction
                })

            shap_explanation.sort(
                key=lambda item: item["absoluteContribution"],
                reverse=True
            )

            print(
                "SHAP BASE VALUE:",
                shap_base_value
            )

            print("SHAP EXPLANATION:")
            print(shap_explanation)

        except Exception as shap_error:

            print(
                "SHAP ERROR:",
                type(shap_error).__name__,
                ":",
                shap_error
            )

            shap_explanation = []
            shap_base_value = None
        
            
        now = datetime.now()
        # =================================================
        # CURRENT MONTH EXPENSES
        # =================================================

        current_month_expenses = monthly_expense(

            expense_records,

            now.year,

            now.month

        )


        # =================================================
        # PREVIOUS MONTH
        # =================================================

        previous_year, previous_month_number = previous_month(

            now.year,

            now.month

        )


        previous_month_expenses = monthly_expense(

            expense_records,

            previous_year,

            previous_month_number

        )


        # =================================================
        # TWO MONTHS AGO
        # =================================================

        previous_2_year, previous_2_month = previous_month(

            previous_year,

            previous_month_number

        )


        previous_2_month_expenses = monthly_expense(

            expense_records,

            previous_2_year,

            previous_2_month

        )


        # =================================================
        # THREE MONTHS AGO
        # =================================================

        previous_3_year, previous_3_month = previous_month(

            previous_2_year,

            previous_2_month

        )


        previous_3_month_expenses = monthly_expense(

            expense_records,

            previous_3_year,

            previous_3_month

        )


        # =================================================
        # THREE MONTH AVERAGE
        # =================================================

        three_month_average = (

            previous_month_expenses

            +

            previous_2_month_expenses

            +

            previous_3_month_expenses

        ) / 3.0


        # =================================================
        # EXPECTED CHANGE
        # =================================================

        if current_month_expenses > 0:

            change_percent = (

                (

                    prediction

                    -

                    current_month_expenses

                )

                /

                current_month_expenses

            ) * 100.0

        else:

            change_percent = 0.0


        # =================================================
        # SAVINGS
        # =================================================

        current_month_income = monthly_income(

            income_records,

            now.year,

            now.month

        )


        current_month_savings = (

            current_month_income

            -

            current_month_expenses

        )


        # =================================================
        # PREDICTION MONTH
        # =================================================

        prediction_year, prediction_month = previous_month(

            now.year,

            now.month

        )


        # The prediction is NEXT month,
        # so calculate it separately.

        if now.month == 12:

            prediction_year = (
                now.year + 1
            )

            prediction_month = 1

        else:

            prediction_year = (
                now.year
            )

            prediction_month = (
                now.month + 1
            )


        prediction_month_name = month_label(

            prediction_year,

            prediction_month

        )


        # =================================================
        # RESPONSE
        # =================================================

        response = {

            "success":
                True,

            "model":
                "Extra Trees Regressor",
                    "shapBaseValue":
        (
            round(
                shap_base_value,
                2
            )
            if shap_base_value is not None
            else None
        ),

    "shapExplanation":
        shap_explanation,

            "prediction":
                round(
                    prediction,
                    2
                ),

            "predictedNextMonthExpenses":
                round(
                    prediction,
                    2
                ),

            "predictionMonth":
                prediction_month_name,

            "currentMonthExpenses":
                round(
                    current_month_expenses,
                    2
                ),

            "previousMonthExpenses":
                round(
                    previous_month_expenses,
                    2
                ),

            "previous2MonthExpenses":
                round(
                    previous_2_month_expenses,
                    2
                ),

            "previous3MonthExpenses":
                round(
                    previous_3_month_expenses,
                    2
                ),

            "threeMonthAverage":
                round(
                    three_month_average,
                    2
                ),

            "expectedChangePercent":
                round(
                    change_percent,
                    2
                ),

            "currentMonthIncome":
                round(
                    current_month_income,
                    2
                ),

            "currentMonthSavings":
                round(
                    current_month_savings,
                    2
                ),

            "transactionCount":
                len(
                    expense_records
                ),

            "expenseTransactions":
                len(
                    expense_records
                ),

            "incomeTransactions":
                len(
                    income_records
                ),

            "target":
                "Next Month Expenses",

            "featuresUsed":
                model_features

        }


        # =================================================
        # TERMINAL OUTPUT
        # =================================================

        print("\n")
        print("=" * 60)
        print("SMARTSPEND AI PREDICTION RESULT")
        print("=" * 60)

        print(
            "User:",
            user_email
        )

        print(
            "Current month:",
            round(
                current_month_expenses,
                2
            )
        )

        print(
            "Previous month:",
            round(
                previous_month_expenses,
                2
            )
        )

        print(
            "3 month average:",
            round(
                three_month_average,
                2
            )
        )

        print(
            "Predicted next month:",
            round(
                prediction,
                2
            )
        )

        print(
            "Expected change:",
            round(
                change_percent,
                2
            ),
            "%"
        )

        print(
            "Transactions:",
            len(
                expense_records
            )
        )

        print(
            "Prediction month:",
            prediction_month_name
        )

        print("=" * 60)
        print()


        # =================================================
        # SEND RESPONSE
        # =================================================

        return jsonify(
            response
        ), 200


    # =====================================================
    # GENERAL ERROR
    # =====================================================

    except Exception as error:

        print("\n")
        print("=" * 60)
        print("SMARTSPEND AI ML PREDICTION ERROR")
        print("=" * 60)

        print(
            "Error type:",
            type(error).__name__
        )

        print(
            "Error:",
            str(error)
        )

        print("=" * 60)
        print()


        return jsonify({

            "success":
                False,

            "message":
                "Unable to generate prediction.",

            "error":
                str(error)

        }), 500


# =========================================================
# ML TEST ENDPOINT
# =========================================================

@ml_prediction.route(
    "/ml/test",
    methods=[
        "GET"
    ]
)
def test_ml():

    return jsonify({

        "success":
            True,

        "modelLoaded":
            model is not None,

        "model":
            (
                type(model).__name__
                if model is not None
                else None
            ),

        "features":
            features,

        "featureCount":
            len(features),

        "expectedFeatureCount":
            getattr(
                model,
                "n_features_in_",
                None
            ),

        "modelPath":
            MODEL_PATH,

        "modelExists":
            os.path.exists(
                MODEL_PATH
            ),

        "modelLoadError":
            model_load_error

    }), 200


# =========================================================
# ML DEBUG ENDPOINT
# =========================================================
#
# Open:
#
# http://127.0.0.1:5000/api/ml/debug
#
# This helps confirm whether the model itself is loaded.
#
# =========================================================

@ml_prediction.route(
    "/ml/debug",
    methods=[
        "GET"
    ]
)
def debug_ml():

    return jsonify({

        "success":
            True,

        "status":
            (
                "ready"
                if model is not None
                else "error"
            ),

        "modelLoaded":
            model is not None,

        "modelType":
            (
                type(model).__name__
                if model is not None
                else None
            ),

        "modelPath":
            MODEL_PATH,

        "modelExists":
            os.path.exists(
                MODEL_PATH
            ),

        "features":
            features,

        "featureCount":
            len(features),

        "modelExpectedFeatures":
            getattr(
                model,
                "n_features_in_",
                None
            ),

        "loadError":
            model_load_error

    }), 200


# =========================================================
# END OF FILE
# =========================================================