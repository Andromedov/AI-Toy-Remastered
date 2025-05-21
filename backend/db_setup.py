from sqlalchemy import create_engine
from backend.models import Base

# Path to SQLite file
DATABASE_URL = "sqlite:///users.db"

def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("✅ Базу даних створено або оновлено")

if __name__ == "__main__":
    init_db()
