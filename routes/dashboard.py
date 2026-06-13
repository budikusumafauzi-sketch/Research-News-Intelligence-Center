from flask import Blueprint, render_template
from services.news_service import NewsService
from services.intelligence_service import IntelligenceService
from services.entity_service import EntityService
from services.strategic_service import StrategicService

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    """Main dashboard rendering the UI prototype with real DB news feed."""
    latest_news = NewsService.get_latest_news(limit=6)
    latest_intelligence = IntelligenceService.get_latest_intelligence(limit=4)
    entity_graph = EntityService.get_entity_graph(limit_entities=5, limit_relationships=10)
    
    opportunities = StrategicService.get_latest_signals_by_type("Opportunity", limit=3)
    risks = StrategicService.get_latest_signals_by_type("Risk", limit=3)
    trends = StrategicService.get_latest_signals_by_type("Emerging Trend", limit=3)
    competition = StrategicService.get_latest_signals_by_type("Competitive Activity", limit=3)
    
    return render_template('dashboard.html', 
                           latest_news=latest_news, 
                           latest_intelligence=latest_intelligence,
                           entity_graph=entity_graph,
                           opportunities=opportunities,
                           risks=risks,
                           trends=trends,
                           competition=competition)
