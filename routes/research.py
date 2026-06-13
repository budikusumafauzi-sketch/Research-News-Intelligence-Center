from flask import Blueprint, jsonify, request
from services.research_service import ResearchService

research_bp = Blueprint('research', __name__)


@research_bp.route('/', methods=['GET'])
def get_all_research():
    """GET /research — Returns the 50 most recent research papers."""
    papers = ResearchService.get_latest_papers(limit=50)
    return jsonify([_serialize(p) for p in papers])


@research_bp.route('/latest', methods=['GET'])
def get_latest_research():
    """GET /research/latest — Returns the 10 most recent research papers."""
    papers = ResearchService.get_latest_papers(limit=10)
    return jsonify([_serialize(p) for p in papers])


@research_bp.route('/search', methods=['GET'])
def search_research():
    """GET /research/search?q= — Full-text search by title."""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    results = ResearchService.search_papers(query)
    return jsonify([_serialize(p) for p in results])


@research_bp.route('/<string:paper_id>', methods=['GET'])
def get_research_by_id(paper_id):
    """GET /research/<uuid> — Returns a single paper by UUID."""
    paper = ResearchService.get_paper_by_id(paper_id)
    if not paper:
        return jsonify({"error": "Research paper not found"}), 404
    return jsonify(_serialize(paper, full=True))


def _serialize(paper, full=False):
    """Shared serializer — keeps response shape consistent with news endpoints."""
    data = {
        "id": paper.id,
        "title": paper.title,
        "authors": paper.authors,
        "doi": paper.doi,
        "published_at": paper.published_at.isoformat() if paper.published_at else None,
        "source": paper.source.name if paper.source else "Unknown"
    }
    if full:
        data["abstract"] = paper.abstract
    return data
