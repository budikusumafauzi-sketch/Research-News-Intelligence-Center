from flask import Blueprint, render_template
from services.news_service import NewsService
from services.intelligence_service import IntelligenceService
from services.entity_service import EntityService
from services.strategic_service import StrategicService
from models.intelligence import Intelligence
from models.entity import Entity
from models.alert import Alert
from models.bookmark import Bookmark

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/settings')
def settings():
    """GET /settings"""
    stats = {
        "intelligence": Intelligence.query.count(),
        "entities": Entity.query.count(),
        "alerts": Alert.query.count(),
        "watchlists": Bookmark.query.count()
    }
    return render_template('settings.html', stats=stats)

@dashboard_bp.route('/profile')
def profile():
    """GET /profile"""
    stats = {
        "alerts": Alert.query.count(),
        "watchlists": Bookmark.query.count(),
        "entities": Entity.query.count(),
        "intelligence": Intelligence.query.count()
    }
    return render_template('profile.html', stats=stats)

@dashboard_bp.route('/')
def index():
    """Main dashboard rendering."""

    latest_news = NewsService.get_latest_news(limit=6)

    latest_intelligence = IntelligenceService.get_latest_intelligence(limit=15)

    latest_feed = IntelligenceService.get_latest_feed(limit=15)

    entity_graph = EntityService.get_entity_graph(
        limit_entities=8,
    )

    opportunities = StrategicService.get_latest_signals_by_type(
        "Opportunity",
        limit=3
    )

    risks = StrategicService.get_latest_signals_by_type(
        "Risk",
        limit=3
    )

    trends = StrategicService.get_latest_signals_by_type(
        "Emerging Trend",
        limit=3
    )

    competition = StrategicService.get_latest_signals_by_type(
        "Competitive Activity",
        limit=3
    )

    return render_template(
        'dashboard.html',
        latest_news=latest_news,
        latest_intelligence=latest_intelligence,
        latest_feed=latest_feed,
        entity_graph=entity_graph,
        opportunities=opportunities,
        risks=risks,
        trends=trends,
        competition=competition
    )
