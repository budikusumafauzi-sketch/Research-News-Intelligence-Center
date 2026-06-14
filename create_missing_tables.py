import os
from flask import Flask
from config import config_by_name
from extensions import db

config_name = os.environ.get('FLASK_ENV', 'development')
app = Flask(__name__)
app.config.from_object(config_by_name[config_name])
db.init_app(app)

with app.app_context():
    import models
    try:
        db.create_all()
        print("Missing tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
