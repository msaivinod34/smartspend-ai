from pymongo import MongoClient

from config import Config


client = MongoClient(
    Config.MONGO_URI
)


db = client[
    Config.DATABASE_NAME
]


users = db["users"]

expenses = db["expenses"]

budgets = db["budgets"]

reports = db["reports"]

ai_history = db["ai_history"]

income = db["income"]