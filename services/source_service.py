from extensions import db
from models.source import Source

INITIAL_SOURCES = [
    {"name": "Reuters Technology", "base_url": "https://www.reutersagency.com/feed/?best-topics=tech&type=rss", "source_type": "rss"},
    {"name": "BBC Technology", "base_url": "http://feeds.bbci.co.uk/news/technology/rss.xml", "source_type": "rss"},
    {"name": "TechCrunch", "base_url": "https://techcrunch.com/feed/", "source_type": "rss"},
    {"name": "The Verge", "base_url": "https://www.theverge.com/rss/index.xml", "source_type": "rss"},
    {"name": "Wired", "base_url": "https://www.wired.com/feed/rss", "source_type": "rss"},
    {"name": "arXiv", "base_url": "http://export.arxiv.org/api/query", "source_type": "api"},
    {"name": "Crossref", "base_url": "https://api.crossref.org/works", "source_type": "api"},
]

class SourceService:
    @staticmethod
    def seed_initial_sources():
        """Ensure initial RSS sources are populated in the database."""
        for s in INITIAL_SOURCES:
            existing = Source.query.filter_by(name=s["name"]).first()
            if not existing:
                source = Source(
                    name=s["name"], 
                    base_url=s["base_url"], 
                    source_type=s["source_type"]
                )
                db.session.add(source)
        db.session.commit()
