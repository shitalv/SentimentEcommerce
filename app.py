import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from config import Config
import os
# from dotenv import load_dotenv
# load_dotenv() 
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key")
app.config["SQLALCHEMY_DATABASE_URI"] ='postgresql://postgres:root@localhost:5432/sentiment_ecommerce'
# Configure the database connection
app.config["SQLALCHEMY_DATABASE_URI"] ="postgresql://postgres:root@localhost:5432/sentiment_ecommerce"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# Add this before db.create_all()
# with app.app_context():
#     # Create a custom schema
#     db.session.execute('CREATE SCHEMA IF NOT EXISTS myschema')
#     db.session.commit()
# Initialize the app with the extension
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models after db initialization
with app.app_context():
    # Import models to create tables
    import models  # noqa: F401
    
    # User loader function for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Create tables if they don't exist
    db.create_all()

# Import routes
from backend.app import *  # noqa: F401

# Development server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)