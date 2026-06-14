"""
services/intelligence_service.py

Orchestrates intelligence generation across news and research content.
Uses the provider abstraction in ai/provider.py — swap LocalIntelligenceProvider
for any future paid provider without touching this file.
"""

import logging
from extensions import db
from models.intelligence import Intelligence
from models.content import News, ResearchPaper
from ai.provider import LocalIntelligenceProvider

logger = logging.getLogger(__name__)

# Instantiate the active provider once — easily swappable
_provider = LocalIntelligenceProvider()


class IntelligenceService:

    # ------------------------------------------------------------------
    # Core generation
    # ------------------------------------------------------------------

    @staticmethod
    def generate_intelligence(content_type: str, content_id: str, text: str, title: str = '') -> Intelligence | None:
        """
        Generates and persists a single Intelligence record for a content item.
        Skips if a record already exists (idempotent).

        Args:
            content_type: 'news' | 'research'
            content_id:   UUID of the target record
            text:         Raw content to analyse (article body or abstract)
            title:        Optional title prepended to text for richer context

        Returns:
            Persisted Intelligence instance, or None if skipped / failed.
        """
        # Guard: skip if already analysed
        existing = Intelligence.query.filter_by(
            content_type=content_type,
            content_id=content_id
        ).first()

        if existing:
            logger.info(f"Skipped intelligence generation because record already exists: {content_id}")
            return None

        full_text = f"{title}\n\n{text}".strip() if title else text

        try:
            summary  = _provider.summarize(full_text)
            topics   = _provider.extract_topics(full_text)
            entities = _provider.extract_entities(full_text)
            confidence = _provider.generate_confidence(full_text, len(entities), len(topics))

            record = Intelligence(
                content_type=content_type,
                content_id=content_id,
                summary=summary,
                topics=topics,
                entities=entities,
                confidence_score=confidence,
                provider=_provider.PROVIDER_NAME
            )
            db.session.add(record)
            db.session.commit()

            logger.info(f"Intelligence generated successfully for {content_type}:{content_id} "
                        f"[confidence={confidence}, topics={len(topics)}, entities={len(entities)}]")
                        
            # Phase 10.5: Generate alerts for monitored entities
            IntelligenceService._generate_alerts_for_intelligence(record)
            
            return record

        except Exception as e:
            db.session.rollback()
            logger.error(f"Intelligence generation failed for {content_type}:{content_id} — {e}")
            return None

    # ------------------------------------------------------------------
    # Alert Generation logic (Phase 10.5)
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_alerts_for_intelligence(record: Intelligence):
        from models.entity import Entity
        from models.bookmark import Bookmark
        from models.alert import Alert

        if not record.entities:
            return

        alerts_created = 0
        for entity_name in record.entities:
            entity = Entity.query.filter_by(name=entity_name, is_deleted=False).first()
            if not entity:
                continue
                
            bookmark = Bookmark.query.filter_by(bookmark_type='entity', target_id=entity.id).first()
            if not bookmark:
                continue
                
            existing_alert = Alert.query.filter_by(entity_id=entity.id, intelligence_id=record.id).first()
            if not existing_alert:
                title = f"Watchlist Update: {entity.name}"
                message = f"New intelligence involving {entity.name} has been detected."
                new_alert = Alert(
                    entity_id=entity.id,
                    intelligence_id=record.id,
                    title=title,
                    message=message
                )
                db.session.add(new_alert)
                alerts_created += 1
        
        if alerts_created > 0:
            try:
                db.session.commit()
                logger.info(f"Generated {alerts_created} alerts for intelligence {record.id}")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Failed to generate alerts for intelligence {record.id}: {e}")

    # ------------------------------------------------------------------
    # Typed convenience methods
    # ------------------------------------------------------------------

    @staticmethod
    def generate_news_intelligence(news: News) -> Intelligence | None:
        """Generate intelligence for a single News record."""
        text = news.content_raw or ''
        return IntelligenceService.generate_intelligence('news', news.id, text, news.title)

    @staticmethod
    def generate_research_intelligence(research: ResearchPaper) -> Intelligence | None:
        """Generate intelligence for a single ResearchPaper record."""
        text = research.abstract or ''
        return IntelligenceService.generate_intelligence('research', research.id, text, research.title)

    # ------------------------------------------------------------------
    # Batch job (called by scheduler every 6 hours)
    # ------------------------------------------------------------------

    @staticmethod
    def generate_batch_intelligence():
        """
        Processes the latest 20 news articles and 20 research papers.
        Records that already have intelligence entries are automatically
        skipped inside generate_intelligence() — no pre-filtering needed.
        """
        logger.info("Batch intelligence generation started.")
        generated = 0

        # Latest 20 news items
        news_items = (
            News.query
            .filter_by(is_deleted=False)
            .order_by(News.published_at.desc())
            .limit(20)
            .all()
        )
        for item in news_items:
            result = IntelligenceService.generate_news_intelligence(item)
            if result:
                generated += 1

        # Latest 20 research papers
        papers = (
            ResearchPaper.query
            .filter_by(is_deleted=False)
            .order_by(ResearchPaper.published_at.desc())
            .limit(20)
            .all()
        )
        for paper in papers:
            result = IntelligenceService.generate_research_intelligence(paper)
            if result:
                generated += 1

        logger.info(f"Batch intelligence generation completed. {generated} new records created.")

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    @staticmethod
    def get_latest_intelligence(limit: int = 20) -> list:
        """Returns the most recently generated intelligence records."""
        return (
            Intelligence.query
            .filter_by(is_deleted=False)
            .order_by(Intelligence.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_intelligence_for(content_type: str, content_id: str) -> Intelligence | None:
        """Returns the intelligence record for a specific content item."""
        return Intelligence.query.filter_by(
            content_type=content_type,
            content_id=content_id,
            is_deleted=False
        ).first()
