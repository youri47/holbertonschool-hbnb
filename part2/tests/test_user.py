import pytest
from app.models.user import User

@pytest.fixture(autouse=True)
def clear_emails():
    User.emails.clear()
    yield

def test_user_creation():
    user = User(first_name="John", last_name="Doe", email="john.doe@example.com")
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.email == "john.doe@example.com"
    assert user.is_admin is False
    print("User creation test passed!")

def test_invalid_email():
    with pytest.raises(ValueError):
        User(first_name="John", last_name="Doe", email="notanemail")

def test_duplicate_email():
    User(first_name="John", last_name="Doe", email="same@test.com")
    with pytest.raises(ValueError):
        User(first_name="Jane", last_name="Doe", email="same@test.com")

def test_first_name_too_long():
    with pytest.raises(ValueError):
        User(first_name="J" * 51, last_name="Doe", email="test@test.com")

def test_is_admin_not_bool():
    with pytest.raises(TypeError):
        User(first_name="John", last_name="Doe", email="test2@test.com", is_admin="yes")