from flask import Blueprint, jsonify
from services.intelligence_service import IntelligenceService

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
