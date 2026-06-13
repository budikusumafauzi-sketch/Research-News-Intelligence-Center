from extensions import db

# Association table for News <-> Topic (Many-to-Many)
news_topics = db.Table('news_topics',
    db.Column('news_id', db.String(36), db.ForeignKey('news.id'), primary_key=True),
    db.Column('topic_id', db.Integer, db.ForeignKey('topic.id'), primary_key=True)
)

# Association table for ResearchPaper <-> Topic (Many-to-Many)
research_topics = db.Table('research_topics',
    db.Column('research_paper_id', db.String(36), db.ForeignKey('research_paper.id'), primary_key=True),
    db.Column('topic_id', db.Integer, db.ForeignKey('topic.id'), primary_key=True)
)
