from flask_repository_getters import get_user_repository
from models.user import User
from test.test_flask_app import TestFlaskApp

class TestIndexBlueprint(TestFlaskApp):
    def test_all_classes(self):
        response = self.test_client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_sign_in_page(self):
        response = self.test_client.get("/sign-in")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sign in", response.data)
        self.assertIn(b"<index", response.data)
        self.assertIn(b"<button", response.data)

        # TODO install and use BeautifulSoup for UI testing

    def test_sign_in_with_correct_credentials(self):
        # Set up a user in the database
        new_user = User(
            email="example@example.com",
            full_name="Test Name"
        )

        sample_password = "f211205aea2d273d48c9a8d26c2346f9d2ec878b50f3e262b2bd86bb3f9e6cf2"

        with self.app.app_context():
            user_repository = get_user_repository()
            new_user.user_id = user_repository.add_new_user_and_get_id(new_user, sample_password)

        response = self.test_client.post("/sign-in", data={
            "email": new_user.email,
            "password": sample_password,
        })

        session_cookie = response.headers.get("Set-Cookie")
        self.assertIsNotNone(session_cookie)
        self.assertIn("session=", session_cookie)

    def test_sign_in_with_incorrect_credentials(self):
        response = self.test_client.post("/sign-in", data={
            "email": "invalid-email@example.com",
            "password": "12345",
        })

        self.assertEqual(response.status_code, 401)
        self.assertIn("Incorrect email or password, please try again", response.data)

    def test_sign_in_with_missing_field(self):
        pass
