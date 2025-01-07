import unittest
from app import app

class TestTokenOrchestrator(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_generate_key(self):
        response = self.app.post('/keys')
        self.assertEqual(response.status_code, 201)
        self.assertIn('keyId', response.json)

    def test_get_key(self):
        # Generate a key first
        self.app.post('/keys')
        response = self.app.get('/keys')
        self.assertEqual(response.status_code, 200)
        self.assertIn('keyId', response.json)

    def test_get_nonexistent_key_info(self):
        response = self.app.get('/keys/nonexistent-id')
        self.assertEqual(response.status_code, 404)

if __name__ == '__main__':
    unittest.main()
