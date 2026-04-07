import pytest
from app import create_app, db
from app.models.user import User

@pytest.fixture
def app():
    app = create_app('config.TestingConfig')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(autouse=True)
def clear_emails():
    User.emails.clear()
    yield

def test_user_creation(app):
    with app.app_context():
        user = User(first_name="John", last_name="Doe", email="john@test.com", password="password123")
        assert user.first_name == "John"
        assert user.email == "john@test.com"
        assert user.is_admin is False

def test_invalid_email(app):
    with app.app_context():
        with pytest.raises(ValueError):
            User(first_name="John", last_name="Doe", email="notanemail", password="password123")

def test_hash_password(app):
    with app.app_context():
        user = User(first_name="John", last_name="Doe", email="john2@test.com", password="placeholder")
        user.hash_password("password123")
        assert user.password != "password123"

def test_verify_password(app):
    with app.app_context():
        user = User(first_name="John", last_name="Doe", email="john3@test.com", password="placeholder")
        user.hash_password("password123")
        assert user.verify_password("password123") is True
        assert user.verify_password("wrongpassword") is False