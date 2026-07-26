import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.product_management.models import Admin
from src.product_management.core.security import hash_password
from src.product_management.models import Base
from main import app
from src.product_management.core.database import get_db
from src.product_management.core.security import limiter

@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()

    yield session

    session.close()


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()
    
@pytest.fixture
def auth_headers(client, db_session):
    db_session.add(Admin(username="testadmin", hashed_password=hash_password("testpass123")))
    db_session.commit()

    response = client.post(
        "/auth/login",
        json={"username": "testadmin", "password": "testpass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
def reset_rate_limiter():
    limiter.reset()
    yield