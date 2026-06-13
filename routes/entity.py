from flask import Blueprint, jsonify
from services.entity_service import EntityService

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
    from models.entity import Entity
    e = Entity.query.get(entity_id)
    if not e or e.is_deleted:
        return jsonify({"error": "Entity not found"}), 404
    return jsonify(_serialize_entity(e))

@entity_bp.route('/graph', methods=['GET'])
def get_entity_graph():
    """GET /entities/graph"""
    graph_data = EntityService.get_entity_graph(limit_entities=5, limit_relationships=10)
    return jsonify(graph_data)
