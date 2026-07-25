from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


protocol = "sqlite"
db_name = "product_management.db"

DATABASE_URL = f"{protocol}:///{db_name}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()