import logging
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import func
from extensions import db
from models.analytics import AnalyticsCache
from models.intelligence import Intelligence
from models.entity import Entity
from models.entity_relationship import EntityRelationship

logger = logging.getLogger(__name__)

class AnalyticsService:
    @staticmethod
    def _upsert_cache(key: str, data: dict):
        """Helper to upsert a JSON blob into AnalyticsCache."""
        try:
            cache = AnalyticsCache.query.filter_by(key=key).first()
            if cache:
                cache.data = data
                cache.last_updated = datetime.utcnow()
            else:
                cache = AnalyticsCache(key=key, data=data)
                db.session.add(cache)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to upsert cache for {key}: {e}")

    @classmethod
    def calculate_trending_topics(cls):
        """Calculates trending topics velocity."""
        try:
            now = datetime.utcnow()
            window_24h = now - timedelta(hours=24)
            window_7d = now - timedelta(days=7)
            
            # Fetch intelligence records in the last 7 days (limit 1000 to prevent huge memory spikes)
            recent_intelligence = Intelligence.query.filter(
                Intelligence.created_at >= window_7d
            ).order_by(Intelligence.created_at.desc()).limit(1000).all()

            topics_24h = defaultdict(int)
            topics_7d = defaultdict(int)

            for record in recent_intelligence:
                if not record.topics:
                    continue
                is_24h = record.created_at >= window_24h
                for topic in record.topics:
                    topics_7d[topic] += 1
                    if is_24h:
                        topics_24h[topic] += 1

            results = []
            # Calculate velocity: trend_score = (1.0 * mentions_24h) + (2.0 * growth_rate)
            for topic, count_7d in topics_7d.items():
                count_24h = topics_24h.get(topic, 0)
                # Average per day in the older 6 days window
                older_6d_count = count_7d - count_24h
                avg_daily_older = older_6d_count / 6.0 if older_6d_count > 0 else 0.1 # Avoid div zero
                
                growth_rate = count_24h / avg_daily_older
                
                # Heuristic scoring
                score = (1.0 * count_24h) + (2.0 * growth_rate)
                
                if growth_rate > 1.5:
                    direction = "up"
                elif growth_rate < 0.5:
                    direction = "down"
                else:
                    direction = "stable"
                    
                results.append({
                    "topic": topic,
                    "score": round(score, 2),
                    "direction": direction,
                    "mentions_24h": count_24h
                })

            # Sort and keep top 10
            results.sort(key=lambda x: x['score'], reverse=True)
            top_trends = results[:10]

            cls._upsert_cache('trending_topics', {"trends": top_trends})
            logger.info("Successfully calculated trending topics velocity.")
        except Exception as e:
            logger.error(f"Error calculating trending topics: {e}")

    @classmethod
    def calculate_entity_momentum(cls):
        """Calculates momentum of entities based on recent appearances."""
        try:
            now = datetime.utcnow()
            window_7d = now - timedelta(days=7)
            
            # Entities have confidence scores. We'll find active ones from recent intelligence.
            recent_intelligence = Intelligence.query.filter(
                Intelligence.created_at >= window_7d
            ).order_by(Intelligence.created_at.desc()).limit(1000).all()

            entity_freq = defaultdict(int)
            entity_conf = defaultdict(float)

            for record in recent_intelligence:
                if not record.entities:
                    continue
                for ent in record.entities:
                    entity_freq[ent] += 1
                    entity_conf[ent] = max(entity_conf[ent], record.confidence_score)

            results = []
            for ent_name, freq in entity_freq.items():
                # We can also check relationships, but frequency in intelligence + max confidence is solid.
                momentum_score = (freq * 10) + (entity_conf[ent_name] * 0.5)
                
                # For direction, we would ideally compare against previous window.
                # Here we just use a heuristic based on frequency
                direction = "up" if freq >= 3 else "stable"
                
                results.append({
                    "entity": ent_name,
                    "momentum_score": round(momentum_score, 2),
                    "direction": direction
                })

            results.sort(key=lambda x: x['momentum_score'], reverse=True)
            top_momentum = results[:10]

            cls._upsert_cache('entity_momentum', {"momentum": top_momentum})
            logger.info("Successfully calculated entity momentum.")
        except Exception as e:
            logger.error(f"Error calculating entity momentum: {e}")

    @classmethod
    def detect_emerging_technologies(cls):
        """Identifies technologies experiencing unusual growth."""
        try:
            now = datetime.utcnow()
            window_30d = now - timedelta(days=30)
            window_7d = now - timedelta(days=7)

            # Look up Technology entities created recently
            tech_entities = Entity.query.filter(
                Entity.entity_type == 'Technology',
                Entity.created_at >= window_30d
            ).all()
            
            tech_names = {e.name for e in tech_entities}
            
            if not tech_names:
                cls._upsert_cache('emerging_tech', {"technologies": []})
                return

            recent_intelligence = Intelligence.query.filter(
                Intelligence.created_at >= window_30d
            ).order_by(Intelligence.created_at.desc()).limit(1000).all()

            tech_30d = defaultdict(int)
            tech_7d = defaultdict(int)

            for record in recent_intelligence:
                if not record.entities:
                    continue
                is_7d = record.created_at >= window_7d
                for ent in record.entities:
                    if ent in tech_names:
                        tech_30d[ent] += 1
                        if is_7d:
                            tech_7d[ent] += 1
            
            results = []
            for tech, count_30d in tech_30d.items():
                count_7d = tech_7d.get(tech, 0)
                # Historical average per 7 days = total 30d / 4.28
                hist_avg = count_30d / 4.28
                if hist_avg == 0:
                    hist_avg = 0.1
                
                ratio = count_7d / hist_avg
                if ratio > 1.2 and count_7d >= 2: # Threshold for emerging
                    results.append({
                        "technology": tech,
                        "ratio": round(ratio, 2),
                        "recent_mentions": count_7d
                    })
            
            results.sort(key=lambda x: x['ratio'], reverse=True)
            top_emerging = results[:10]

            cls._upsert_cache('emerging_tech', {"technologies": top_emerging})
            logger.info("Successfully detected emerging technologies.")
        except Exception as e:
            logger.error(f"Error detecting emerging technologies: {e}")
