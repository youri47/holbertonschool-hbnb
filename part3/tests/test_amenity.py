import pytest
from app import create_app, db
from app.models.amenity import Amenity

@pytest.fixture
def app():
    app = create_app('config.TestingConfig')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_amenity_creation(app):
    with app.app_context():
        amenity = Amenity(name="WiFi")
        assert amenity.name == "WiFi"

def test_amenity_empty_name(app):
    with app.app_context():
        with pytest.raises(ValueError):
            Amenity(name="")

def test_amenity_name_not_string(app):
    with app.app_context():
        with pytest.raises(TypeError):
            Amenity(name=123)

def test_amenity_name_too_long(app):
    with app.app_context():
        with pytest.raises(ValueError):
            Amenity(name="A" * 51)