import os
from collections.abc import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///product_management.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Provide a database session for the duration of a single request.

    Used as a FastAPI dependency via Depends(get_db). The try/finally
    ensures the session is always closed after the request completes,
    even if the route raises an exception — preventing connection leaks.

    Yields:
        Session: An active database session, closed automatically
        after the request finishes.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
