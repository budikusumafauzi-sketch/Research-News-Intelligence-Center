from datetime import datetime
from extensions import db

class BaseModel(db.Model):
    """
    Abstract base model that provides timestamp mixins and soft-delete capabilities.
    Inherited by models that require lifecycle tracking and non-destructive deletion.
    """
    __abstract__ = True

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Soft delete support
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def soft_delete(self):
        """Perform a soft delete on the record."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        db.session.commit()
        
    def restore(self):
        """Restore a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None
        db.session.commit()
