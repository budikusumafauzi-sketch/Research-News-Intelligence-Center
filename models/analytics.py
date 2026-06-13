from extensions import db
from datetime import datetime

class TrendSnapshot(db.Model):
    __tablename__ = 'trend_snapshot'
    
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False, index=True)
    snapshot_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    mention_count = db.Column(db.Integer, default=0, nullable=False)
    average_sentiment = db.Column(db.Float, default=0.0, nullable=False)

class ActivityLog(db.Model):
    __tablename__ = 'activity_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, index=True)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

class AnalyticsCache(db.Model):
    """Stores singleton analytics results for O(1) dashboard reads."""
    __tablename__ = 'analytics_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False, index=True)
    data = db.Column(db.JSON, nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

