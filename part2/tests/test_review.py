import pytest
from app.models.review import Review
from app.models.place import Place
from app.models.user import User

@pytest.fixture(autouse=True)
def clear_emails():
    User.emails.clear()
    yield

@pytest.fixture
def user():
    return User(first_name="John", last_name="Doe", email="john@test.com")

@pytest.fixture
def place(user):
    return Place(title="Nice flat", price=100.0, latitude=48.85, longitude=2.35, owner=user)

def test_review_creation(user, place):
    review = Review(text="Great place!", rating=4, place=place, user=user)
    assert review.text == "Great place!"
    assert review.rating == 4

def test_review_empty_text(user, place):
    with pytest.raises(ValueError):
        Review(text="", rating=4, place=place, user=user)

def test_review_invalid_rating(user, place):
    with pytest.raises(ValueError):
        Review(text="ok", rating=7, place=place, user=user)

def test_review_rating_not_int(user, place):
    with pytest.raises(TypeError):
        Review(text="ok", rating="5", place=place, user=user)

def test_review_invalid_place(user):
    with pytest.raises(TypeError):
        Review(text="ok", rating=4, place="notaplace", user=user)

def test_review_invalid_user(place):
    with pytest.raises(TypeError):
        Review(text="ok", rating=4, place=place, user="notauser")

def test_review_to_dict(user, place):
    review = Review(text="Great!", rating=5, place=place, user=user)
    d = review.to_dict()
    assert d["text"] == "Great!"
    assert d["place_id"] == place.id
    assert d["user_id"] == user.id