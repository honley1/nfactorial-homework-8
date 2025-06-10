import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models import User, Task

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "message": "Task Manager API is running"}

def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Task Manager" in response.text

def test_login_page():
    response = client.get("/login")
    assert response.status_code == 200
    assert "Welcome Back" in response.text

def test_register_page():
    response = client.get("/register")
    assert response.status_code == 200
    assert "Create Account" in response.text

def test_user_registration(setup_database):
    response = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"

def test_user_login(setup_database):
    # First register a user
    client.post("/api/auth/register", json={
        "username": "logintest",
        "email": "logintest@example.com",
        "password": "testpassword"
    })
    
    # Then try to login
    response = client.post("/api/auth/login", data={
        "username": "logintest",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_protected_route_without_token():
    response = client.get("/api/auth/me")
    assert response.status_code == 403

def test_create_task_without_auth():
    response = client.post("/api/tasks/create_task", json={
        "title": "Test Task",
        "description": "Test Description"
    })
    assert response.status_code == 403 