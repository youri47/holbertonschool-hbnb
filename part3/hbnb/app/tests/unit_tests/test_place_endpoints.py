import unittest
from part2.hbnb.app import create_app

# Global variable to keep UUID
GLOBAL_USER_ID = None

class TestPlaceEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        global GLOBAL_USER_ID
        if GLOBAL_USER_ID is None:
            self.create_user()

    def create_user(self):
        """
        Creating a new user
        We need to create a user to be able to create a place
        """
        global GLOBAL_USER_ID
        response = self.client.post('/api/v1/users/', json={
            "first_name": "Luke",
            "last_name": "Skywalker",
            "email": "luke@starwars.com"
        })
        print("\nUser creation response:", response.json)
        self.assertEqual(response.status_code, 201)
        GLOBAL_USER_ID = response.json['id']

    def test_create_place(self):
        response = self.client.post('/api/v1/places/', json={
            "title": "Dagobah swamp",
            "description": "Yoda's home",
            "price": 1337.00,
            "latitude": 37.7749,
            "longitude": -122.4194,
            "owner": GLOBAL_USER_ID
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json)
        self.assertEqual(response.json['title'], "Dagobah swamp")
        self.assertEqual(response.json['price'], 1337.00)

    def test_create_place_empty_data(self):
        response = self.client.post('/api/v1/places/', json={})
        self.assertEqual(response.status_code, 400)

    def test_create_place_invalid_data(self):
        response = self.client.post('/api/v1/places/', json={
            "title": "Tattoine hut",
            "description": "A place with 3 suns to stay",
            "price": "100.42",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "owner": GLOBAL_USER_ID
        })
        self.assertEqual(response.status_code, 400)

    def test_get_place_not_found(self):
        response = self.client.get('/api/v1/places/non-existent-id')
        self.assertEqual(response.status_code, 404)

    def test_update_place_not_found(self):
        response = self.client.put('/api/v1/places/non-existent-id', json={
            "title": "The New Dagobah cave",
            "price": 4242.42,
            "description": "A place to face your fears"
        })
        self.assertEqual(response.status_code, 404)

    def test_get_place_by_ID(self):
        response = self.client.post('/api/v1/places/', json={
            "title": "Cloud City",
            "description": "Best cloudy place to stay in Bespin",
            "price": 1000000.0,
            "latitude": 37.7749,
            "longitude": -122.4194,
            "owner": GLOBAL_USER_ID
        })
        self.assertEqual(response.status_code, 201)
        self.assertIn('id', response.json)
        self.assertEqual(response.json['title'], "Cloud City")
        self.assertEqual(response.json['price'], 1000000.0)
        place_id = response.json['id']
        response = self.client.get(f'/api/v1/places/{place_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['title'], "Cloud City")
        self.assertEqual(response.json['price'], 1000000.0)

    def test_get_places(self):
        response = self.client.get('/api/v1/places/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        print(f"\nPlaces in memory: {response.json}")

    def test_update_place(self):
        response = self.client.get('/api/v1/places/')
        self.assertEqual(response.status_code, 200)
        first_place = response.json[0]
        place_id = first_place['id']
        before_modification = self.client.get(f'/api/v1/places/{place_id}')
        self.assertEqual(response.status_code, 200)
        print(f"\nOriginal Place: {before_modification.json}")
        response = self.client.put(f'/api/v1/places/{place_id}', json={
            "title": "Dagobah cave",
            "price": 4242.42,
            "description": "A place to face your fears"
        })
        self.assertEqual(response.status_code, 200)
        after_modification = self.client.get(f'/api/v1/places/{place_id}')
        self.assertEqual(response.status_code, 200)
        print(f"\nUpdated Place: {after_modification.json}")

    def test_update_place_empty_data(self):
        response = self.client.get('/api/v1/places/')
        self.assertEqual(response.status_code, 200)
        first_place = response.json[0]
        place_id = first_place['id']
        response = self.client.put(f'/api/v1/places/{place_id}', json={})
        self.assertEqual(response.status_code, 400)

    def test_update_place_invalid_data(self):
        response = self.client.get('/api/v1/places/')
        self.assertEqual(response.status_code, 200)
        first_place = response.json[0]
        place_id = first_place['id']
        response = self.client.put(f'/api/v1/places/{place_id}', json={
            "title": 123456,
            "price": "4242.42",
            "description": "A place to face your fears"
        })
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
