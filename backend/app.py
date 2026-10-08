from flask import Flask, jsonify
from flask_cors import CORS

from routes.auth import auth
from routes.expenses import expenses_bp
from routes.income import income_bp
from routes.analytics import analytics
from routes.ml_prediction import ml_prediction


# =========================================================
# CREATE APP
# =========================================================

app = Flask(__name__)


# =========================================================
# CORS
# =========================================================

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "*"
        }
    }
)


# =========================================================
# REGISTER BLUEPRINTS
# =========================================================

app.register_blueprint(
    auth,
    url_prefix="/api"
)

app.register_blueprint(
    expenses_bp,
    url_prefix="/api"
)

app.register_blueprint(
    income_bp,
    url_prefix="/api"
)

app.register_blueprint(
    analytics,
    url_prefix="/api"
)

app.register_blueprint(
    ml_prediction,
    url_prefix="/api"
)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return jsonify({

        "success": True,

        "message":
            "SmartSpend AI Backend is running.",

        "status":
            "online"

    })


# =========================================================
# HEALTH
# =========================================================

@app.route("/api/health")
def health():

    return jsonify({

        "success": True,

        "message":
            "SmartSpend AI API is working."

    })


# =========================================================
# BLUEPRINT CHECK
# =========================================================

print()
print("==========================================")
print("SMARTSPEND AI BLUEPRINT CHECK")
print("==========================================")

print("auth:", type(auth))
print("expenses:", type(expenses_bp))
print("income:", type(income_bp))
print("analytics:", type(analytics))
print("ml_prediction:", type(ml_prediction))

print("==========================================")


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    print()
    print("==========================================")
    print("SMARTSPEND AI SERVER STARTING")
    print("==========================================")
    print("URL: http://127.0.0.1:5000")
    print("==========================================")

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )