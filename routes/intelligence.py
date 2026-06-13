from flask import Blueprint, jsonify, render_template, abort
from services.intelligence_service import IntelligenceService
from extensions import db
from models.intelligence import Intelligence
from models.entity import Entity
from models.strategic_signal import StrategicSignal

intelligence_bp = Blueprint('intelligence', __name__)


def _serialize(record):
    """Shared serializer — consistent shape across all endpoints."""
    return {
        "id":               record.id,
        "content_type":     record.content_type,
        "content_id":       record.content_id,
        "summary":          record.summary,
        "topics":           record.topics or [],
        "entities":         record.entities or [],
        "confidence_score": record.confidence_score,
        "provider":         record.provider,
        "created_at":       record.created_at.isoformat() if record.created_at else None,
    }


@intelligence_bp.route('/', methods=['GET'])
def get_all_intelligence():
    """GET /intelligence — Returns the 20 most recent intelligence records."""
    records = IntelligenceService.get_latest_intelligence(limit=20)
    return jsonify([_serialize(r) for r in records])


@intelligence_bp.route('/latest', methods=['GET'])
def get_latest_intelligence():
    """GET /intelligence/latest — Same as above, named alias."""
    records = IntelligenceService.get_latest_intelligence(limit=10)
    return jsonify([_serialize(r) for r in records])


@intelligence_bp.route('/news/<string:news_id>', methods=['GET'])
def get_news_intelligence(news_id):
    """GET /intelligence/news/<uuid> — Returns the intelligence for a specific news item."""
    record = IntelligenceService.get_intelligence_for('news', news_id)
    if not record:
        return jsonify({"error": "No intelligence found for this news item"}), 404
    return jsonify(_serialize(record))


@intelligence_bp.route('/research/<string:paper_id>', methods=['GET'])
def get_research_intelligence(paper_id):
    """GET /intelligence/research/<uuid> — Returns the intelligence for a specific paper."""
    record = IntelligenceService.get_intelligence_for('research', paper_id)
    if not record:
        return jsonify({"error": "No intelligence found for this research paper"}), 404
    return jsonify(_serialize(record))

@intelligence_bp.route('/<string:intelligence_id>', methods=['GET'])
def intelligence_explorer(intelligence_id):
    """GET /intelligence/<intelligence_id> — Renders Intelligence Explorer page."""
    record = Intelligence.query.filter_by(id=intelligence_id, is_deleted=False).first()
    if not record:
        abort(404)

    # Related Entities
    related_entities = []
    if record.entities:
        related_entities = Entity.query.filter(
            Entity.name.in_(record.entities),
            Entity.is_deleted == False
        ).all()
        
    # Related Intelligence
    related_intelligence = []
    if record.entities:
        conditions = [Intelligence.entities.ilike(f'%"{e}"%') for e in record.entities]
        related_intelligence = Intelligence.query.filter(
            Intelligence.id != record.id,
            Intelligence.is_deleted == False,
            db.or_(*conditions)
        ).order_by(Intelligence.created_at.desc()).limit(10).all()

    # Strategic Signals
    strategic_signals = []
    if record.entities:
        signal_conditions = []
        for e in record.entities:
            signal_conditions.append(StrategicSignal.title.ilike(f'%{e}%'))
            signal_conditions.append(StrategicSignal.description.ilike(f'%{e}%'))
        
        strategic_signals = StrategicSignal.query.filter(
            StrategicSignal.is_deleted == False,
            db.or_(*signal_conditions)
        ).order_by(StrategicSignal.created_at.desc()).limit(5).all()

    return render_template(
        'intelligence_detail.html',
        intelligence=record,
        related_entities=related_entities,
        related_intelligence=related_intelligence,
        strategic_signals=strategic_signals
    )
