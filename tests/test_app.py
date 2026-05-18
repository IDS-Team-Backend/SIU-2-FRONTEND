import unittest

from app import app


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_page_loads(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"SIU-2 Frontend App", response.data)
        self.assertIn(b"Flask-based frontend website", response.data)


if __name__ == "__main__":
    unittest.main()
