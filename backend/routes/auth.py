from flask import Blueprint, request, jsonify
from database.db import users
from flask_bcrypt import Bcrypt

auth = Blueprint("auth", __name__)

bcrypt = Bcrypt()

# ---------------- REGISTER ---------------- #

@auth.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")

    if not name or not email or not phone or not password:
        return jsonify({"message": "All fields are required"}), 400

    # Check email
    if users.find_one({"email": email}):
        return jsonify({"message": "Email already exists"}), 409

    # Check phone
    if users.find_one({"phone": phone}):
        return jsonify({"message": "Phone number already exists"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    users.insert_one({

        "name": name,
        "email": email,
        "phone": phone,
        "password": hashed_password

    })

    return jsonify({
        "message": "Registration Successful"
    }), 201

# ---------------- LOGIN ---------------- #

@auth.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")

    password = data.get("password")

    user = users.find_one({"email":email})

    if not user:

        return jsonify({"message":"Invalid Email"}),401

    if bcrypt.check_password_hash(user["password"],password):

        return jsonify({

            "message":"Login Successful",

            "name":user["name"]

        })

    return jsonify({"message":"Invalid Password"}),401