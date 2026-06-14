from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from extensions import db
from models.bookmark import Bookmark
from models.intelligence import Intelligence
from models.entity import Entity

bookmarks_bp = Blueprint('bookmarks', __name__)

@bookmarks_bp.route('/')
def index():
    """Watchlist page: shows bookmarked intelligence and entities."""
    bookmarks = Bookmark.query.order_by(Bookmark.created_at.desc()).all()
    
    saved_intelligence = []
    monitored_entities = []
    
    for b in bookmarks:
        if b.bookmark_type == 'intelligence':
            intel = Intelligence.query.get(b.target_id)
            if intel and not intel.is_deleted:
                saved_intelligence.append({"bookmark": b, "record": intel})
        elif b.bookmark_type == 'entity':
            ent = Entity.query.get(b.target_id)
            if ent and not ent.is_deleted:
                monitored_entities.append({"bookmark": b, "record": ent})
                
    return render_template(
        'bookmarks.html',
        saved_intelligence=saved_intelligence,
        monitored_entities=monitored_entities
    )

@bookmarks_bp.route('/intelligence/<string:intelligence_id>', methods=['POST'])
def bookmark_intelligence(intelligence_id):
    """Bookmark an intelligence record."""
    existing = Bookmark.query.filter_by(bookmark_type='intelligence', target_id=intelligence_id).first()
    if not existing:
        new_bookmark = Bookmark(bookmark_type='intelligence', target_id=intelligence_id)
        db.session.add(new_bookmark)
        db.session.commit()
    return redirect(request.referrer or url_for('bookmarks.index'))

@bookmarks_bp.route('/entities/<string:entity_id>', methods=['POST'])
def bookmark_entity(entity_id):
    """Bookmark an entity."""
    existing = Bookmark.query.filter_by(bookmark_type='entity', target_id=entity_id).first()
    if not existing:
        new_bookmark = Bookmark(bookmark_type='entity', target_id=entity_id)
        db.session.add(new_bookmark)
        db.session.commit()
    return redirect(request.referrer or url_for('bookmarks.index'))

@bookmarks_bp.route('/delete/<string:bookmark_id>', methods=['POST'])
def delete_bookmark(bookmark_id):
    """Remove a bookmark."""
    bookmark = Bookmark.query.get(bookmark_id)
    if bookmark:
        db.session.delete(bookmark)
        db.session.commit()
    return redirect(url_for('bookmarks.index'))
