# Import all models here so Flask-Migrate and SQLAlchemy can discover them automatically
from models.associations import news_topics, research_topics
from models.user import User
from models.source import Source
from models.content import News, ResearchPaper
from models.topic import Topic
from models.analytics import TrendSnapshot, ActivityLog, AnalyticsCache
from models.ai import AIInsight, KnowledgeRelation
from models.bookmark import Bookmark
from models.intelligence import Intelligence
from models.entity import Entity
from models.entity_relationship import EntityRelationship
from models.strategic_signal import StrategicSignal
from models.alert import Alert

# This empty block guarantees __all__ exposes exactly what is needed for migrations.
__all__ = [
    'news_topics',
    'research_topics',
    'User',
    'Source',
    'News',
    'ResearchPaper',
    'Topic',
    'TrendSnapshot',
    'ActivityLog',
    'AnalyticsCache',
    'AIInsight',
    'KnowledgeRelation',
    'Bookmark',
    'Intelligence',
    'Entity',
    'EntityRelationship',
    'StrategicSignal',
    'Alert'
]
