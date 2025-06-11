from sqlalchemy import create_engine
from backend.app import DATABASE_URL
from backend.models import Base

def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print("✅ Базу даних створено або оновлено")

if __name__ == "__main__":
    init_db()
