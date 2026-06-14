from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from extensions import db
from models.alert import Alert

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/')
def index():
    """Render Alert Center."""
    alerts = Alert.query.order_by(Alert.created_at.desc()).all()
    
    unread_alerts = [a for a in alerts if not a.is_read]
    read_alerts = [a for a in alerts if a.is_read]
    
    return render_template(
        'alerts.html',
        unread_alerts=unread_alerts,
        read_alerts=read_alerts
    )

@alerts_bp.route('/read/<string:alert_id>', methods=['POST'])
def mark_read(alert_id):
    """Mark a single alert as read."""
    alert = Alert.query.get(alert_id)
    if alert and not alert.is_read:
        alert.is_read = True
        db.session.commit()
    return redirect(request.referrer or url_for('alerts.index'))

@alerts_bp.route('/read-all', methods=['POST'])
def mark_all_read():
    """Mark all alerts as read."""
    unread_alerts = Alert.query.filter_by(is_read=False).all()
    for alert in unread_alerts:
        alert.is_read = True
    
    if unread_alerts:
        db.session.commit()
        
    return redirect(request.referrer or url_for('alerts.index'))
