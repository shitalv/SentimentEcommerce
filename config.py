import os
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:root@localhost:5432/sentiment_ecommerce')
    SQLALCHEMY_TRACK_MODIFICATIONS = False