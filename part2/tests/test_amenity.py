import pytest
from app.models.amenity import Amenity

def test_amenity_creation():
    amenity = Amenity(name="WiFi")
    assert amenity.name == "WiFi"

def test_amenity_empty_name():
    with pytest.raises(ValueError):
        Amenity(name="")

def test_amenity_name_not_string():
    with pytest.raises(TypeError):
        Amenity(name=123)

def test_amenity_name_too_long():
    with pytest.raises(ValueError):
        Amenity(name="A" * 51)

def test_amenity_to_dict():
    amenity = Amenity(name="Pool")
    d = amenity.to_dict()
    assert d["name"] == "Pool"
    assert "id" in d