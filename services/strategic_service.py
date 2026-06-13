import logging
from sqlalchemy import desc
from extensions import db
from models.strategic_signal import StrategicSignal
from models.intelligence import Intelligence
from models.entity import Entity
from models.entity_relationship import EntityRelationship
from models.analytics import AnalyticsCache

logger = logging.getLogger(__name__)

ALLOWED_OPPORTUNITY_TYPES = {
    "Company",
    "Technology",
    "ResearchOrganization",
    "Product",
    "MediaOrganization"
}

STRATEGIC_STOP_ENTITIES = {
    "World Cup",
    "Football",
    "Soccer",
    "Olympics"
}

class StrategicService:
    @staticmethod
    def generate_strategic_signals():
        """
        Main orchestration method to generate all types of strategic signals.
        Processes a maximum of 1000 recent intelligence records to maintain performance.
        """
        logger.info("StrategicService: Starting generation of strategic signals.")
        
        try:
            # Generate each type of signal
            StrategicService._generate_opportunities()
            StrategicService._generate_risks()
            StrategicService._generate_emerging_trends()
            StrategicService._generate_competitive_activities()
            
            # Commit all new signals
            db.session.commit()
            logger.info("StrategicService: Successfully generated and persisted strategic signals.")
        except Exception as e:
            db.session.rollback()
            logger.error(f"StrategicService: Error generating strategic signals: {e}")

    @staticmethod
    def _generate_opportunities():
        """
        Detect opportunities:
        - Entity momentum exceeds threshold
        - Mentioned frequently across recent intelligence records
        """
        logger.info("StrategicService: Generating Opportunity signals...")
        
        # High momentum entities from AnalyticsCache
        cache = AnalyticsCache.query.filter_by(key='entity_momentum').first()
        high_momentum_entities = []
        if cache and cache.data and 'momentum' in cache.data:
            for item in cache.data['momentum']:
                if item.get('momentum_score', 0) > 30.0:
                    high_momentum_entities.append(item)

        for item in high_momentum_entities:
            entity_name = item['entity']
            momentum_score = item['momentum_score']
            
            if any(stop_entity.lower() == entity_name.lower() for stop_entity in STRATEGIC_STOP_ENTITIES):
                continue
            
            if entity_name.upper() == "GPT":
                entity_type = "Technology"
            else:
                entity_record = Entity.query.filter(Entity.name.ilike(entity_name)).first()
                entity_type = entity_record.entity_type if entity_record else None
                
            if entity_type not in ALLOWED_OPPORTUNITY_TYPES:
                continue
            
            momentum_score = min(float(momentum_score), 100.0)
            
            title = f"Opportunity: High Growth in {entity_name}"
            description = (f"The entity '{entity_name}' is showing exceptional "
                           f"momentum (Score: {momentum_score:.1f}). This indicates rapidly "
                           f"growing interest and potential opportunity in this area.")
            
            # Check if we already created a recent signal for this entity
            existing_signal = StrategicSignal.query.filter(
                StrategicSignal.title == title,
                StrategicSignal.is_deleted == False
            ).first()

            if not existing_signal:
                signal = StrategicSignal(
                    signal_type="Opportunity",
                    title=title,
                    description=description,
                    confidence_score=momentum_score
                )
                db.session.add(signal)

    @staticmethod
    def _generate_risks():
        """
        Detect risks based on keywords in recent intelligence.
        """
        logger.info("StrategicService: Generating Risk signals...")
        
        risk_keywords = [
            "breach", "attack", "lawsuit", "shutdown", "regulation", 
            "sanctions", "vulnerability", "exploit", "fraud", "bankruptcy"
        ]

        # Get recent 1000 intelligence records
        recent_intel = Intelligence.query.filter_by(is_deleted=False)\
            .order_by(desc(Intelligence.created_at)).limit(1000).all()

        risk_counts = {keyword: 0 for keyword in risk_keywords}
        
        for intel in recent_intel:
            text_to_check = (intel.summary or "").lower()
            for keyword in risk_keywords:
                if keyword in text_to_check:
                    risk_counts[keyword] += 1

        for keyword, count in risk_counts.items():
            if count > 2: # Threshold for generating a risk signal
                title = f"Risk Alert: Elevated activity around '{keyword}'"
                description = (f"Detected {count} recent intelligence records mentioning '{keyword}'. "
                               f"This could indicate an emerging risk landscape in the tracked sectors.")
                confidence = min(float(50 + (count * 5)), 100.0) # Simple confidence calculation

                # Check for existing
                existing_signal = StrategicSignal.query.filter(
                    StrategicSignal.title == title,
                    StrategicSignal.is_deleted == False
                ).first()

                if not existing_signal:
                    signal = StrategicSignal(
                        signal_type="Risk",
                        title=title,
                        description=description,
                        confidence_score=confidence
                    )
                    db.session.add(signal)

    @staticmethod
    def _generate_emerging_trends():
        """
        Detect emerging trends: converging signals from trending topics and entity momentum.
        For zero-cost, we look for overlapping 'Technology' entities with high confidence.
        """
        logger.info("StrategicService: Generating Emerging Trend signals...")

        # Detect emerging trends from AnalyticsCache
        cache = AnalyticsCache.query.filter_by(key='emerging_tech').first()
        tech_entities = []
        if cache and cache.data and 'technologies' in cache.data:
            for item in cache.data['technologies']:
                tech_entities.append(item)

        for item in tech_entities:
            tech_name = item['technology']
            ratio = item['ratio']
            
            if any(stop_entity.lower() == tech_name.lower() for stop_entity in STRATEGIC_STOP_ENTITIES):
                continue
            
            title = f"Emerging Trend: {tech_name}"
            description = (f"Sustained growth and activity detected for {tech_name}. "
                           f"This technology is emerging as a significant trend (Growth Ratio: {ratio}x).")
            confidence = min(float(50 + (ratio * 10)), 100.0)

            existing_signal = StrategicSignal.query.filter(
                StrategicSignal.title == title,
                StrategicSignal.is_deleted == False
            ).first()

            if not existing_signal:
                signal = StrategicSignal(
                    signal_type="Emerging Trend",
                    title=title,
                    description=description,
                    confidence_score=confidence
                )
                db.session.add(signal)

    @staticmethod
    def _generate_competitive_activities():
        """
        Detect competitive activity by identifying organizations that repeatedly appear together.
        """
        logger.info("StrategicService: Generating Competitive Activity signals...")

        # Find relationships between Organizations
        # We look for high confidence relationships between two Organization entities
        relationships = EntityRelationship.query.join(
            Entity, EntityRelationship.source_entity_id == Entity.id
        ).filter(
            Entity.entity_type == 'Organization',
            EntityRelationship.confidence_score > 50.0, # Threshold
            EntityRelationship.is_deleted == False
        ).order_by(desc(EntityRelationship.confidence_score)).limit(10).all()

        for rel in relationships:
            source_entity = Entity.query.get(rel.source_entity_id)
            target_entity = Entity.query.get(rel.target_entity_id)
            
            if source_entity and target_entity and target_entity.entity_type == 'Organization':
                # Order names alphabetically to avoid duplicates (A vs B is same as B vs A)
                orgs = sorted([source_entity.name, target_entity.name])
                
                if any(stop_entity.lower() in [o.lower() for o in orgs] for stop_entity in STRATEGIC_STOP_ENTITIES):
                    continue
                
                title = f"Competitive Activity: {orgs[0]} vs {orgs[1]}"
                description = (f"Frequent co-occurrences detected between {orgs[0]} and {orgs[1]}. "
                               f"This indicates potential competitive dynamics, partnerships, or joint market movements.")
                confidence = min(float(rel.confidence_score), 100.0)

                existing_signal = StrategicSignal.query.filter(
                    StrategicSignal.title == title,
                    StrategicSignal.is_deleted == False
                ).first()

                if not existing_signal:
                    signal = StrategicSignal(
                        signal_type="Competitive Activity",
                        title=title,
                        description=description,
                        confidence_score=confidence
                    )
                    db.session.add(signal)

    @staticmethod
    def get_latest_signals_by_type(signal_type, limit=5):
        """Fetch the most recent strategic signals of a specific type."""
        return StrategicSignal.query.filter_by(
            signal_type=signal_type, 
            is_deleted=False
        ).order_by(desc(StrategicSignal.created_at)).limit(limit).all()
