import uuid
from extensions import db
from models.base import BaseModel

class Alert(BaseModel):
    __tablename__ = 'alert'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_id = db.Column(db.String(36), db.ForeignKey('entity.id'), nullable=False, index=True)
    intelligence_id = db.Column(db.String(36), db.ForeignKey('intelligence.id'), nullable=False, index=True)
    
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)

    # Relationships
    entity = db.relationship('Entity', backref=db.backref('alerts', lazy=True))
    intelligence = db.relationship('Intelligence', backref=db.backref('alerts', lazy=True))
