from flask import Blueprint, jsonify

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def index():
    """Admin module placeholder."""
    return jsonify({
        "status": "success",
        "module": "admin",
        "message": "Admin blueprint is active."
    })
