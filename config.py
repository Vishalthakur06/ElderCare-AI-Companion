import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///eldercare.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
    NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
