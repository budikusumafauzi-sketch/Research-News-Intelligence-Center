import os
from flask import Flask
from config import config_by_name
from extensions import db
from sqlalchemy import text

config_name = os.environ.get('FLASK_ENV', 'development')
app = Flask(__name__)
app.config.from_object(config_by_name[config_name])
db.init_app(app)

with app.app_context():
    # Drop existing bookmark table if it exists
    try:
        db.session.execute(text('DROP TABLE IF EXISTS bookmark'))
        db.session.commit()
        print("Dropped bookmark table.")
    except Exception as e:
        print(f"Error dropping table: {e}")
        
    # Import the models to register them
    import models
    
    # Create tables
    try:
        db.create_all()
        print("Created tables successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
