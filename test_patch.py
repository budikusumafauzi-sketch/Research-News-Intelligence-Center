import os
import sys

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from extensions import db
from services.strategic_service import StrategicService
from models.strategic_signal import StrategicSignal

app = create_app()

with app.app_context():
    print("Clearing old signals...")
    StrategicSignal.query.delete()
    db.session.commit()
    
    print("Executing strategic signal generation...")
    StrategicService.generate_strategic_signals()
    print("Done. Fetching generated signals...")
    
    signals = StrategicSignal.query.filter_by(is_deleted=False).all()
    print(f"Total active strategic signals: {len(signals)}")
    for s in signals:
        print(f"[{s.signal_type}] {s.title} (Confidence: {s.confidence_score})")
