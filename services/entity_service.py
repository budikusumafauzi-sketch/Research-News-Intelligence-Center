import logging
import re
from sqlalchemy import func
from extensions import db
from models.entity import Entity
from models.entity_relationship import EntityRelationship
from models.intelligence import Intelligence
from models.content import News, ResearchPaper

logger = logging.getLogger(__name__)

STOP_ENTITIES = {
    "The", "This", "These", "That", "Those", "Here", "There", "What", "When",
    "Where", "Who", "Why", "How", "Under", "Over", "After", "Before", "During",
    "Following", "Recent", "However", "Through", "Without", "Within", "Using",
    "Multi", "Self", "Such", "Many", "Several", "Some", "Most", "Few"
}

KNOWN_COMPANIES = {
    'Technology': {
        'Google', 'Meta', 'Microsoft', 'Apple', 'Amazon', 'Nvidia', 'OpenAI',
        'Anthropic', 'xAI', 'DeepMind', 'Waymo', 'Tesla', 'SpaceX', 'IBM',
        'Intel', 'AMD', 'Oracle', 'Adobe', 'Salesforce', 'Databricks',
        'Palantir', 'Snowflake'
    },
    'Research': {
        'OpenAI', 'DeepMind', 'Anthropic', 'Hugging Face'
    },
    'Media': {
        'Reuters', 'Bloomberg', 'CNBC', 'TechCrunch', 'Wired', 'The Verge'
    },
    'Social': {
        'TikTok', 'Snapchat', 'Discord', 'Reddit', 'LinkedIn'
    }
}

RELATIONSHIP_RULES = {
    'partnered_with': [r'partner(?:ed|s|ship)?\s+with', r'team(?:ed|s)?\s+up\s+with', r'collaborat(?:e|ed|ion)\s+with'],
    'invested_in': [r'invest(?:ed|s|ment)?\s+in', r'fund(?:ed|ing)?', r'back(?:ed)?\s+by', r'raised'],
    'competing_with': [r'compet(?:e|es|ing)\s+with', r'rival(?:s)?', r'vs\.?'],
    'acquired': [r'acquir(?:e|ed|es)', r'bought', r'purchas(?:e|ed|es)', r'takeover'],
    'developed': [r'develop(?:ed|s)?\s+by', r'built\s+by', r'creat(?:e|ed|es)\s+by', r'launch(?:ed|es)?'],
    'published': [r'publish(?:ed|es)?\s+by', r'releas(?:e|ed|es)\s+by']
}

class EntityService:

    @staticmethod
    def _determine_entity_type(name, topics):
        """Heuristic to determine entity type."""
        for category, companies in KNOWN_COMPANIES.items():
            if name in companies:
                if category == 'Technology': return 'Company'
                if category == 'Research': return 'ResearchOrganization'
                if category == 'Media': return 'MediaOrganization'
                if category == 'Social': return 'Company'
                
        lower_topics = [t.lower() for t in topics]
        lower_name = name.lower()
        
        if any(t in lower_name for t in ['ai', 'learning', 'network', 'model', 'api', 'quantum', 'cloud', 'robot']):
            return 'Technology'
            
        if any(t in lower_name for t in ['research', 'study', 'analysis', 'paper']):
            return 'ResearchOrganization'
            
        if any(t in lower_name for t in ['university', 'institute', 'college', 'academy']):
            return 'AcademicInstitution'
            
        return 'Organization'

    @classmethod
    def process_intelligence_records(cls, limit=50):
        """Extracts entities and relationships from recent intelligence records."""
        records = Intelligence.query.filter_by(is_deleted=False).order_by(Intelligence.created_at.desc()).limit(limit).all()
        
        entities_created = 0
        relationships_created = 0

        for record in records:
            # 1. Gather text context
            text_context = record.summary or ""
            
            # Optionally get title if available
            title = ""
            if record.content_type == 'news':
                news = News.query.get(record.content_id)
                if news: title = news.title
            elif record.content_type == 'research':
                paper = ResearchPaper.query.get(record.content_id)
                if paper: title = paper.title
                
            full_text = f"{title} {text_context}"
            topics = record.topics or []
            intel_entities = record.entities or []
            
            # 2. Extract entities (Priority 1 & 2 & 3 & 4 via heuristic)
            discovered_entities = set(intel_entities)
            
            # Priority 3: Regex title-case detection for any missed ones
            # Ignore common capitalized words, prioritize multi-word, strip whitespace/linebreaks, reject malformed fragments
            raw_matches = re.findall(r'\b(?:[A-Z][A-Za-z0-9&]*\s+)+[A-Z][A-Za-z0-9&]*\b|\b[A-Z][A-Za-z0-9&]*\b', full_text)
            for match in raw_matches:
                clean_match = match.strip().replace('\n', ' ').replace('\r', '')
                if len(clean_match) >= 4 and clean_match not in discovered_entities and clean_match not in STOP_ENTITIES:
                    if not re.search(r'[^\w\s&.\'-]', clean_match) and clean_match.lower() not in [s.lower() for s in STOP_ENTITIES]:
                        discovered_entities.add(clean_match)
            
            # Limit to top 10 entities per record to avoid noise
            discovered_entities = list(discovered_entities)[:10]
            
            # 3. Create or Update Entities
            db_entities = {}
            for e_name in discovered_entities:
                e_type = cls._determine_entity_type(e_name, topics)
                
                # Check if exists
                entity = Entity.query.filter_by(name=e_name, entity_type=e_type).first()
                if not entity:
                    initial_conf = 30.0
                    is_known = any(e_name in category for category in KNOWN_COMPANIES.values())
                    if is_known:
                        initial_conf += 5.0
                        
                    entity = Entity(
                        name=e_name,
                        entity_type=e_type,
                        description=f"Auto-discovered from {record.content_type}",
                        confidence_score=initial_conf
                    )
                    db.session.add(entity)
                    try:
                        db.session.commit()
                        entities_created += 1
                    except Exception:
                        db.session.rollback()
                        entity = Entity.query.filter_by(name=e_name, entity_type=e_type).first()
                else:
                    # Bump confidence slightly
                    bump = 2.0
                    is_known = any(e_name in category for category in KNOWN_COMPANIES.values())
                    if is_known:
                        bump += 5.0
                    
                    if entity.is_deleted:
                        entity.is_deleted = False
                        
                    entity.confidence_score = min(100.0, entity.confidence_score + bump)
                    db.session.commit()
                
                if entity:
                    db_entities[e_name] = entity

            # 4. Discover Relationships
            names = list(db_entities.keys())
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    name_a = names[i]
                    name_b = names[j]
                    ent_a = db_entities[name_a]
                    ent_b = db_entities[name_b]
                    
                    # Prevent self-relationships
                    if ent_a.id == ent_b.id:
                        continue
                    
                    # Determine relationship type
                    rel_type = 'mentioned_with'
                    lower_text = full_text.lower()
                    
                    # Check if they co-occur closely or match regex rules
                    if name_a.lower() in lower_text and name_b.lower() in lower_text:
                        for r_type, patterns in RELATIONSHIP_RULES.items():
                            for pattern in patterns:
                                if re.search(pattern, lower_text, re.IGNORECASE):
                                    rel_type = r_type
                                    break
                            if rel_type != 'mentioned_with':
                                break
                    
                    # Sort to avoid A->B and B->A duplicates for undirected (or always insert in consistent order)
                    src_id, tgt_id = (ent_a.id, ent_b.id) if ent_a.id < ent_b.id else (ent_b.id, ent_a.id)
                    
                    rel = EntityRelationship.query.filter_by(
                        source_entity_id=src_id,
                        target_entity_id=tgt_id,
                        relationship_type=rel_type
                    ).first()
                    
                    if not rel:
                        rel = EntityRelationship(
                            source_entity_id=src_id,
                            target_entity_id=tgt_id,
                            relationship_type=rel_type,
                            confidence_score=30.0 if rel_type == 'mentioned_with' else 70.0
                        )
                        db.session.add(rel)
                        try:
                            db.session.commit()
                            relationships_created += 1
                        except Exception:
                            db.session.rollback()
                            rel = EntityRelationship.query.filter_by(
                                source_entity_id=src_id,
                                target_entity_id=tgt_id,
                                relationship_type=rel_type
                            ).first()
                    else:
                        if hasattr(rel, 'is_deleted') and rel.is_deleted:
                            rel.is_deleted = False
                        rel.confidence_score = min(100.0, rel.confidence_score + 2.0)
                        db.session.commit()
                        
                    # Relationship participation: +1 confidence for entities
                    ent_a.confidence_score = min(100.0, ent_a.confidence_score + 1.0)
                    ent_b.confidence_score = min(100.0, ent_b.confidence_score + 1.0)
                    db.session.commit()

        logger.info(f"Entity discovery completed. Created {entities_created} entities, {relationships_created} relationships.")
        return {"entities": entities_created, "relationships": relationships_created}

    @classmethod
    def cleanup_low_quality_entities(cls):
        """Soft-deletes low quality entities and orphaned relationships."""
        all_entities = Entity.query.filter_by(is_deleted=False).all()
        deleted_count = 0
        
        stop_entities_lower = {s.lower() for s in STOP_ENTITIES}
        
        for entity in all_entities:
            should_delete = False
            name = entity.name
            
            if name in STOP_ENTITIES or name.lower() in stop_entities_lower:
                should_delete = True
            elif len(name) < 4:
                should_delete = True
            elif entity.confidence_score < 35.0:
                should_delete = True
            elif '\n' in name or '\r' in name:
                should_delete = True
                
            if should_delete:
                entity.is_deleted = True
                deleted_count += 1
                
        db.session.commit()
        
        # Soft-delete orphaned relationships
        all_rels = EntityRelationship.query.filter_by(is_deleted=False).all()
        rel_deleted_count = 0
        for rel in all_rels:
            ent_a = Entity.query.get(rel.source_entity_id)
            ent_b = Entity.query.get(rel.target_entity_id)
            if (not ent_a or ent_a.is_deleted) or (not ent_b or ent_b.is_deleted):
                rel.is_deleted = True
                rel_deleted_count += 1
                
        db.session.commit()
        logger.info(f"Cleanup completed. Deleted {deleted_count} entities and {rel_deleted_count} relationships.")
        return {"entities_deleted": deleted_count, "relationships_deleted": rel_deleted_count}

    @classmethod
    def get_top_entities(cls, limit=5):
        """Retrieves top entities by confidence."""
        return Entity.query.filter_by(is_deleted=False).order_by(Entity.confidence_score.desc()).limit(limit).all()

    @classmethod
    def get_entity_graph(cls, limit_entities=12):
    
        top_entities = (
            Entity.query
            .filter_by(is_deleted=False)
            .filter(Entity.entity_type == "Company")
            .order_by(Entity.confidence_score.desc())
            .limit(limit_entities)
            .all()
        )

        entity_ids = [e.id for e in top_entities]

        relationships = (
            EntityRelationship.query
            .filter(
                EntityRelationship.source_entity_id.in_(entity_ids),
                EntityRelationship.target_entity_id.in_(entity_ids),
                EntityRelationship.is_deleted == False
            )
            .order_by(EntityRelationship.confidence_score.desc())
            .all()
        )

        nodes = []

        for e in top_entities:
            nodes.append({
                "id": e.id,
                "name": e.name,
                "type": e.entity_type,
                "confidence": e.confidence_score
            })

        links = []

        for r in relationships:
            links.append({
                "source": r.source_entity_id,
                "target": r.target_entity_id,
                "type": r.relationship_type,
                "confidence": r.confidence_score
            })

        return {
            "nodes": nodes,
            "links": links
        }

        """
        Retrieves top entities and their strongest relationships for visualization.
        """
        # Exclude STOP_ENTITIES explicitly
        stop_entities_lower = {s.lower() for s in STOP_ENTITIES}
        all_valid_entities = Entity.query.filter(Entity.is_deleted == False).filter(~Entity.name.in_(STOP_ENTITIES)).all()
        valid_entities = [e for e in all_valid_entities if e.name.lower() not in stop_entities_lower]
        
        # Graph prioritization order
        type_priority = {
            'Company': 1,
            'Technology': 2,
            'ResearchOrganization': 3,
            'Product': 4,
            'MediaOrganization': 5,
            'AcademicInstitution': 6,
            'Organization': 7
        }
        
        # Sort by type priority, then confidence
        valid_entities.sort(key=lambda x: (type_priority.get(x.entity_type, 99), -x.confidence_score))
        top_entities = valid_entities[:limit_entities]
        
        entity_ids = [e.id for e in top_entities]
        
        if not entity_ids:
            return {"nodes": [], "links": []}
            
        # Get relationships where either source or target is in top entities
        rels = EntityRelationship.query.filter(
            (EntityRelationship.source_entity_id.in_(entity_ids)) |
            (EntityRelationship.target_entity_id.in_(entity_ids))
        ).filter_by(is_deleted=False).order_by(EntityRelationship.confidence_score.desc()).limit(50).all()
        
        # Need to ensure all nodes present in links are also in the nodes list
        extra_entity_ids = set()
        for r in rels:
            if r.source_entity_id not in entity_ids: extra_entity_ids.add(r.source_entity_id)
            if r.target_entity_id not in entity_ids: extra_entity_ids.add(r.target_entity_id)
            
        extra_entities = []
        if extra_entity_ids:
            extra_entities = Entity.query.filter(Entity.id.in_(extra_entity_ids)).filter_by(is_deleted=False).all()
            
        all_entities = top_entities + extra_entities
        
        nodes = [{"id": e.id, "name": e.name, "type": e.entity_type, "confidence": e.confidence_score} for e in all_entities]
        links = [{"source": r.source_entity_id, "target": r.target_entity_id, "type": r.relationship_type, "confidence": r.confidence_score} for r in rels]
        
        return {"nodes": nodes, "links": links}
