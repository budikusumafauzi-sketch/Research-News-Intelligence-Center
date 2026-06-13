from flask import Blueprint, jsonify
from models.analytics import AnalyticsCache

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/trends')
def get_trends():
    cache = AnalyticsCache.query.filter_by(key='trending_topics').first()
    return jsonify(cache.data if cache else {"trends": []})

@analytics_bp.route('/momentum')
def get_momentum():
    cache = AnalyticsCache.query.filter_by(key='entity_momentum').first()
    return jsonify(cache.data if cache else {"momentum": []})

@analytics_bp.route('/emerging')
def get_emerging():
    cache = AnalyticsCache.query.filter_by(key='emerging_tech').first()
    return jsonify(cache.data if cache else {"technologies": []})
