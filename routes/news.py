from flask import Blueprint, jsonify, request
from services.news_service import NewsService

news_bp = Blueprint('news', __name__)

@news_bp.route('/', methods=['GET'])
def get_all_news():
    """GET /news"""
    news_list = NewsService.get_latest_news(limit=50)
    return jsonify([{
        "id": n.id,
        "title": n.title,
        "original_url": n.original_url,
        "published_at": n.published_at.isoformat() if n.published_at else None,
        "source": n.source.name if n.source else "Unknown"
    } for n in news_list])

@news_bp.route('/search', methods=['GET'])
def search_news():
    """GET /news/search"""
    query = request.args.get('q', '')
    if not query:
        return jsonify([])
    from models.content import News
    results = News.query.filter(News.title.ilike(f'%{query}%')).limit(20).all()
    return jsonify([{
        "id": n.id, "title": n.title
    } for n in results])

@news_bp.route('/trending', methods=['GET'])
def get_trending_news():
    """GET /news/trending"""
    news_list = NewsService.get_trending_news()
    return jsonify([{
        "id": n.id, "title": n.title
    } for n in news_list])

@news_bp.route('/<string:news_id>', methods=['GET'])
def get_news_by_id(news_id):
    """GET /news/<uuid>"""
    n = NewsService.get_news_by_id(news_id)
    if not n:
        return jsonify({"error": "News not found"}), 404
        
    return jsonify({
        "id": n.id,
        "title": n.title,
        "content_raw": n.content_raw,
        "original_url": n.original_url,
        "published_at": n.published_at.isoformat() if n.published_at else None,
        "source": n.source.name if n.source else "Unknown"
    })
