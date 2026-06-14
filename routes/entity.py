from flask import Blueprint, jsonify, render_template, abort
from services.entity_service import EntityService
from models.entity import Entity
from models.intelligence import Intelligence
from models.entity_relationship import EntityRelationship
from models.strategic_signal import StrategicSignal
from models.analytics import AnalyticsCache
from sqlalchemy import or_

entity_bp = Blueprint('entity', __name__)

def _serialize_entity(e):
    return {
        "id": e.id,
        "name": e.name,
        "entity_type": e.entity_type,
        "description": e.description,
        "confidence_score": e.confidence_score
    }

@entity_bp.route('/', methods=['GET'])
def get_entities():
    """GET /entities"""
    entities = EntityService.get_top_entities(limit=50)
    return jsonify([_serialize_entity(e) for e in entities])

@entity_bp.route('/top', methods=['GET'])
def get_top_entities():
    """GET /entities/top"""
    entities = EntityService.get_top_entities(limit=5)
    return jsonify([_serialize_entity(e) for e in entities])

@entity_bp.route('/<string:entity_id>', methods=['GET'])
def get_entity_by_id(entity_id):
    """GET /entities/<uuid>"""
    e = Entity.query.get(entity_id)
    if not e or e.is_deleted:
        abort(404)

    from models.bookmark import Bookmark
    bookmark = Bookmark.query.filter_by(bookmark_type='entity', target_id=e.id).first()
    is_bookmarked = bookmark is not None
    bookmark_id = bookmark.id if bookmark else None

    # 1. Intelligence Context (Up to 10 recent)
    # Using string matching since entities is JSON
    recent_intel = Intelligence.query.filter(
        Intelligence.entities.like(f'%"{e.name}"%')
    ).order_by(Intelligence.created_at.desc()).limit(10).all()

    # 2. Related Entities (Up to 10)
    related_rels = EntityRelationship.query.filter(
        (EntityRelationship.source_entity_id == e.id) | (EntityRelationship.target_entity_id == e.id)
    ).order_by(EntityRelationship.confidence_score.desc()).limit(10).all()

    related_entities = []
    for rel in related_rels:
        if rel.source_entity_id == e.id:
            if rel.target_entity and not rel.target_entity.is_deleted:
                related_entities.append({"entity": rel.target_entity, "score": rel.confidence_score})
        else:
            if rel.source_entity and not rel.source_entity.is_deleted:
                related_entities.append({"entity": rel.source_entity, "score": rel.confidence_score})

    # 3. Strategic Signals (Up to 5)
    signals = StrategicSignal.query.filter(
        StrategicSignal.description.like(f'%{e.name}%')
    ).order_by(StrategicSignal.created_at.desc()).limit(5).all()

    # 4. Momentum Analytics
    cache = AnalyticsCache.query.filter_by(key='entity_momentum').first()
    momentum_score = 50.0
    trend_direction = 'stable'
    if cache and cache.data and 'momentum' in cache.data:
        for item in cache.data['momentum']:
            if item.get('entity') == e.name:
                momentum_score = item.get('momentum_score', 50.0)
                trend_direction = item.get('direction', 'stable')
                break

    # Determine trend text (just a helper string, logic in template or here)
    if momentum_score > 70:
        trend_direction_text = 'Rising'
    elif momentum_score < 40:
        trend_direction_text = 'Declining'
    else:
        trend_direction_text = 'Stable'

    return render_template('entity_detail.html', 
                           entity=e, 
                           intelligence=recent_intel,
                           related_entities=related_entities,
                           signals=signals,
                           momentum_score=momentum_score,
                           trend_direction=trend_direction_text,
                           is_bookmarked=is_bookmarked,
                           bookmark_id=bookmark_id)

@entity_bp.route('/graph', methods=['GET'])
def get_entity_graph():
    """GET /entities/graph"""
    graph_data = EntityService.get_entity_graph(limit_entities=5, limit_relationships=10)
    return jsonify(graph_data)
