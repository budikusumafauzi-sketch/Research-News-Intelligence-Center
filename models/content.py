import uuid
from extensions import db
from models.base import BaseModel
from models.associations import news_topics, research_topics

class News(BaseModel):
    __tablename__ = 'news'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = db.Column(db.Integer, db.ForeignKey('source.id'), nullable=False, index=True)
    
    title = db.Column(db.String(512), nullable=False)
    content_raw = db.Column(db.Text, nullable=False)
    original_url = db.Column(db.String(1024), nullable=False)
    content_hash = db.Column(db.String(64), unique=True, nullable=True, index=True)
    published_at = db.Column(db.DateTime, nullable=False, index=True)

    # Relationships
    topics = db.relationship('Topic', secondary=news_topics, backref=db.backref('news_items', lazy='dynamic'))
    ai_insights = db.relationship('AIInsight', backref='news', lazy=True)
    bookmarks = db.relationship('Bookmark', backref='news', lazy=True)


class ResearchPaper(BaseModel):
    __tablename__ = 'research_paper'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_id = db.Column(db.Integer, db.ForeignKey('source.id'), nullable=False, index=True)
    
    doi = db.Column(db.String(255), nullable=True, index=True)
    title = db.Column(db.String(512), nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    authors = db.Column(db.Text, nullable=False)
    content_hash = db.Column(db.String(64), unique=True, nullable=True, index=True)
    published_at = db.Column(db.DateTime, nullable=False, index=True)

    # Relationships
    topics = db.relationship('Topic', secondary=research_topics, backref=db.backref('research_papers', lazy='dynamic'))
    ai_insights = db.relationship('AIInsight', backref='research_paper', lazy=True)
    bookmarks = db.relationship('Bookmark', backref='research_paper', lazy=True)
