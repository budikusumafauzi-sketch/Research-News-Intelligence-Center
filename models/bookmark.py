import uuid
from extensions import db
from models.base import BaseModel
from datetime import datetime

class Bookmark(BaseModel):
    __tablename__ = 'bookmark'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Valid types: "intelligence", "entity"
    bookmark_type = db.Column(db.String(50), nullable=False, index=True)
    target_id = db.Column(db.String(36), nullable=False, index=True)
    
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=True, index=True)
