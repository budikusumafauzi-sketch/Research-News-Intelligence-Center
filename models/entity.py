import uuid
from extensions import db
from models.base import BaseModel

class Entity(BaseModel):
    """
    Represents an automatically discovered entity (Company, Person, Technology, etc.)
    from intelligence records.
    """
    __tablename__ = 'entity'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False, index=True)
    entity_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    confidence_score = db.Column(db.Float, default=0.0, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('name', 'entity_type', name='uq_entity_name_type'),
    )

    # Relationships
    # A generic setup for relationships to other entities could be added here, 
    # but they are managed via EntityRelationship.
