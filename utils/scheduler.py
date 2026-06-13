from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from services.news_service import NewsService
from services.research_service import ResearchService
from services.intelligence_service import IntelligenceService
from services.entity_service import EntityService
from services.analytics_service import AnalyticsService
from services.strategic_service import StrategicService
import logging

logger = logging.getLogger(__name__)

# Initialize background scheduler globally
scheduler = BackgroundScheduler(daemon=True)


def fetch_rss_job(app):
    """Job wrapper passing app context to SQLAlchemy."""
    with app.app_context():
        try:
            NewsService.fetch_latest_news()
        except Exception as e:
            logger.error(f"Error executing fetch_rss_job: {e}")


def fetch_research_job(app):
    """Job wrapper for research paper synchronization."""
    with app.app_context():
        try:
            ResearchService.fetch_latest_papers()
        except Exception as e:
            logger.error(f"Error executing fetch_research_job: {e}")


def generate_intelligence_job(app):
    """Job wrapper for batch intelligence generation every 1 hour."""
    with app.app_context():
        try:
            IntelligenceService.generate_batch_intelligence()
        except Exception as e:
            logger.error(f"Error executing generate_intelligence_job: {e}")


def discover_entities_job(app):
    """Job wrapper for entity and relationship discovery every 2 hours."""
    with app.app_context():
        try:
            EntityService.process_intelligence_records()
        except Exception as e:
            logger.error(f"Error executing discover_entities_job: {e}")

def calculate_trends_job(app):
    """Job wrapper for calculating trending topics every 2 hours."""
    with app.app_context():
        try:
            AnalyticsService.calculate_trending_topics()
        except Exception as e:
            logger.error(f"Error executing calculate_trends_job: {e}")

def calculate_momentum_job(app):
    """Job wrapper for calculating entity momentum every 2 hours."""
    with app.app_context():
        try:
            AnalyticsService.calculate_entity_momentum()
        except Exception as e:
            logger.error(f"Error executing calculate_momentum_job: {e}")

def detect_emerging_job(app):
    """Job wrapper for detecting emerging technologies every 6 hours."""
    with app.app_context():
        try:
            AnalyticsService.detect_emerging_technologies()
        except Exception as e:
            logger.error(f"Error executing detect_emerging_job: {e}")

def generate_strategic_signals_job(app):
    """Job wrapper for generating strategic signals every 6 hours (Phase 8)."""
    with app.app_context():
        try:
            StrategicService.generate_strategic_signals()
        except Exception as e:
            logger.error(f"Error executing generate_strategic_signals_job: {e}")


def refresh_source_stats_job(app):
    """Job to update analytics daily (Placeholder for Phase 7)."""
    with app.app_context():
        logger.info("Scheduler: Refreshing source statistics (Daily Run).")


def init_scheduler(app):
    """Registers and starts APScheduler jobs."""
    if not scheduler.running:
        # Every 15 minutes: fetch RSS feeds (Phase 5.1 — upgraded from 30 min)
        scheduler.add_job(
            func=fetch_rss_job,
            trigger=IntervalTrigger(minutes=15),
            args=[app],
            id='fetch_rss_feeds',
            name='Fetch RSS feeds every 15 minutes',
            replace_existing=True
        )

        # Every 6 hours: fetch research papers (Phase 5.1 — upgraded from 12 hr)
        scheduler.add_job(
            func=fetch_research_job,
            trigger=IntervalTrigger(hours=6),
            args=[app],
            id='fetch_research_papers',
            name='Fetch research papers every 6 hours',
            replace_existing=True
        )

        # Every 1 hour: generate intelligence (Phase 5.1 — upgraded from 6 hr)
        scheduler.add_job(
            func=generate_intelligence_job,
            trigger=IntervalTrigger(hours=1),
            args=[app],
            id='generate_intelligence',
            name='Generate intelligence every 1 hour',
            replace_existing=True
        )

        # Every 2 hours: discover entities (Phase 6)
        scheduler.add_job(
            func=discover_entities_job,
            trigger=IntervalTrigger(hours=2),
            args=[app],
            id='discover_entities',
            name='Discover entities every 2 hours',
            replace_existing=True
        )

        # Every 2 hours: calculate trends (Phase 7)
        scheduler.add_job(
            func=calculate_trends_job,
            trigger=IntervalTrigger(hours=2),
            args=[app],
            id='calculate_trends',
            name='Calculate trending topics every 2 hours',
            replace_existing=True
        )

        # Every 2 hours: calculate momentum (Phase 7)
        scheduler.add_job(
            func=calculate_momentum_job,
            trigger=IntervalTrigger(hours=2),
            args=[app],
            id='calculate_momentum',
            name='Calculate entity momentum every 2 hours',
            replace_existing=True
        )

        # Every 6 hours: detect emerging technologies (Phase 7)
        scheduler.add_job(
            func=detect_emerging_job,
            trigger=IntervalTrigger(hours=6),
            args=[app],
            id='detect_emerging',
            name='Detect emerging technologies every 6 hours',
            replace_existing=True
        )

        # Every 6 hours: generate strategic signals (Phase 8)
        scheduler.add_job(
            func=generate_strategic_signals_job,
            trigger=IntervalTrigger(hours=6),
            args=[app],
            id='generate_strategic_signals',
            name='Generate strategic signals every 6 hours',
            replace_existing=True
        )

        # Every 24 hours: refresh stats (unchanged)
        scheduler.add_job(
            func=refresh_source_stats_job,
            trigger=IntervalTrigger(hours=24),
            args=[app],
            id='refresh_source_stats',
            name='Refresh source statistics daily',
            replace_existing=True
        )

        scheduler.start()
        logger.info("APScheduler initialized and running background jobs.")
