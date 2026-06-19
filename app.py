import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify

from config import config_by_name
from extensions import db, migrate

# Import scheduler
from utils.scheduler import init_scheduler

def create_app(
    config_name=None,
    run_initial_sync=False,
    run_initial_intelligence=False,
    run_initial_analytics=False,
    run_initial_strategic=False
):
    """
    Application factory pattern to create and configure the Flask app.
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configure logging first so startup tasks are properly tracked
    _configure_logging(app)

    # Important: Bind models to app context to ensure Flask-Migrate detects them
    with app.app_context():
        import models
        # Create all tables dynamically if they don't exist
        db.create_all()
        
        # Seed initial source integrations
        from services.source_service import SourceService
        SourceService.seed_initial_sources()
        
        if run_initial_sync:
            # Execute initial fetch to populate UI before the first scheduler tick
            from services.news_service import NewsService
            try:
                app.logger.info("Initial RSS synchronization started.")
                NewsService.fetch_latest_news()
                app.logger.info("Initial RSS synchronization completed.")
            except Exception as e:
                app.logger.warning(f"Initial RSS synchronization failed: {e}")

            # Execute initial research synchronization
            from services.research_service import ResearchService
            try:
                app.logger.info("Initial research synchronization started.")
                ResearchService.fetch_latest_papers()
                app.logger.info("Initial research synchronization completed.")
            except Exception as e:
                app.logger.warning(f"Initial research synchronization failed: {e}")
        else:
            app.logger.info("Skipping initial RSS synchronization.")

        if run_initial_intelligence:
            # Execute initial intelligence generation
            from services.intelligence_service import IntelligenceService
            try:
                app.logger.info("Initial intelligence generation started.")
                IntelligenceService.generate_batch_intelligence()
                app.logger.info("Initial intelligence generation completed.")
            except Exception as e:
                app.logger.warning(f"Initial intelligence generation failed: {e}")
        else:
            app.logger.info("Skipping initial intelligence generation.")

        if run_initial_analytics:
            # Execute initial analytics generation
            from services.analytics_service import AnalyticsService
            try:
                app.logger.info("Initial analytics generation started.")

                AnalyticsService.calculate_trending_topics()
                AnalyticsService.calculate_entity_momentum()
                AnalyticsService.detect_emerging_technologies()

                app.logger.info("Initial analytics generation completed.")
            except Exception as e:
                app.logger.warning(f"Initial analytics generation failed: {e}")
        else:
            app.logger.info("Skipping initial analytics generation.")

        if run_initial_strategic:
            # Execute initial strategic signals generation (Phase 8)
            from services.strategic_service import StrategicService
            try:
                app.logger.info("Initial strategic signal generation started.")
                StrategicService.generate_strategic_signals()
                app.logger.info("Initial strategic signal generation completed.")
            except Exception as e:
                app.logger.warning(f"Initial strategic signal generation failed: {e}")
        else:
            app.logger.info("Skipping initial strategic signal generation.")

    _register_error_handlers(app)
    _register_blueprints(app)
    _register_context_processors(app)

    # Start the background tasks
    init_scheduler(app)

    app.logger.info(f"RNIC Platform initialized in '{config_name}' mode.")

    return app

def _configure_logging(app):
    """Configure console and file logging with rotation."""
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # File handler with rotation (10MB per file, keeping last 10 logs)
    file_handler = RotatingFileHandler('logs/rnic.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG if app.debug else logging.INFO)

    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)

def _register_error_handlers(app):
    """Register custom error handlers for the application."""
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.warning(f"404 Not Found: {error}")
        return jsonify({"error": "Resource not found", "status_code": 404}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"500 Internal Server Error: {error}")
        return jsonify({"error": "Internal server error", "status_code": 500}), 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        app.logger.exception("Unhandled Exception")
        return jsonify({"error": "An unexpected error occurred", "status_code": 500}), 500

def _register_context_processors(app):
    """Register context processors to inject global variables into templates."""
    @app.context_processor
    def inject_unread_alerts():
        try:
            from models.alert import Alert
            count = Alert.query.filter_by(is_read=False).count()
            recent_alerts = Alert.query.filter_by(is_read=False).order_by(Alert.created_at.desc()).limit(5).all()
            return dict(unread_alerts_count=count, recent_alerts=recent_alerts)
        except Exception:
            # Failsafe if DB or table isn't ready
            return dict(unread_alerts_count=0, recent_alerts=[])

def _register_blueprints(app):
    """Register all application blueprints."""
    from routes.dashboard import dashboard_bp
    from routes.news import news_bp
    from routes.research import research_bp
    from routes.analytics import analytics_bp
    from routes.bookmarks import bookmarks_bp
    from routes.admin import admin_bp
    from routes.intelligence import intelligence_bp
    from routes.entity import entity_bp
    from routes.strategic import strategic_bp
    from routes.search import search_bp
    from routes.alerts import alerts_bp

    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(news_bp, url_prefix='/news')
    app.register_blueprint(research_bp, url_prefix='/research')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(bookmarks_bp, url_prefix='/bookmarks')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(intelligence_bp, url_prefix='/intelligence')
    app.register_blueprint(entity_bp, url_prefix='/entities')
    app.register_blueprint(strategic_bp, url_prefix='/strategic')
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(alerts_bp, url_prefix='/alerts')

if __name__ == '__main__':
    # Startup sequence
    app = create_app(
        run_initial_sync=True,
        run_initial_intelligence=True,
        run_initial_analytics=True,
        run_initial_strategic=True
    )
    app.run(host='0.0.0.0', port=5000)
