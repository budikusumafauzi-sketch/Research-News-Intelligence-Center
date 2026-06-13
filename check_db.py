import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app import create_app
from models.entity import Entity

app = create_app()
with app.app_context():
    print("Entities in DB:")
    for e in Entity.query.all():
        print(f"Name: '{e.name}', Type: '{e.entity_type}'")
