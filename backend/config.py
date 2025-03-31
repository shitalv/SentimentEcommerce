import os
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

class Config:
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev_key_for_testing')
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost:5432/sentiment_ecommerce")
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Optional, disables tracking modifications
