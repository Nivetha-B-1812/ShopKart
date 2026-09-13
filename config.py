import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "shopkart-development-secret-key"
    )

    SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/shopkart.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False