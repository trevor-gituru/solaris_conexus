from datetime import datetime, timedelta
from random import uniform, randint
from sqlalchemy.orm import Session
from db.models import PowerConsumption

def generate_sample_readings(db: Session, device_id: int, count: int = 10):
    now = datetime.utcnow()

    for i in range(count):
        timestamp = now - timedelta(minutes=5 * i)
        voltage = round(uniform(210, 240), 2)  # e.g., 220V to 240V
        current = round(uniform(0.5, 5.0), 2)   # e.g., 0.5A to 5A
        power = round(voltage * current, 2)

        sample = PowerConsumption(
            device_id=device_id,
            timestamp=timestamp,
            voltage=voltage,
            current=current,
            power=power
        )
        db.add(sample)

    db.commit()
    print(f"[Sample] {count} fake readings created for device {device_id}")

