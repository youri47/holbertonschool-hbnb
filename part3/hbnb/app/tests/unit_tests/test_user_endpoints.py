import unittest
from part2.hbnb.app import create_app

class TestUserEndpoints(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_create_user(self):
        response = self.client.post('/api/v1/users/', json={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com"
        })
        self.assertEqual(response.status_code, 201)

    def test_create_user_invalid_data(self):
        response = self.client.post('/api/v1/users/', json={})
        self.assertEqual(response.status_code, 400)

    def test_create_user_preexisting_email(self):
        response = self.client.post('/api/v1/users/', json={
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com"
        })
        self.assertEqual(response.status_code, 400)

    def test_get_user_by_ID(self):
        response = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com"
        })
        self.assertEqual(response.status_code, 201)
        user_id = response.json['id']
        response = self.client.get(f'/api/v1/users/{user_id}')
        self.assertEqual(response.status_code, 200)

    def test_get_user_by_invalid_ID(self):
        response = self.client.get('/api/v1/users/1234567890')
        self.assertEqual(response.status_code, 404)

    def test_retrieve_user_list(self):
        response = self.client.get('/api/v1/users/')
        self.assertEqual(response.status_code, 200)
        print(f"Users in memory: {response.json}")

    def test_update_a_user(self):
        response = self.client.post('/api/v1/users/', json={
            "first_name": "Anakin",
            "last_name": "Skywalker",
            "email": "anakin.skywalker@starwars.com"
        })
        self.assertEqual(response.status_code, 201)
        user_id = response.json["id"]
        response = self.client.put(f'/api/v1/users/{user_id}', json={
            "first_name": "Darth",
            "last_name": "Vader",
            "email": "darth.vader@starwars.com"
        })
        self.assertEqual(response.status_code, 200)

    def test_update_a_non_existing_user(self):
        response = self.client.put('/api/v1/users/1234567890', json={
            "first_name": "Gial",
            "last_name": "Ackbar",
            "email": "its_a_trap@starwars.com"
        })
        self.assertEqual(response.status_code, 404)

    def test_update_a_user_with_invalid_data(self):
        create_user = self.client.post('/api/v1/users/', json={
            "first_name": "Anakin",
            "last_name": "Skywalker",
            "email": "anakin.skywalker@starwars.com"
        })
        self.assertEqual(create_user.status_code, 201)
        user_id = create_user.json["id"]
        response = self.client.put(f'/api/v1/users/{user_id}', json={
            "color": "Blue",
        })
        self.assertEqual(response.status_code, 400)

    def test_user_first_name_validation_len(self):
        response = self.client.post('/api/v1/users/', json={
            "first_name": "Orn Free Taa the Twi'lek Senator of "
                          "Ryloth and Coruscant",
            "last_name": "Doe",
            "email": "email@example.com"
        })
        self.assertEqual(response.status_code, 400)

    def test_user_last_name_validation_len(self):
        response = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Orn Free Taa the Twi'lek Senator of "
                         "Ryloth and Coruscant",
            "email": "email@example.com"
        })
        self.assertEqual(response.status_code, 400)

    def test_user_email_validation(self):
        response = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "1234567890"
        })
        self.assertEqual(response.status_code, 400)

    def test_user_first_name_validation_string(self):
        response = self.client.post('/api/v1/users/', json={
            "first_name": 1234567890,
            "last_name": "Doe",
            "email": "email@example.com"
        })
        self.assertEqual(response.status_code, 400)

    def test_user_last_name_validation_string(self):
        response = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": 1234567890,
            "email": "email@example.com"
        })
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
