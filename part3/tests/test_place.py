import pytest
from app import create_app, db
from app.models.user import User
from app.models.place import Place

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

def test_place_creation(app):
    with app.app_context():
        place = Place(title="Nice flat", price=100.0, latitude=48.85, longitude=2.35)
        assert place.title == "Nice flat"
        assert place.price == 100.0

def test_place_empty_title(app):
    with app.app_context():
        with pytest.raises(ValueError):
            Place(title="", price=100.0, latitude=48.85, longitude=2.35)

def test_place_negative_price(app):
    with app.app_context():
        with pytest.raises(ValueError):
            Place(title="Flat", price=-10.0, latitude=48.85, longitude=2.35)

def test_place_invalid_latitude(app):
    with app.app_context():
        with pytest.raises(ValueError):
            Place(title="Flat", price=100.0, latitude=91.0, longitude=2.35)

def test_place_invalid_longitude(app):
    with app.app_context():
        with pytest.raises(ValueError):
            Place(title="Flat", price=100.0, latitude=48.85, longitude=181.0)