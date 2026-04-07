import pytest
from app import create_app, db
from app.models.review import Review

@pytest.fixture
def app():
    app = create_app('config.TestingConfig')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_review_creation(app):
    with app.app_context():
        review = Review(text="Great place!", rating=4)
        assert review.text == "Great place!"
        assert review.rating == 4

def test_review_empty_text(app):
    with app.app_context():
        with pytest.raises(ValueError):
            Review(text="", rating=4)

def test_review_invalid_rating(app):
    with app.app_context():
        with pytest.raises(ValueError):
            Review(text="ok", rating=7)

def test_review_rating_not_int(app):
    with app.app_context():
        with pytest.raises(TypeError):
            Review(text="ok", rating="5")