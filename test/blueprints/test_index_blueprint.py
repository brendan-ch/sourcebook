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
        new_user, sample_password = self.add_sample_user_to_test_db()

        response = self.test_client.post("/sign-in", data={
            "email": new_user.email,
            "password": sample_password,
        })

        session_cookie = response.headers.get("Set-Cookie")
        self.assertIsNotNone(session_cookie)
        self.assertIn(b"session=", session_cookie)

    def test_sign_in_with_incorrect_credentials(self):
        response = self.test_client.post("/sign-in", data={
            "email": "invalid-email@example.com",
            "password": "12345",
        })

        self.assertEqual(response.status_code, 401)
        self.assertIn(b"Incorrect email or password, please try again", response.data)

    def test_sign_in_with_missing_email(self):
        new_user, sample_password = self.add_sample_user_to_test_db()

        response = self.test_client.post("/sign-in", data={
            "password": sample_password
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Please fill out all missing fields", response.data)

    def test_sign_in_with_missing_password(self):
        new_user, sample_password = self.add_sample_user_to_test_db()

        response = self.test_client.post("/sign-in", data={
            "email": new_user.email,
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Please fill out all missing fields", response.data)
