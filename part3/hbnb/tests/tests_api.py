import unittest
from hbnb.app import create_app

class TestHBNB(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_invalid_user_creation(self):
        """Проверка создания пользователя с неверным email"""
        response = self.client.post('/api/v1/users/', json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "invalid-email"
        })
        self.assertEqual(response.status_code, 400)