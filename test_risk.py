from app import create_app
from models.intelligence import Intelligence
from extensions import db

app = create_app()

with app.app_context():

    risk_intel = Intelligence(
        summary="""
Critical cybersecurity breach affected Microsoft's cloud infrastructure
following a coordinated attack involving ransomware deployment.
""",
        content_type="news",
        content_id=1,
        topics=["Cybersecurity", "Microsoft", "Ransomware"],
        entities=["Microsoft"],
        confidence_score=95.0,
        provider="Phase8 Verification"
    )

    db.session.add(risk_intel)
    db.session.commit()

    print("Risk intelligence inserted.")