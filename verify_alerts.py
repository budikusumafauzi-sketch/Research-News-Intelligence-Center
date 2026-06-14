import os
from flask import Flask
from config import config_by_name
from extensions import db
from models.entity import Entity
from models.bookmark import Bookmark
from models.alert import Alert
from services.intelligence_service import IntelligenceService
from models.content import News

config_name = os.environ.get('FLASK_ENV', 'development')
app = Flask(__name__)
app.config.from_object(config_by_name[config_name])
db.init_app(app)

with app.app_context():
    # Setup test data
    # Find an entity
    entity = Entity.query.filter_by(name="Apple").first()
    if not entity:
        entity = Entity(name="Apple", entity_type="company", description="Test entity")
        db.session.add(entity)
        db.session.commit()
        print("Created test entity Apple")
        
    print(f"Testing with Entity: {entity.name}")
    
    # Bookmark it
    bookmark = Bookmark.query.filter_by(bookmark_type='entity', target_id=entity.id).first()
    if not bookmark:
        bookmark = Bookmark(bookmark_type='entity', target_id=entity.id)
        db.session.add(bookmark)
        db.session.commit()
        print("Created bookmark.")
    
    # Create fake news containing the entity
    news = News(
        title=f"Test News about {entity.name}",
        content_raw=f"This is a test news article about {entity.name}. They are doing great things.",
        source_id=1,
        original_url=f"http://test.com/{entity.id}",
        published_at=db.func.now()
    )
    db.session.add(news)
    db.session.commit()
    
    print("Created test news.")
    
    # Count alerts before
    alerts_before = Alert.query.count()
    
    # Generate intelligence
    record = IntelligenceService.generate_news_intelligence(news)
    print(f"Generated intelligence: {record.id}")
    
    # Count alerts after
    alerts_after = Alert.query.count()
    print(f"Alerts before: {alerts_before}, after: {alerts_after}")
    
    alert = Alert.query.filter_by(entity_id=entity.id, intelligence_id=record.id).first()
    if alert:
        print(f"Alert generated successfully: {alert.title}")
    else:
        print("FAILED to generate alert!")
        
    # Test duplicate prevention
    IntelligenceService._generate_alerts_for_intelligence(record)
    alerts_after_duplicate = Alert.query.count()
    if alerts_after_duplicate == alerts_after:
        print("Duplicate prevention successful.")
    else:
        print("FAILED: Duplicates were created.")
        
    # Clean up test data
    db.session.delete(alert)
    db.session.delete(record)
    db.session.delete(news)
    # Don't delete bookmark, let it stay
    db.session.commit()
    print("Cleaned up test data.")
