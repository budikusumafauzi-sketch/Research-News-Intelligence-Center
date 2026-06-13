from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize global extensions
# This prevents circular imports by initializing extensions without the app instance,
# allowing models to import 'db' cleanly.
db = SQLAlchemy()
migrate = Migrate()
