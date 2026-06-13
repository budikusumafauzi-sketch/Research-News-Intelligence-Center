from flask import Blueprint, jsonify

bookmarks_bp = Blueprint('bookmarks', __name__)

@bookmarks_bp.route('/')
def index():
    """Bookmarks module placeholder."""
    return jsonify({
        "status": "success",
        "module": "bookmarks",
        "message": "Bookmarks blueprint is active."
    })
