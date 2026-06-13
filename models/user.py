import uuid
from extensions import db
from models.base import BaseModel

class User(BaseModel):
    __tablename__ = 'user'
    
    # Using String(36) to store UUID natively and maintain high compatibility.
    # In extremely high-scale enterprise systems, BINARY(16) could be substituted.
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user', nullable=False)

    # Relationships
    bookmarks = db.relationship('Bookmark', backref='user', lazy=True)
    activity_logs = db.relationship('ActivityLog', backref='user', lazy=True)
