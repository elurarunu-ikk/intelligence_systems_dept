import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __call__(self):
        return self

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

    # ✅ Render-safe DB config
    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:
        # Render / production
        SQLALCHEMY_DATABASE_URI = DATABASE_URL
    else:
        # Local / default (SQLite in instance folder)
        SQLALCHEMY_DATABASE_URI = "sqlite:///instance/site.db"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Seed admin (dev / review only)
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@saveetha.edu.in")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "ChangeMe@123")
