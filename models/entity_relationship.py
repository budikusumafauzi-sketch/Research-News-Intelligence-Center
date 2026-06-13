import uuid
from extensions import db
from models.base import BaseModel

class EntityRelationship(BaseModel):
    """
    Represents a relationship between two entities automatically discovered from text.
    """
    __tablename__ = 'entity_relationship'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_entity_id = db.Column(db.String(36), db.ForeignKey('entity.id'), nullable=False, index=True)
    target_entity_id = db.Column(db.String(36), db.ForeignKey('entity.id'), nullable=False, index=True)
    relationship_type = db.Column(db.String(100), nullable=False)
    confidence_score = db.Column(db.Float, default=0.0, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('source_entity_id', 'target_entity_id', 'relationship_type', name='uq_entity_relationship'),
    )

    source_entity = db.relationship('Entity', foreign_keys=[source_entity_id], backref=db.backref('outgoing_relationships', lazy='dynamic'))
    target_entity = db.relationship('Entity', foreign_keys=[target_entity_id], backref=db.backref('incoming_relationships', lazy='dynamic'))
