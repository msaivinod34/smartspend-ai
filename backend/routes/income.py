from flask import Blueprint, request, jsonify
from database.db import income
from bson import ObjectId


income_bp = Blueprint("income", __name__)


# =========================================================
# ADD INCOME
# =========================================================

@income_bp.route("/income", methods=["POST"])
def add_income():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "message": "No data received."
            }), 400

        source = data.get("source")
        category = data.get("category")
        amount = data.get("amount")
        date = data.get("date")
        description = data.get("description", "")
        user_email = data.get("userEmail")

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not source:
            return jsonify({
                "message": "Income source is required."
            }), 400

        if not category:
            return jsonify({
                "message": "Income category is required."
            }), 400

        if amount is None or amount == "":
            return jsonify({
                "message": "Income amount is required."
            }), 400

        if not date:
            return jsonify({
                "message": "Income date is required."
            }), 400

        if not user_email:
            return jsonify({
                "message": "User email is required."
            }), 400

        try:
            amount = float(amount)
        except (ValueError, TypeError):

            return jsonify({
                "message": "Amount must be a valid number."
            }), 400

        if amount <= 0:

            return jsonify({
                "message": "Amount must be greater than zero."
            }), 400

        # -------------------------------------------------
        # SAVE TO MONGODB
        # -------------------------------------------------

        document = {

            "source": source.strip(),

            "category": category.strip(),

            "amount": amount,

            "date": date,

            "description": description.strip(),

            "userEmail": user_email.strip().lower()

        }

        result = income.insert_one(document)

        return jsonify({

            "message": "Income Added Successfully",

            "income": {

                "_id": str(result.inserted_id),

                "source": document["source"],

                "category": document["category"],

                "amount": document["amount"],

                "date": document["date"],

                "description": document["description"],

                "userEmail": document["userEmail"]

            }

        }), 201

    except Exception as error:

        print("ADD INCOME ERROR:", error)

        return jsonify({

            "message": "Unable to add income.",

            "error": str(error)

        }), 500


# =========================================================
# GET INCOME
# =========================================================

@income_bp.route("/income", methods=["GET"])
def get_income():

    try:

        user_email = request.args.get("userEmail")

        if not user_email:

            return jsonify({

                "message": "User email is required."

            }), 400

        user_email = user_email.strip().lower()

        records = income.find({

            "userEmail": user_email

        }).sort(
            "date",
            -1
        )

        income_list = []

        for item in records:

            income_list.append({

                "_id":
                    str(item["_id"]),

                "source":
                    item.get("source", ""),

                "category":
                    item.get("category", "Other"),

                "amount":
                    float(item.get("amount", 0)),

                "date":
                    item.get("date", ""),

                "description":
                    item.get("description", ""),

                "userEmail":
                    item.get("userEmail", "")

            })

        return jsonify(income_list), 200

    except Exception as error:

        print("GET INCOME ERROR:", error)

        return jsonify({

            "message": "Unable to fetch income.",

            "error": str(error)

        }), 500


# =========================================================
# DELETE INCOME
# =========================================================

@income_bp.route("/income/<income_id>", methods=["DELETE"])
def delete_income(income_id):

    try:

        result = income.delete_one({

            "_id": ObjectId(income_id)

        })

        if result.deleted_count == 0:

            return jsonify({

                "message": "Income record not found."

            }), 404

        return jsonify({

            "message": "Income Deleted Successfully"

        }), 200

    except Exception as error:

        print("DELETE INCOME ERROR:", error)

        return jsonify({

            "message": "Unable to delete income.",

            "error": str(error)

        }), 500


# =========================================================
# UPDATE INCOME
# =========================================================

@income_bp.route("/income/<income_id>", methods=["PUT"])
def update_income(income_id):

    try:

        data = request.get_json()

        if not data:

            return jsonify({

                "message": "No data received."

            }), 400

        source = data.get("source")
        category = data.get("category")
        amount = data.get("amount")
        date = data.get("date")
        description = data.get("description", "")

        if not source or not category or amount is None or not date:

            return jsonify({

                "message":
                    "Source, category, amount and date are required."

            }), 400

        try:

            amount = float(amount)

        except (ValueError, TypeError):

            return jsonify({

                "message":
                    "Amount must be a valid number."

            }), 400

        if amount <= 0:

            return jsonify({

                "message":
                    "Amount must be greater than zero."

            }), 400

        result = income.update_one(

            {
                "_id": ObjectId(income_id)
            },

            {
                "$set": {

                    "source":
                        source.strip(),

                    "category":
                        category.strip(),

                    "amount":
                        amount,

                    "date":
                        date,

                    "description":
                        description.strip()

                }

            }

        )

        if result.matched_count == 0:

            return jsonify({

                "message":
                    "Income record not found."

            }), 404

        return jsonify({

            "message":
                "Income Updated Successfully"

        }), 200

    except Exception as error:

        print("UPDATE INCOME ERROR:", error)

        return jsonify({

            "message":
                "Unable to update income.",

            "error":
                str(error)

        }), 500