import pytest
from app.models.place import Place
from app.models.user import User

@pytest.fixture(autouse=True)
def clear_emails():
    User.emails.clear()
    yield

@pytest.fixture
def owner():
    return User(first_name="John", last_name="Doe", email="john@test.com")

def test_place_creation(owner):
    place = Place(title="Nice flat", price=100.0, latitude=48.85, longitude=2.35, owner=owner)
    assert place.title == "Nice flat"
    assert place.price == 100.0
    assert place.owner == owner

def test_place_empty_title(owner):
    with pytest.raises(ValueError):
        Place(title="", price=100.0, latitude=48.85, longitude=2.35, owner=owner)

def test_place_title_too_long(owner):
    with pytest.raises(ValueError):
        Place(title="A" * 101, price=100.0, latitude=48.85, longitude=2.35, owner=owner)

def test_place_negative_price(owner):
    with pytest.raises(ValueError):
        Place(title="Flat", price=-10.0, latitude=48.85, longitude=2.35, owner=owner)

def test_place_invalid_latitude(owner):
    with pytest.raises(ValueError):
        Place(title="Flat", price=100.0, latitude=91.0, longitude=2.35, owner=owner)

def test_place_invalid_longitude(owner):
    with pytest.raises(ValueError):
        Place(title="Flat", price=100.0, latitude=48.85, longitude=181.0, owner=owner)

def test_place_owner_not_user(owner):
    with pytest.raises(TypeError):
        Place(title="Flat", price=100.0, latitude=48.85, longitude=2.35, owner="notauser")

def test_place_to_dict(owner):
    place = Place(title="Flat", price=100.0, latitude=48.85, longitude=2.35, owner=owner)
    d = place.to_dict()
    assert d["title"] == "Flat"
    assert d["owner_id"] == owner.id