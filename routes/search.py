from flask import Blueprint, request, render_template
from sqlalchemy import or_

from extensions import db
from models.intelligence import Intelligence
from models.entity import Entity
from models.strategic_signal import StrategicSignal

search_bp = Blueprint('search', __name__)

@search_bp.route('', methods=['GET'])
def search():
    q = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    intelligence_results = None
    entity_results = None
    signal_results = None

    if q:
        search_pattern = f"%{q}%"
        
        if search_type in ['all', 'intelligence']:
            # Search intelligence
            intelligence_query = Intelligence.query.filter(
                Intelligence.is_deleted == False,
                Intelligence.summary.ilike(search_pattern)
            ).order_by(Intelligence.confidence_score.desc())
            intelligence_results = intelligence_query.paginate(page=page, per_page=per_page, error_out=False)

        if search_type in ['all', 'entities']:
            # Search entities
            entity_query = Entity.query.filter(
                Entity.is_deleted == False,
                Entity.name.ilike(search_pattern)
            ).order_by(Entity.confidence_score.desc())
            entity_results = entity_query.paginate(page=page, per_page=per_page, error_out=False)

        if search_type in ['all', 'strategic_signals']:
            # Search strategic signals
            signal_query = StrategicSignal.query.filter(
                StrategicSignal.is_deleted == False,
                or_(
                    StrategicSignal.title.ilike(search_pattern),
                    StrategicSignal.description.ilike(search_pattern)
                )
            ).order_by(StrategicSignal.confidence_score.desc())
            signal_results = signal_query.paginate(page=page, per_page=per_page, error_out=False)

    # Calculate overall pagination variables
    has_prev = False
    has_next = False
    total_pages = 1
    
    for res in [intelligence_results, entity_results, signal_results]:
        if res:
            if res.has_prev:
                has_prev = True
            if res.has_next:
                has_next = True
            if res.pages > total_pages:
                total_pages = res.pages

    return render_template(
        'search_results.html',
        q=q,
        type=search_type,
        page=page,
        has_prev=has_prev,
        has_next=has_next,
        total_pages=total_pages,
        intelligence_results=intelligence_results,
        entity_results=entity_results,
        signal_results=signal_results
    )
