import os
import sys

# Setup paths so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from extensions import db
from services.entity_service import EntityService
from models.intelligence import Intelligence
from models.entity import Entity

def run_migration():
    # To avoid the initialization syncing if we just want app context, we can just create it.
    # Actually create_app() will trigger sync. Let's just create a bare flask app for db context.
    from flask import Flask
    from config import config_by_name
    app = Flask(__name__)
    app.config.from_object(config_by_name[os.environ.get('FLASK_ENV', 'development')])
    db.init_app(app)
    
    with app.app_context():
        print("Starting Phase 6.1 Data Migration...")
        
        # 1. Cleanup
        print("1. Running cleanup_low_quality_entities...")
        res = EntityService.cleanup_low_quality_entities()
        print(f"Cleanup results: {res}")
        
        print("2. Regenerating entities and rebuilding relationships...")
        
        # limit to 50 for quick execution and verification
        res_intel = EntityService.process_intelligence_records(limit=50)
        print(f"Regeneration results: {res_intel}")
        
        print("\n--- Migration Complete. Top 10 Entities Now ---")
        top = Entity.query.filter_by(is_deleted=False).order_by(Entity.confidence_score.desc()).limit(10).all()
        for e in top:
            print(f"- {e.name} ({e.entity_type}, score: {e.confidence_score})")

if __name__ == '__main__':
    run_migration()
