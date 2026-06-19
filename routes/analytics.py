from flask import Blueprint, jsonify, render_template
from models.analytics import AnalyticsCache

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard')
def dashboard():
    trends = AnalyticsCache.query.filter_by(key='trending_topics').first()
    momentum = AnalyticsCache.query.filter_by(key='entity_momentum').first()
    emerging = AnalyticsCache.query.filter_by(key='emerging_tech').first()
    
    return render_template('analytics.html', 
        trends=trends.data['trends'] if trends else [],
        momentum=momentum.data['momentum'] if momentum else [],
        emerging=emerging.data['technologies'] if emerging else []
    )

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
