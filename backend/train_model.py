# ============================================================
# SMARTSPEND AI
# TRAIN NEXT MONTH EXPENSE PREDICTION MODEL
# ============================================================

import os
import sys
import joblib
import pandas as pd
import numpy as np

from sklearn.ensemble import ExtraTreesRegressor

# Make backend imports work
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.db import expenses


# ============================================================
# MODEL PATH
# ============================================================

MODEL_DIR = os.path.join(
    BASE_DIR,
    "ml_models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "extra_trees_spending_model.joblib"
)

os.makedirs(MODEL_DIR, exist_ok=True)


# ============================================================
# DATE FIELD DETECTION
# ============================================================

DATE_FIELDS = [
    "date",
    "expenseDate",
    "transactionDate",
    "createdAt",
    "created_at"
]


# ============================================================
# AMOUNT FIELD DETECTION
# ============================================================

AMOUNT_FIELDS = [
    "amount",
    "Amount",
    "expenseAmount",
    "value"
]


# ============================================================
# GET VALUE
# ============================================================

def get_first_value(document, fields):

    for field in fields:

        if field in document:

            value = document[field]

            if value is not None:
                return value

    return None


# ============================================================
# CONVERT DATE
# ============================================================

def convert_date(value):

    if value is None:
        return None

    try:

        return pd.to_datetime(
            value,
            errors="coerce"
        )

    except Exception:

        return None


# ============================================================
# LOAD EXPENSE DATA
# ============================================================

def load_expenses():

    documents = list(
        expenses.find({})
    )

    rows = []

    for document in documents:

        amount = get_first_value(
            document,
            AMOUNT_FIELDS
        )

        date_value = get_first_value(
            document,
            DATE_FIELDS
        )

        if amount is None:
            continue

        if date_value is None:
            continue

        try:

            amount = float(amount)

        except:

            continue

        if amount <= 0:
            continue

        date_value = convert_date(
            date_value
        )

        if pd.isna(date_value):
            continue

        rows.append({

            "date": date_value,

            "amount": amount

        })

    return pd.DataFrame(rows)


# ============================================================
# CREATE MONTHLY DATA
# ============================================================

def create_monthly_data(df):

    if df.empty:

        return pd.DataFrame()

    df["month"] = (
        df["date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    monthly = (
        df
        .groupby("month")
        .agg(
            monthly_expense=("amount", "sum"),
            transaction_count=("amount", "count")
        )
        .reset_index()
        .sort_values("month")
    )

    return monthly


# ============================================================
# CREATE TRAINING DATA
# ============================================================

def create_training_data(monthly):

    if len(monthly) < 3:

        return None, None

    rows = []

    targets = []

    # --------------------------------------------------------
    # Each row predicts the following month.
    #
    # Example:
    #
    # July + August -> September
    # August + September -> October
    # --------------------------------------------------------

    for i in range(2, len(monthly)):

        previous_2 = float(
            monthly.iloc[i - 2]["monthly_expense"]
        )

        previous_1 = float(
            monthly.iloc[i - 1]["monthly_expense"]
        )

        current = float(
            monthly.iloc[i]["monthly_expense"]
        )

        previous_count = int(
            monthly.iloc[i - 1]["transaction_count"]
        )

        current_count = int(
            monthly.iloc[i]["transaction_count"]
        )

        average_3_month = (
            previous_2 +
            previous_1 +
            current
        ) / 3

        trend = current - previous_1

        rows.append({

            "previous_month_expense":
                previous_1,

            "previous_2_month_expense":
                previous_2,

            "current_month_expense":
                current,

            "average_3_month_expense":
                average_3_month,

            "expense_trend":
                trend,

            "previous_month_transactions":
                previous_count,

            "current_month_transactions":
                current_count

        })

        # The target is the NEXT month.
        #
        # We can only create a target when the next month
        # actually exists in the database.

        if i + 1 < len(monthly):

            targets.append(
                float(
                    monthly.iloc[i + 1]["monthly_expense"]
                )
            )

        else:

            # Last row has no known next month.
            # Remove it from training rows.
            rows.pop()

    if not rows:

        return None, None

    X = pd.DataFrame(rows)

    y = np.array(targets)

    return X, y


# ============================================================
# TRAIN MODEL
# ============================================================

def train_model():

    print()
    print("=" * 60)
    print("SMARTSPEND AI - MODEL TRAINING")
    print("=" * 60)

    # --------------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------------

    df = load_expenses()

    print(
        f"Expense records found: {len(df)}"
    )

    if df.empty:

        print()
        print(
            "ERROR: No usable expense records found."
        )

        print(
            "Make sure your expenses collection contains:"
        )

        print(
            "- amount"
        )

        print(
            "- date / expenseDate / transactionDate"
        )

        return

    # --------------------------------------------------------
    # MONTHLY DATA
    # --------------------------------------------------------

    monthly = create_monthly_data(
        df
    )

    print()
    print("MONTHLY EXPENSE HISTORY")
    print("-" * 60)

    for _, row in monthly.iterrows():

        print(
            f"{row['month'].strftime('%B %Y'):15}"
            f" ₹{row['monthly_expense']:,.2f}"
            f"  Transactions: "
            f"{int(row['transaction_count'])}"
        )

    print("-" * 60)

    # --------------------------------------------------------
    # CHECK MONTH COUNT
    # --------------------------------------------------------

    if len(monthly) < 3:

        print()
        print(
            "ERROR: At least 3 different months "
            "of expense data are required."
        )

        print(
            "Add more monthly expense history "
            "before training the model."
        )

        return

    # --------------------------------------------------------
    # TRAINING DATA
    # --------------------------------------------------------

    X, y = create_training_data(
        monthly
    )

    if X is None or len(X) == 0:

        print()
        print(
            "ERROR: Not enough monthly history "
            "to create training samples."
        )

        return

    print()
    print(
        f"Training samples: {len(X)}"
    )

    print(
        f"Features: {list(X.columns)}"
    )

    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    model = ExtraTreesRegressor(

        n_estimators=300,

        random_state=42,

        min_samples_leaf=1,

        max_features=1.0

    )

    model.fit(
        X,
        y
    )

    # --------------------------------------------------------
    # SAVE MODEL
    # --------------------------------------------------------

    model_bundle = {

        "model":
            model,

        "features":
            list(X.columns),

        "description":
            "SmartSpend AI next month expense prediction",

        "training_months":
            len(monthly),

        "training_samples":
            len(X)

    }

    joblib.dump(
        model_bundle,
        MODEL_PATH
    )

    print()
    print("=" * 60)

    print(
        "MODEL TRAINING COMPLETED"
    )

    print(
        f"Model saved to:"
    )

    print(
        MODEL_PATH
    )

    print("=" * 60)

    print()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    train_model()