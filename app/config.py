import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///instance/site.db")

    # SQLAlchemy sometimes needs postgresql:// not postgres://
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
