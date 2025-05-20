from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database import SessionLocal
from src.local_hub_mqtt.publisher import publish_power_consumptions
from src.local_hub_mqtt.models import PowerConsumption

def publish_historical_data(hours=24):
    db: Session = SessionLocal()
    start_time = datetime.utcnow() - timedelta(hours=hours)

    readings = db.query(PowerConsumption).filter(PowerConsumption.timestamp >= start_time).all()
    publish_power_consumptions(readings)



