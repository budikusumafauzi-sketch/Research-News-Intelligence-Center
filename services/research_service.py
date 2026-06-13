import hashlib
import logging
from extensions import db
from models.content import ResearchPaper
from models.source import Source
from scraper.research_parser import ResearchParser

logger = logging.getLogger(__name__)


class ResearchService:

    @staticmethod
    def generate_content_hash(title, abstract):
        """Generate SHA-256 hash from title + abstract for deduplication."""
        safe_title = title or ""
        safe_abstract = abstract or ""
        return hashlib.sha256(
            f"{safe_title}{safe_abstract}".encode('utf-8')
        ).hexdigest()

    @staticmethod
    def fetch_latest_papers():
        """
        Triggered by APScheduler (every 12 hours) and at startup.
        Fetches papers from all configured research parsers and persists
        unique records to the database.
        """
        logger.info("Research synchronization started.")

        # Retrieve the arXiv source record seeded by SourceService
        arxiv_source = Source.query.filter_by(name='arXiv').first()
        if not arxiv_source:
            logger.warning("arXiv source not found in database. Skipping research fetch.")
            return

        papers = ResearchParser.fetch_arxiv()
        total_saved = 0

        for paper_data in papers:
            if ResearchService.save_paper(arxiv_source.id, paper_data):
                total_saved += 1

        db.session.commit()
        logger.info(f"Research synchronization completed. {total_saved} new papers saved.")

    @staticmethod
    def save_paper(source_id, paper_data):
        """
        Persists a single research paper after a two-pass deduplication check.
        Deduplication order:
          1. DOI uniqueness check (fast indexed lookup)
          2. Content hash uniqueness check (catches DOI-less duplicates)
          3. Database insert
        Returns True if saved, False if skipped.
        """
        doi = paper_data.get('doi')
        title = paper_data.get('title', 'Untitled')
        abstract = paper_data.get('abstract', '')

        # Pass 1: DOI uniqueness check
        if doi:
            if ResearchPaper.query.filter_by(doi=doi).first():
                logger.info(f"Duplicate DOI detected: {doi}")
                return False

        # Pass 2: Content hash uniqueness check
        content_hash = ResearchService.generate_content_hash(title, abstract)
        if ResearchPaper.query.filter_by(content_hash=content_hash).first():
            logger.info("Duplicate research content detected.")
            return False

        # Pass 3: Insert
        paper = ResearchPaper(
            source_id=source_id,
            doi=doi,
            title=title,
            abstract=abstract,
            authors=paper_data.get('authors', 'Unknown'),
            content_hash=content_hash,
            published_at=paper_data.get('published_at')
        )
        db.session.add(paper)
        logger.info(f"Research paper accepted: {title[:80]}")
        return True

    @staticmethod
    def get_latest_papers(limit=10):
        """Retrieve the most recently published papers."""
        return (
            ResearchPaper.query
            .filter_by(is_deleted=False)
            .order_by(ResearchPaper.published_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_paper_by_id(paper_id):
        """Fetch a specific research paper by its UUID."""
        return ResearchPaper.query.filter_by(
            id=paper_id, is_deleted=False
        ).first()

    @staticmethod
    def search_papers(query, limit=20):
        """Full-text search across title and abstract fields."""
        return (
            ResearchPaper.query
            .filter(
                ResearchPaper.is_deleted == False,
                ResearchPaper.title.ilike(f'%{query}%')
            )
            .order_by(ResearchPaper.published_at.desc())
            .limit(limit)
            .all()
        )
