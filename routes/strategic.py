from flask import Blueprint, jsonify
from services.strategic_service import StrategicService

strategic_bp = Blueprint('strategic', __name__)

@strategic_bp.route('/opportunities', methods=['GET'])
def get_opportunities():
    """Get the latest opportunity signals."""
    signals = StrategicService.get_latest_signals_by_type("Opportunity", limit=10)
    return jsonify({
        "status": "success",
        "data": [signal.to_dict() for signal in signals]
    }), 200

@strategic_bp.route('/risks', methods=['GET'])
def get_risks():
    """Get the latest risk signals."""
    signals = StrategicService.get_latest_signals_by_type("Risk", limit=10)
    return jsonify({
        "status": "success",
        "data": [signal.to_dict() for signal in signals]
    }), 200

@strategic_bp.route('/trends', methods=['GET'])
def get_trends():
    """Get the latest emerging trend signals."""
    signals = StrategicService.get_latest_signals_by_type("Emerging Trend", limit=10)
    return jsonify({
        "status": "success",
        "data": [signal.to_dict() for signal in signals]
    }), 200

@strategic_bp.route('/competition', methods=['GET'])
def get_competition():
    """Get the latest competitive activity signals."""
    signals = StrategicService.get_latest_signals_by_type("Competitive Activity", limit=10)
    return jsonify({
        "status": "success",
        "data": [signal.to_dict() for signal in signals]
    }), 200
