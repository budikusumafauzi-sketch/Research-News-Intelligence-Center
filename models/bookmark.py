import uuid
from extensions import db
from models.base import BaseModel
from datetime import datetime

class Bookmark(BaseModel):
    __tablename__ = 'bookmark'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False, index=True)
    
    # Polymorphic link to either News or ResearchPaper
    news_id = db.Column(db.String(36), db.ForeignKey('news.id'), nullable=True, index=True)
    research_paper_id = db.Column(db.String(36), db.ForeignKey('research_paper.id'), nullable=True, index=True)
    
    saved_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
