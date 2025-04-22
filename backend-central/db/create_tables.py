from db.database import engine, Base
from db.models import User

# Create tables
Base.metadata.create_all(bind=engine)