from extensions import db
from datetime import datetime

class Source(db.Model):
    """
    Source model does not use Soft Delete as it is a core configuration entity.
    Integer ID used for fast joins with massive content tables.
    """
    __tablename__ = 'source'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    base_url = db.Column(db.String(512), nullable=False)
    source_type = db.Column(db.String(50), nullable=False) # e.g., 'rss', 'api', 'custom'
    country = db.Column(db.String(100), nullable=True)
    
    trust_score = db.Column(db.Float, default=0.0)
    bias_score = db.Column(db.Float, default=0.0)
    
    # Scraper configuration
    refresh_interval = db.Column(db.Integer, default=60) # Interval in minutes
    last_scraped_at = db.Column(db.DateTime, nullable=True)
    next_scrape_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    news_items = db.relationship('News', backref='source', lazy=True)
    research_papers = db.relationship('ResearchPaper', backref='source', lazy=True)
