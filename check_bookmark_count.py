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
    try:
        res = db.session.execute(text('SELECT COUNT(*) FROM bookmark')).scalar()
        print(f"BOOKMARK_COUNT: {res}")
    except Exception as e:
        print(f"ERROR: {e}")
