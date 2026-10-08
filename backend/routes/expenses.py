from flask import Blueprint, request, jsonify
from database.db import expenses
from bson import ObjectId
from pypdf import PdfReader
from io import BytesIO
from datetime import datetime
import re
import pdfplumber

expense = Blueprint("expense", __name__)

# Compatibility name used by app.py
expenses_bp = expense


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def detect_category(title):
    """
    Automatically classify a transaction into a meaningful
    spending category using merchant / narration keywords.
    """

    text = str(title or "").lower().strip()

    # Normalize common separators
    text = re.sub(r"[_\-/*|]+", " ", text)
    text = re.sub(r"\s+", " ", text)

    # =========================================================
    # FOOD
    # =========================================================
    food_keywords = [
        "swiggy", "zomato", "dominos", "domino's", "pizza",
        "mcdonald", "mcd", "kfc", "burger king", "subway",
        "starbucks", "restaurant", "restro", "cafe", "coffee",
        "tea", "bakery", "bake", "food", "canteen", "mess",
        "dining", "dine", "eatery", "biryani", "juice",
        "foodpanda", "ubereats", "eatclub", "box8",
        "faasos", "behrouz", "ovenstory", "freshmenu",
        "haldiram", "barbeque", "dominos"
    ]

    if any(word in text for word in food_keywords):
        return "Food"

    # =========================================================
    # SHOPPING
    # =========================================================
    shopping_keywords = [
        "amazon", "amzn", "flipkart", "myntra", "meesho",
        "ajio", "nykaa", "snapdeal", "tata cliq",
        "reliance trends", "reliance digital",
        "dmart", "big bazaar", "walmart", "target",
        "shopping", "mall", "retail", "store",
        "market", "supermarket", "mart", "fashion",
        "clothing", "garments", "electronics",
        "lifestyle", "decathlon"
    ]

    if any(word in text for word in shopping_keywords):
        return "Shopping"

    # =========================================================
    # TRANSPORT
    # =========================================================
    transport_keywords = [
        "uber", "ola", "rapido", "auto", "cab",
        "taxi", "metro", "bus", "railway",
        "train", "irctc", "transport",
        "ride", "parking", "toll", "fastag",
        "parking fee"
    ]

    if any(word in text for word in transport_keywords):
        return "Transport"

    # =========================================================
    # FUEL
    # =========================================================
    fuel_keywords = [
        "petrol", "fuel", "diesel", "hpcl",
        "bpcl", "iocl", "indian oil",
        "bharat petroleum", "hindustan petroleum",
        "shell", "reliance petroleum",
        "essar", "nayara", "petrol pump",
        "fuel station", "gas station"
    ]

    if any(word in text for word in fuel_keywords):
        return "Fuel"

    # =========================================================
    # TRAVEL
    # =========================================================
    travel_keywords = [
        "flight", "airlines", "air india",
        "indigo", "spicejet", "vistara",
        "akasa", "goair", "travel",
        "makemytrip", "mmt", "cleartrip",
        "booking.com", "agoda", "oyo",
        "hotel", "resort", "holiday",
        "trip", "yatra", "redbus"
    ]

    if any(word in text for word in travel_keywords):
        return "Travel"

    # =========================================================
    # BILLS & UTILITIES
    # =========================================================
    bills_keywords = [
        "electricity", "electric", "power bill",
        "water bill", "gas bill", "lpg",
        "recharge", "mobile recharge",
        "mobile bill", "phone bill",
        "airtel", "jio", "vi ", "vodafone",
        "bsnl", "broadband", "wifi",
        "internet", "fiber", "dth",
        "tataplay", "dish tv", "electricity board",
        "bescom", "msedcl", "tneb", "torrent power"
    ]

    if any(word in text for word in bills_keywords):
        return "Bills"

    # =========================================================
    # MEDICAL
    # =========================================================
    medical_keywords = [
        "hospital", "pharmacy", "medical",
        "medicine", "medicines", "doctor",
        "clinic", "apollo", "medplus",
        "netmeds", "1mg", "tata 1mg",
        "pharmeasy", "practo", "diagnostic",
        "diagnostics", "lab", "pathology",
        "health", "dental", "dentist",
        "eye hospital", "chemist"
    ]

    if any(word in text for word in medical_keywords):
        return "Medical"

    # =========================================================
    # EDUCATION
    # =========================================================
    education_keywords = [
        "school", "college", "university",
        "education", "course", "courses",
        "fees", "tuition", "coaching",
        "academy", "training", "udemy",
        "coursera", "unacademy",
        "byju", "books", "textbook",
        "exam fee", "education fee"
    ]

    if any(word in text for word in education_keywords):
        return "Education"

    # =========================================================
    # ENTERTAINMENT
    # =========================================================
    entertainment_keywords = [
        "netflix", "spotify", "youtube premium",
        "prime video", "amazon prime",
        "hotstar", "disney", "zee5",
        "sonyliv", "movie", "cinema",
        "pvr", "inox", "bookmyshow",
        "game", "gaming", "steam",
        "playstation", "xbox",
        "entertainment", "concert"
    ]

    if any(word in text for word in entertainment_keywords):
        return "Entertainment"

    # =========================================================
    # INVESTMENT
    # =========================================================
    investment_keywords = [
        "mutual fund", "mutualfund", "sip",
        "investment", "invest", "zerodha",
        "groww", "upstox", "angel one",
        "angelone", "coin", "nse",
        "bse", "stock", "stocks",
        "shares", "equity", "demat",
        "fd", "fixed deposit", "recurring deposit"
    ]

    if any(word in text for word in investment_keywords):
        return "Investment"

    # =========================================================
    # EMI / LOAN
    # =========================================================
    emi_keywords = [
        "emi", "loan", "lending",
        "finance", "bajaj finserv",
        "bajaj finance", "hdfc loan",
        "icici loan", "axis loan",
        "personal loan", "home loan",
        "car loan"
    ]

    if any(word in text for word in emi_keywords):
        return "EMI"

    # =========================================================
    # INCOME
    # =========================================================
    income_keywords = [
        "salary", "salary credit",
        "payroll", "income",
        "interest credit", "dividend",
        "refund", "cashback received",
        "credit received"
    ]

    if any(word in text for word in income_keywords):
        return "Income"

    # =========================================================
    # OTHER
    # =========================================================
    return "Others"
def normalize_date(date_text):
    """
    Convert common statement date formats
    into YYYY-MM-DD.
    """

    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d/%m/%y",
        "%d-%m-%y",
        "%d.%m.%Y",
        "%d.%m.%y",
        "%Y-%m-%d",
        "%d %b %Y",
        "%d %B %Y"
    ]

    for fmt in formats:

        try:

            value = datetime.strptime(
                date_text.strip(),
                fmt
            )

            return value.strftime("%Y-%m-%d")

        except ValueError:
            continue

    return None


def clean_amount(amount_text):
    """
    Convert values such as:
    ₹1,250.50
    1,250.50
    1250.50
    into float.
    """

    try:

        value = amount_text

        value = value.replace("₹", "")
        value = value.replace(",", "")
        value = value.replace(" ", "")

        return float(value)

    except Exception:

        return None
def detect_payment_method(title):

    text = title.lower()

    if "upi" in text:
        return "UPI"

    if any(word in text for word in [
        "debit card",
        "credit card",
        "card",
        "pos"
    ]):
        return "Card"

    if any(word in text for word in [
        "atm",
        "cash withdrawal",
        "cash"
    ]):
        return "Cash"

    if any(word in text for word in [
        "neft",
        "imps",
        "rtgs",
        "bank transfer",
        "fund transfer"
    ]):
        return "Bank Transfer"

    return "Bank Transfer"


    # your existing parser code...

def extract_transactions(text):
    """
    Extract expense transactions from PDF statement text.
    Handles common formats such as:

    Date | Description | Debit | Credit | Balance

    Only debit/expense amounts are imported.
    """

    transactions = []

    # ---------------------------------------------
    # CLEAN LINES
    # ---------------------------------------------

    lines = []

    for line in text.splitlines():

        line = line.strip()

        if line:
            lines.append(line)

    # ---------------------------------------------
    # DATE PATTERN
    # ---------------------------------------------

    date_pattern = re.compile(
        r"^("
        r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}"
        r"|"
        r"\d{4}[/-]\d{1,2}[/-]\d{1,2}"
        r"|"
        r"\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}"
        r")"
    )

    # ---------------------------------------------
    # AMOUNT PATTERN
    # ---------------------------------------------

    amount_pattern = re.compile(
        r"(?:₹|INR|Rs\.?)?\s*"
        r"([\d,]+(?:\.\d{1,2})?)"
    )

    i = 0

    while i < len(lines):

        line = lines[i]

        date_match = date_pattern.match(line)

        # -----------------------------------------
        # NOT A TRANSACTION LINE
        # -----------------------------------------

        if not date_match:

            i += 1
            continue

        # -----------------------------------------
        # GET DATE
        # -----------------------------------------

        date_text = date_match.group(1)

        date_value = normalize_date(
            date_text
        )

        if not date_value:

            i += 1
            continue

        # -----------------------------------------
        # TEXT AFTER DATE
        # -----------------------------------------

        remaining = line[
            date_match.end():
        ].strip()

        # -----------------------------------------
        # COLLECT THE NEXT FEW LINES
        # -----------------------------------------

        transaction_text = remaining

        j = i + 1

        while j < len(lines) and j < i + 5:

            next_line = lines[j]

            # Stop if another date starts
            if date_pattern.match(next_line):

                break

            transaction_text += " " + next_line

            j += 1

        # -----------------------------------------
        # FIND ALL NUMBERS
        # -----------------------------------------

        matches = list(
            amount_pattern.finditer(
                transaction_text
            )
        )

        if not matches:

            i = j
            continue

        # -----------------------------------------
        # REMOVE VERY LARGE REFERENCE NUMBERS
        # -----------------------------------------

        amounts = []

        for match in matches:

            value = clean_amount(
                match.group(1)
            )

            if value is None:
                continue

            # Ignore obvious account/reference numbers
            if value > 10000000:
                continue

            amounts.append(
                (
                    value,
                    match.start(),
                    match.end()
                )
            )

        if not amounts:

            i = j
            continue

        # -----------------------------------------
        # DESCRIPTION
        # -----------------------------------------

        first_amount_position = amounts[0][1]

        merchant = transaction_text[
            :first_amount_position
        ].strip()

        # Remove common statement words
        merchant = re.sub(
            r"\b(DEBIT|CREDIT|DR|CR|"
            r"WITHDRAWAL|DEPOSIT|TRANSFER|"
            r"PURCHASE|PAYMENT)\b",
            "",
            merchant,
            flags=re.IGNORECASE
        )

        merchant = re.sub(
            r"\s+",
            " ",
            merchant
        ).strip(" -|:")

        # -----------------------------------------
        # IGNORE NON-TRANSACTION ROWS
        # -----------------------------------------

        ignored = [
            "opening balance",
            "closing balance",
            "available balance",
            "account number",
            "statement period",
            "transaction date",
            "value date",
            "balance brought forward",
            "balance carried forward"
        ]

        if any(
            word in merchant.lower()
            for word in ignored
        ):

            i = j
            continue

        if not merchant:

            merchant = "Imported Transaction"

        # -----------------------------------------
        # SELECT AMOUNT
        # -----------------------------------------

        amount = amounts[0][0]

        # -----------------------------------------
        # ADD TRANSACTION
        # -----------------------------------------

        transactions.append({

            "title": merchant,

            "amount": amount,

            "date": date_value

        })

        i = j

    # =================================================
    # REMOVE DUPLICATES FROM SAME PDF
    # =================================================

    unique_transactions = []

    seen = set()

    for transaction in transactions:

        key = (
            transaction["date"],
            transaction["title"].strip().lower(),
            round(
                transaction["amount"],
                2
            )
        )

        if key in seen:

            continue

        seen.add(key)

        unique_transactions.append(
            transaction
        )

    return unique_transactions

# =========================================================
# ADD EXPENSE
# =========================================================

@expense.route("/expenses", methods=["POST"])
def add_expense():

    data = request.get_json()

    title = data.get("title")
    category = data.get("category")
    amount = data.get("amount")
    date = data.get("date")
    user_email = data.get("userEmail")

    if not title or not category or not amount or not date or not user_email:

        return jsonify({
            "message": "All fields are required"
        }), 400

    expenses.insert_one({

        "title": title,
        "category": category,
        "amount": float(amount),
        "date": date,

        "payment": data.get(
            "payment",
            "Cash"
        ),

        "description": data.get(
            "description",
            ""
        ),

        "notes": data.get(
            "notes",
            ""
        ),

        "tags": data.get(
            "tags",
            ""
        ),

        "location": data.get(
            "location",
            ""
        ),

        "time": data.get(
            "time",
            ""
        ),

        "transactionType": data.get(
            "transactionType",
            "Personal"
        ),

        "source": data.get(
            "source",
            "Manual"
        ),

        "userEmail": user_email

    })

    return jsonify({

        "message":
        "Expense Added Successfully"

    }), 201


# ==========================================
# GET EXPENSES - MONTHLY FILTER
# ==========================================

@expense.route("/expenses", methods=["GET"])
def get_expenses():

    user_email = request.args.get("userEmail")
    month = request.args.get("month")

    if not user_email:

        return jsonify({
            "message": "User email is required"
        }), 400

    # ------------------------------------------
    # BASE QUERY
    # ------------------------------------------

    query = {
        "userEmail": user_email
    }

    # ------------------------------------------
    # MONTH SELECTION
    # ------------------------------------------
    # Frontend can send month=YYYY-MM.
    # If no month is supplied, use the current month.
    # This prevents /expenses from returning all months.

    if not month:

        month = datetime.now().strftime("%Y-%m")

    # ------------------------------------------
    # MONTH FILTER
    # ------------------------------------------

    try:

        # Expected format: 2026-08
        selected_month = datetime.strptime(
            month,
            "%Y-%m"
        )

        year = selected_month.year
        month_number = selected_month.month

        # First day of selected month
        start_date = (
            f"{year:04d}-{month_number:02d}-01"
        )

        # First day of next month
        if month_number == 12:

            end_date = (
                f"{year + 1:04d}-01-01"
            )

        else:

            end_date = (
                f"{year:04d}-{month_number + 1:02d}-01"
            )

        query["date"] = {
            "$gte": start_date,
            "$lt": end_date
        }

    except ValueError:

        return jsonify({

            "message":
            "Invalid month format. Use YYYY-MM."

        }), 400

    # ------------------------------------------
    # GET DATA
    # ------------------------------------------

    expense_list = []

    for item in expenses.find(
        query
    ).sort(
        "date",
        -1
    ):

        expense_list.append({

            "_id":
            str(item["_id"]),

            "title":
            item.get(
                "title",
                ""
            ),

            "category":
            item.get(
                "category",
                "Others"
            ),

            "amount":
            float(
                item.get(
                    "amount",
                    0
                )
            ),

            "date":
            item.get(
                "date",
                ""
            ),

            "payment":
            item.get(
                "payment",
                "Unknown"
            ),

            "description":
            item.get(
                "description",
                ""
            ),

            "notes":
            item.get(
                "notes",
                ""
            ),

            "tags":
            item.get(
                "tags",
                ""
            ),

            "location":
            item.get(
                "location",
                ""
            ),

            "source":
            item.get(
                "source",
                "Manual"
            )

        })

    return jsonify(
        expense_list
    )
# =========================================================
# DELETE EXPENSE
# =========================================================

@expense.route(
    "/expenses/<expense_id>",
    methods=["DELETE"]
)
def delete_expense(expense_id):

    try:

        result = expenses.delete_one({
            "_id": ObjectId(
                expense_id
            )
        })

        if result.deleted_count == 0:

            return jsonify({
                "message":
                "Expense not found"
            }), 404

        return jsonify({

            "message":
            "Expense Deleted Successfully"

        })

    except Exception:

        return jsonify({

            "message":
            "Invalid expense ID"

        }), 400


# =========================================================
# UPDATE EXPENSE
# =========================================================

@expense.route(
    "/expenses/<expense_id>",
    methods=["PUT"]
)
def update_expense(expense_id):

    try:

        data = request.get_json()

        expenses.update_one(

            {
                "_id": ObjectId(
                    expense_id
                )
            },

            {
                "$set": {

                    "title":
                    data.get("title"),

                    "category":
                    data.get("category"),

                    "amount":
                    float(
                        data.get("amount")
                    ),

                    "date":
                    data.get("date"),

                    "payment":
                    data.get(
                        "payment",
                        "Cash"
                    ),

                    "description":
                    data.get(
                        "description",
                        ""
                    ),

                    "notes":
                    data.get(
                        "notes",
                        ""
                    ),

                    "tags":
                    data.get(
                        "tags",
                        ""
                    ),

                    "location":
                    data.get(
                        "location",
                        ""
                    ),

                    "time":
                    data.get(
                        "time",
                        ""
                    ),

                    "transactionType":
                    data.get(
                        "transactionType",
                        "Personal"
                    )

                }
            }
        )

        return jsonify({

            "message":
            "Expense Updated Successfully"

        })

    except Exception:

        return jsonify({

            "message":
            "Unable to update expense"

        }), 400


# =========================================================
# DASHBOARD TOTALS
# =========================================================

# =========================================================
# DASHBOARD TOTALS - MONTHLY
# =========================================================

@expense.route("/dashboard", methods=["GET"])
def dashboard():

    try:

        user_email = request.args.get("userEmail")

        if not user_email:
            return jsonify({
                "message": "User email is required"
            }), 400

        # -------------------------------------------------
        # MONTH SELECTION
        # -------------------------------------------------

        # Example:
        # /api/dashboard?userEmail=test@gmail.com&month=2026-08

        month = request.args.get("month")

        # If month is not supplied, use current month
        if not month:

            month = datetime.now().strftime("%Y-%m")

        # Validate month format
        try:

            datetime.strptime(
                month,
                "%Y-%m"
            )

        except ValueError:

            return jsonify({
                "message":
                "Invalid month format. Use YYYY-MM."
            }), 400

        # -------------------------------------------------
        # CREATE MONTH DATE RANGE
        # -------------------------------------------------

        start_date = f"{month}-01"

        year = int(month[:4])
        month_number = int(month[5:7])

        if month_number == 12:

            next_year = year + 1
            next_month = 1

        else:

            next_year = year
            next_month = month_number + 1

        end_date = (
            f"{next_year:04d}-{next_month:02d}-01"
        )

        # -------------------------------------------------
        # GET MONTHLY EXPENSES
        # -------------------------------------------------

        data = list(
            expenses.find({
                "userEmail": user_email,
                "date": {
                    "$gte": start_date,
                    "$lt": end_date
                }
            }).sort("date", -1)
        )

        # -------------------------------------------------
        # TOTAL EXPENSE
        # -------------------------------------------------

        total_expense = sum(
            float(
                item.get(
                    "amount",
                    0
                )
            )
            for item in data
        )

        # -------------------------------------------------
        # TOTAL TRANSACTIONS
        # -------------------------------------------------

        total_transactions = len(data)

               # -------------------------------------------------
        # CATEGORY TOTALS
        # -------------------------------------------------

        categories = {}

        for item in data:

            title = item.get(
                "title",
                ""
            )

            existing_category = str(
                item.get(
                    "category",
                    ""
                )
            ).strip()

            transaction_type = str(
                item.get(
                    "transactionType",
                    ""
                )
            ).lower()

            # Recalculate category from transaction title
            detected_category = detect_category(
                title
            )

            # Use detected category when the existing
            # category is missing or incorrectly classified
            if (
                not existing_category
                or existing_category == "Others"
                or existing_category == "Transportation"
            ):

                category = detected_category

            else:

                category = existing_category

            amount = float(
                item.get(
                    "amount",
                    0
                )
            )

            categories[category] = (
                categories.get(
                    category,
                    0
                )
                + amount
            )

        # -------------------------------------------------
        # TOP CATEGORY
        # -------------------------------------------------

        top_category = "None"

        if categories:

            top_category = max(
                categories,
                key=categories.get
            )

        # -------------------------------------------------
        # PAYMENT METHOD TOTALS
        # -------------------------------------------------

        payments = {}

        for item in data:

            payment = item.get(
                "payment",
                "Unknown"
            )

            payments[payment] = (
                payments.get(
                    payment,
                    0
                )
                + 1
            )

        # -------------------------------------------------
        # MOST USED PAYMENT
        # -------------------------------------------------

        most_used_payment = "None"

        if payments:

            most_used_payment = max(
                payments,
                key=payments.get
            )
        # -------------------------------------------------
        # PAYMENT METHOD TOTALS
        # -------------------------------------------------

        payments = {}

        for item in data:

            payment = item.get(
                "payment",
                "Unknown"
            )

            payments[payment] = (
                payments.get(
                    payment,
                    0
                )
                + 1
            )

        # -------------------------------------------------
        # MOST USED PAYMENT
        # -------------------------------------------------

        most_used_payment = "None"

        if payments:

            most_used_payment = max(
                payments,
                key=payments.get
            )

        # -------------------------------------------------
        # RECENT EXPENSES
        # -------------------------------------------------

        recent_expenses = []

        for item in data[:10]:

            recent_expenses.append({

                "_id":
                str(
                    item["_id"]
                ),

                "title":
                item.get(
                    "title",
                    ""
                ),

                "category":
                item.get(
                    "category",
                    "Others"
                ),

                "amount":
                float(
                    item.get(
                        "amount",
                        0
                    )
                ),

                "date":
                item.get(
                    "date",
                    ""
                ),

                "payment":
                item.get(
                    "payment",
                    "Unknown"
                ),

                "source":
                item.get(
                    "source",
                    "Manual"
                )

            })

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return jsonify({

            "month":
            month,

            "startDate":
            start_date,

            "endDate":
            end_date,

            "totalExpense":
            round(
                total_expense,
                2
            ),

            "totalTransactions":
            total_transactions,

            "topCategory":
            top_category,

            "mostUsedPayment":
            most_used_payment,

            "categories":
            categories,

            "payments":
            payments,

            "recentExpenses":
            recent_expenses

        }), 200

    except Exception as error:

        print(
            "\n========== DASHBOARD ERROR =========="
        )

        print(error)

        print(
            "=====================================\n"
        )

        return jsonify({

            "message":
            "Unable to load dashboard.",

            "error":
            str(error)

        }), 500

# =========================================================
# UPLOAD + ANALYZE + IMPORT STATEMENT
# =========================================================

@expense.route(
    "/expenses/upload-statement",
    methods=["POST"]
)
def upload_statement():

    try:

        # -------------------------------------------------
        # FILE
        # -------------------------------------------------

        if "file" not in request.files:

            return jsonify({

                "message":
                "No PDF file received."

            }), 400

        file = request.files["file"]

        if not file.filename:

            return jsonify({

                "message":
                "No file selected."

            }), 400

        if not file.filename.lower().endswith(
            ".pdf"
        ):

            return jsonify({

                "message":
                "Only PDF files are supported."

            }), 400

        # -------------------------------------------------
        # USER
        # -------------------------------------------------

        user_email = request.form.get(
            "userEmail"
        )

        if not user_email:

            return jsonify({

                "message":
                "User email is required."

            }), 400

        # -------------------------------------------------
        # PASSWORD
        # -------------------------------------------------

        pdf_password = request.form.get(
            "password",
            ""
        )

        # -------------------------------------------------
        # READ PDF
        # -------------------------------------------------

        pdf_bytes = file.read()

        reader = PdfReader(
            BytesIO(pdf_bytes)
        )

        # -------------------------------------------------
        # UNLOCK PASSWORD PROTECTED PDF
        # -------------------------------------------------

        if reader.is_encrypted:

            if not pdf_password:

                return jsonify({

                    "message":
                    "This PDF is password protected. Please enter the PDF password."

                }), 400

            try:

                result = reader.decrypt(
                    pdf_password
                )

                if result == 0:

                    return jsonify({

                        "message":
                        "Incorrect PDF password."

                    }), 400

            except Exception as error:

                print(
                    "PDF PASSWORD ERROR:",
                    error
                )

                return jsonify({

                    "message":
                    "Unable to unlock the PDF. Please check the password."

                }), 400

                      # -------------------------------------------------
        # EXTRACT PDF TABLES
        # -------------------------------------------------

        pdf_tables = []

        try:

            with pdfplumber.open(
                BytesIO(pdf_bytes),
                password=pdf_password or None
            ) as pdf:

                for page_number, page in enumerate(pdf.pages, start=1):

                    tables = page.extract_tables()

                    print(
                        f"PDF PAGE {page_number}: "
                        f"{len(tables)} table(s) found"
                    )

                    for table in tables:

                        if table:

                            pdf_tables.extend(table)


        except Exception as error:

            print(
                "\n========== PDF TABLE ERROR =========="
            )

            print(error)

            print(
                "=====================================\n"
            )

            return jsonify({

                "message":
                "Unable to read the transaction tables from the PDF.",

                "error":
                str(error)

            }), 400


        # -------------------------------------------------
        # CHECK TABLE
        # -------------------------------------------------

        if not pdf_tables:

            return jsonify({

                "message":
                "The PDF was opened successfully, but no transaction table was detected.",

                "imported":
                0

            }), 400


        # -------------------------------------------------
        # DEBUG TABLE DATA
        # -------------------------------------------------

        print(
            "\n========== PDF TABLE DATA =========="
        )

        for row in pdf_tables[:30]:

            print(row)

        print(
            "====================================\n"
        )


        # -------------------------------------------------
        # HELPER: CLEAN CELL
        # -------------------------------------------------

        def clean_cell(value):

            if value is None:

                return ""

            value = str(value)

            value = value.replace(
                "\n",
                " "
            )

            value = re.sub(
                r"\s+",
                " ",
                value
            )

            return value.strip()


        # -------------------------------------------------
        # HELPER: FIND DATE
        # -------------------------------------------------

        def find_date(row):

            date_patterns = [

                r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",

                r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",

                r"\b\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4}\b"

            ]

            for cell in row:

                cell = clean_cell(cell)

                for pattern in date_patterns:

                    match = re.search(
                        pattern,
                        cell
                    )

                    if match:

                        return normalize_date(
                            match.group(0)
                        )

            return None


        # -------------------------------------------------
        # HELPER: AMOUNT
        # -------------------------------------------------

        def extract_amount(value):

            if value is None:

                return None

            value = clean_cell(value)

            if not value:

                return None

            # Remove currency symbols
            value = re.sub(
                r"(₹|INR|Rs\.?)",
                "",
                value,
                flags=re.IGNORECASE
            )

            # Remove commas
            value = value.replace(
                ",",
                ""
            )

            # Remove spaces
            value = value.replace(
                " ",
                ""
            )

            # Handle parentheses as negative
            negative = False

            if (
                value.startswith("(")
                and value.endswith(")")
            ):

                negative = True

                value = value[1:-1]

            # Keep only numeric value
            match = re.search(
                r"-?\d+(?:\.\d{1,2})?",
                value
            )

            if not match:

                return None

            try:

                amount = float(
                    match.group(0)
                )

                if negative:

                    amount = -amount

                return amount

            except Exception:

                return None


        # -------------------------------------------------
        # HELPER: PAYMENT METHOD
        # -------------------------------------------------

        def get_payment_method(description):

            text = description.lower()

            if any(
                word in text
                for word in [
                    "upi",
                    "upi/",
                    "upi-",
                    "gpay",
                    "google pay",
                    "phonepe",
                    "paytm"
                ]
            ):

                return "UPI"


            if any(
                word in text
                for word in [
                    "debit card",
                    "credit card",
                    "card",
                    "pos",
                    "visa",
                    "mastercard"
                ]
            ):

                return "Card"


            if any(
                word in text
                for word in [
                    "atm",
                    "cash withdrawal",
                    "cash withdraw"
                ]
            ):

                return "Cash"


            if any(
                word in text
                for word in [
                    "neft",
                    "imps",
                    "rtgs",
                    "bank transfer",
                    "fund transfer"
                ]
            ):

                return "Bank Transfer"


            if any(
                word in text
                for word in [
                    "cheque",
                    "check"
                ]
            ):

                return "Cheque"


            return "Unknown"


        # -------------------------------------------------
        # PROCESS TABLES
        # -------------------------------------------------

        transactions = []

        current_header = None


        for row in pdf_tables:

            if not row:

                continue


            cells = [
                clean_cell(cell)
                for cell in row
            ]


            # Remove completely empty cells
            if not any(cells):

                continue


            # -------------------------------------------------
            # DETECT HEADER
            # -------------------------------------------------

            row_text = " ".join(
                cells
            ).lower()


            header_words = [

                "date",
                "description",
                "narration",
                "particular",
                "debit",
                "withdrawal",
                "credit",
                "deposit",
                "balance",
                "amount",
                "transaction"

            ]


            header_score = sum(

                1
                for word in header_words
                if word in row_text

            )


            if header_score >= 2:

                current_header = [
                    cell.lower()
                    for cell in cells
                ]

                print(
                    "HEADER DETECTED:",
                    current_header
                )

                continue


            # -------------------------------------------------
            # FIND DATE
            # -------------------------------------------------

            transaction_date = find_date(
                cells
            )

            if not transaction_date:

                continue


            # -------------------------------------------------
            # DETERMINE COLUMNS
            # -------------------------------------------------

            date_index = None

            description_index = None

            debit_index = None

            credit_index = None

            balance_index = None


            if current_header:

                for index, header in enumerate(
                    current_header
                ):

                    if (
                        "date" in header
                        or "transaction date" in header
                    ):

                        if date_index is None:

                            date_index = index


                    if any(
                        word in header
                        for word in [
                            "description",
                            "narration",
                            "particular",
                            "merchant",
                            "transaction details"
                        ]
                    ):

                        if description_index is None:

                            description_index = index


                    if any(
                        word in header
                        for word in [
                            "debit",
                            "withdrawal",
                            "withdraw",
                            "dr"
                        ]
                    ):

                        if debit_index is None:

                            debit_index = index


                    if any(
                        word in header
                        for word in [
                            "credit",
                            "deposit",
                            "cr"
                        ]
                    ):

                        if credit_index is None:

                            credit_index = index


                    if "balance" in header:

                        if balance_index is None:

                            balance_index = index


            # -------------------------------------------------
            # DESCRIPTION
            # -------------------------------------------------

            if (
                description_index is not None
                and description_index < len(cells)
            ):

                title = cells[
                    description_index
                ]

            else:

                # Find a useful non-date text cell

                title = ""

                for cell in cells:

                    if not cell:

                        continue

                    if re.search(
                        r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",
                        cell
                    ):

                        continue

                    if extract_amount(cell) is not None:

                        continue

                    title = cell

                    break


            title = clean_cell(
                title
            )


            # -------------------------------------------------
            # GET DEBIT AMOUNT  
            # -------------------------------------------------

            amount = None


            if (
                debit_index is not None
                and debit_index < len(cells)
            ):

                amount = extract_amount(
                    cells[debit_index]
                )


            # -------------------------------------------------
            # GET CREDIT AMOUNT
            # -------------------------------------------------

            credit_amount = None


            if (
                credit_index is not None
                and credit_index < len(cells)
            ):

                credit_amount = extract_amount(
                    cells[credit_index]
                )


            # -------------------------------------------------
            # IF THERE IS NO DEBIT COLUMN
            # -------------------------------------------------

            if amount is None:

                # Look for explicit debit indicators
                row_lower = row_text

                debit_indicated = any(
                    word in row_lower
                    for word in [
                        "debit",
                        "withdrawal",
                        "withdraw",
                        " dr "
                    ]
                )


                if debit_indicated:

                    possible_amounts = []

                    for index, cell in enumerate(
                        cells
                    ):

                        value = extract_amount(
                            cell
                        )

                        if value is None:

                            continue

                        if (
                            balance_index is not None
                            and index == balance_index
                        ):

                            continue

                        if (
                            credit_index is not None
                            and index == credit_index
                        ):

                            continue

                        possible_amounts.append(
                            value
                        )


                    if possible_amounts:

                        amount = (
                            possible_amounts[0]
                        )


            # -------------------------------------------------
            # SKIP CREDIT-ONLY TRANSACTIONS
            # -------------------------------------------------

            if (
                amount is None
                and credit_amount is not None
            ):

                print(
                    "CREDIT TRANSACTION SKIPPED:",
                    title,
                    credit_amount
                )

                continue


            # -------------------------------------------------
            # NO AMOUNT
            # -------------------------------------------------

            if amount is None:

                continue


            # -------------------------------------------------
            # INVALID AMOUNT
            # -------------------------------------------------

            if amount <= 0:

                continue


            # Prevent impossible reference numbers
            if amount > 10000000:

                print(
                    "SUSPICIOUS AMOUNT SKIPPED:",
                    title,
                    amount
                )

                continue


            # -------------------------------------------------
            # CLEAN TITLE
            # -------------------------------------------------

            if not title:

                title = "Imported Transaction"


            title = re.sub(
                r"\s+",
                " ",
                title
            ).strip(
                " -|:"
            )


            # -------------------------------------------------
            # PAYMENT METHOD
            # -------------------------------------------------

            payment = get_payment_method(
                " ".join(cells)
            )


            # -------------------------------------------------
            # ADD TRANSACTION
            # -------------------------------------------------

            transactions.append({

                "title":
                title,

                "amount":
                round(
                    amount,
                    2
                ),

                "date":
                transaction_date,

                "payment":
                payment

            })


        # -------------------------------------------------
        # REMOVE DUPLICATES INSIDE PDF
        # -------------------------------------------------

        unique_transactions = []

        seen = set()


        for transaction in transactions:

            key = (

                transaction["date"],

                transaction["title"]
                .strip()
                .lower(),

                round(
                    transaction["amount"],
                    2
                )

            )


            if key in seen:

                print(
                    "DUPLICATE IN PDF SKIPPED:",
                    transaction
                )

                continue


            seen.add(
                key
            )

            unique_transactions.append(
                transaction
            )


        transactions = unique_transactions


        # -------------------------------------------------
        # CHECK TRANSACTIONS
        # -------------------------------------------------

        if not transactions:

            return jsonify({

                "message":
                "The PDF was read successfully, but no debit transactions could be detected.",

                "imported":
                0

            }), 200


        print(
            "\n========== TRANSACTIONS =========="
        )

        for transaction in transactions:

            print(
                transaction
            )

        print(
            "=================================\n"
        )


        # -------------------------------------------------
        # DUPLICATE CHECK + INSERT
        # -------------------------------------------------

        imported = []

        skipped = []


        for transaction in transactions:

            title = transaction[
                "title"
            ]

            amount = transaction[
                "amount"
            ]

            date = transaction[
                "date"
            ]

            payment = transaction.get(
                "payment",
                "Unknown"
            )


            # ---------------------------------------------
            # CATEGORY
            # ---------------------------------------------

            category = detect_category(
                title
            )


            # ---------------------------------------------
            # DUPLICATE CHECK
            # ---------------------------------------------

            duplicate = expenses.find_one({

                "userEmail":
                user_email,

                "title":
                title,

                "amount":
                amount,

                "date":
                date,

                "source":
                "Statement"

            })


            if duplicate:

                skipped.append({

                    "title":
                    title,

                    "amount":
                    amount,

                    "date":
                    date

                })

                print(
                    "DATABASE DUPLICATE SKIPPED:",
                    title,
                    amount,
                    date
                )

                continue


            # ---------------------------------------------
            # INSERT
            # ---------------------------------------------

            expense_document = {

                "title":
                title,

                "category":
                category,

                "amount":
                amount,

                "date":
                date,

                "payment":
                payment,

                "description":
                "Imported from PDF statement",

                "notes":
                "",

                "tags":
                "statement, imported",

                "location":
                "",

                "time":
                "",

                "transactionType":
                "Personal",

                "source":
                "Statement",

                "userEmail":
                user_email,

                "importedAt":
                datetime.utcnow()

            }


            result = expenses.insert_one(
                expense_document
            )


            imported.append({

                "_id":
                str(
                    result.inserted_id
                ),

                "title":
                title,

                "category":
                category,

                "amount":
                amount,

                "date":
                date,

                "payment":
                payment

            })


        # -------------------------------------------------
        # FINAL RESPONSE
        # -------------------------------------------------

        return jsonify({

            "message":
            "Statement analyzed successfully.",

            "imported":
            len(imported),

            "skipped":
            len(skipped),

            "transactions":
            imported,

            "skippedTransactions":
            skipped

        }), 200


    except Exception as error:

        print(
            "\n========== STATEMENT ERROR =========="
        )

        print(
            error
        )

        print(
            "=====================================\n"
        )

        return jsonify({

            "message":
            "Unable to analyze the PDF statement.",

            "error":
            str(error)

        }), 500
    # =========================================================
# RECLASSIFY EXISTING TRANSACTIONS
# =========================================================

@expense.route(
    "/reclassify-categories",
    methods=["POST"]
)
def reclassify_categories():

    try:

        user_email = request.args.get(
            "userEmail"
        )

        if not user_email:

            return jsonify({

                "message":
                "User email is required."

            }), 400

        # -------------------------------------------------
        # GET USER TRANSACTIONS
        # -------------------------------------------------

        transactions = list(
            expenses.find({
                "userEmail":
                user_email
            })
        )

        updated = 0

        category_counts = {}

        # -------------------------------------------------
        # RECLASSIFY
        # -------------------------------------------------

        for item in transactions:

            title = item.get(
                "title",
                ""
            )

            if not title:

                continue

            old_category = str(
                item.get(
                    "category",
                    ""
                )
            ).strip()

            # Calculate category using our
            # actual category detector
            new_category = detect_category(
                title
            )

            # Only change categories that are
            # missing, Others, or old Transport name
            if (
                not old_category
                or old_category == "Others"
                or old_category == "Transportation"
            ):

                expenses.update_one(

                    {
                        "_id":
                        item["_id"]
                    },

                    {
                        "$set": {
                            "category":
                            new_category
                        }
                    }

                )

                updated += 1

                category_counts[
                    new_category
                ] = (
                    category_counts.get(
                        new_category,
                        0
                    )
                    + 1
                )

        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        return jsonify({

            "success":
            True,

            "message":
            "Existing transactions reclassified successfully.",

            "updated":
            updated,

            "categories":
            category_counts

        }), 200

    except Exception as error:

        print(
            "\n========== RECLASSIFICATION ERROR =========="
        )

        print(error)

        print(
            "============================================\n"
        )

        return jsonify({

            "success":
            False,

            "message":
            "Unable to reclassify transactions.",

            "error":
            str(error)

        }), 500
    