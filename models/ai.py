import uuid
from extensions import db
from models.base import BaseModel

class AIInsight(BaseModel):
    __tablename__ = 'ai_insight'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Polymorphic associations allowing Insight to apply to News, Research, or a broader Topic
    news_id = db.Column(db.String(36), db.ForeignKey('news.id'), nullable=True, index=True)
    research_paper_id = db.Column(db.String(36), db.ForeignKey('research_paper.id'), nullable=True, index=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=True, index=True)
    
    summary = db.Column(db.Text, nullable=False)
    sentiment_score = db.Column(db.Float, nullable=True)
    tokens_used = db.Column(db.Integer, default=0)
    generated_at = db.Column(db.DateTime, nullable=False, index=True)

    # Relationships
    knowledge_relations = db.relationship('KnowledgeRelation', backref='ai_insight', lazy=True)

class KnowledgeRelation(BaseModel):
    __tablename__ = 'knowledge_relation'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ai_insight_id = db.Column(db.String(36), db.ForeignKey('ai_insight.id'), nullable=False, index=True)
    
    entity_a = db.Column(db.String(255), nullable=False, index=True)
    entity_b = db.Column(db.String(255), nullable=False, index=True)
    relationship_type = db.Column(db.String(255), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
