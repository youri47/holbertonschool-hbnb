import unittest
from part2.hbnb.app import create_app

class TestAmenityEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_create_amenity(self):
        response = self.client.post('/api/v1/amenities/', json={
            "name": "Wi-Fi"
        })
        self.assertEqual(response.status_code, 201)

    def test_create_amenity_invalid_data(self):
        response = self.client.post('/api/v1/amenities/', json={})
        self.assertEqual(response.status_code, 400)

    def test_create_preexisting_amenity(self):
        response = self.client.post('/api/v1/amenities/', json={
            "name": "Wi-Fi"
        })
        self.assertEqual(response.status_code, 400)

    def test_get_amenity_by_ID(self):
        response = self.client.post('/api/v1/amenities/', json={
            "name": "Microwave"
        })
        self.assertEqual(response.status_code, 201)
        amenity_id = response.json['id']
        response = self.client.get(f'/api/v1/amenities/{amenity_id}')
        self.assertEqual(response.status_code, 200)

    def get_amenity_by_invalid_ID(self):
        response = self.client.get('/api/v1/amenities/1234567890')
        self.assertEqual(response.status_code, 404)

    def test_retrieve_amenity_list(self):
        response = self.client.get('/api/v1/amenities/')
        self.assertEqual(response.status_code, 200)
        print(f"Amenities in memory: {response.json}")

    def test_update_a_amenity(self):
        response = self.client.post('/api/v1/amenities/', json={
            "name": "pool"
        })
        self.assertEqual(response.status_code, 201)
        amenity_id = response.json["id"]
        response = self.client.put(f'/api/v1/amenities/{amenity_id}', json={
            "name": "swimming pool"
        })
        self.assertEqual(response.status_code, 200)

    def test_update_a_non_existing_amenity(self):
        response = self.client.put('/api/v1/amenities/1234567890', json={
            "name": "jacuzzi"
        })
        self.assertEqual(response.status_code, 404)

    def test_update_a_amenity_with_invalid_data(self):
        response = self.client.post('/api/v1/amenities/', json={
            "name": "dancefloor"
        })
        self.assertEqual(response.status_code, 201)
        amenity_id = response.json["id"]
        response = self.client.put(f'/api/v1/amenities/{amenity_id}', json={
            "color": "Blue",
        })
        self.assertEqual(response.status_code, 400)

    def test_amenity_name_validation_len(self):
        response = self.client.post('/api/v1/amenities/', json={
            "name": "Ultra-Premium Deluxe Executive Rooftop Infinity Pool "
            "& Spa with AI-Controlled Water Temperature System"
        })
        self.assertEqual(response.status_code, 400)

    def test_amenity_name_validation_string(self):
        response = self.client.post('/api/v1/amenities/', json={
            "name": 1234567890
        })
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
