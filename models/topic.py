from extensions import db

class Topic(db.Model):
    __tablename__ = 'topic'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False, index=True)
    category = db.Column(db.String(100), nullable=True)

    # Relationships
    trend_snapshots = db.relationship('TrendSnapshot', backref='topic', lazy=True)
    ai_insights = db.relationship('AIInsight', backref='topic', lazy=True)
