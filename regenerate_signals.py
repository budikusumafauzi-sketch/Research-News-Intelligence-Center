from app import create_app
from services.strategic_service import StrategicService

app = create_app()

with app.app_context():
    StrategicService.generate_strategic_signals()
    print("Strategic signals regenerated.")