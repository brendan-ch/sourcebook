import uuid

from test.test_flask_app import TestFlaskApp

class TestIndexBlueprint(TestFlaskApp):
    def test_your_classes(self):
        user, sample_password = self.add_sample_user_to_test_db()
        (
            course_terms_to_enroll_user_in,
            courses_to_enroll_user_in_as_assistant,
            courses_to_enroll_user_in_as_student,
            courses_to_not_enroll_user_in
        ) = self.add_sample_course_term_and_course_enrollment_cluster(user.user_id)

        # Set user session to simulate login
        with self.test_client.session_transaction() as session:
            session["user_uuid"] = user.user_uuid

        response = self.test_client.get("/")
        self.assertEqual(response.status_code, 200)

        for course_term_with_courses in course_terms_to_enroll_user_in:
            self.assertIn(course_term_with_courses.title.encode(), response.data)

        for course_to_check in courses_to_enroll_user_in_as_student:
            self.assertIn(course_to_check.title.encode(), response.data)

        for course_to_check in courses_to_not_enroll_user_in:
            self.assertNotIn(course_to_check.title.encode(), response.data)

    def test_your_classes_if_no_classes(self):
        user, sample_password = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()

        with self.test_client.session_transaction() as session:
            session["user_uuid"] = user.user_uuid

        response = self.test_client.get("/")
        self.assertEqual(response.status_code, 200)

        # Verify that a message was displayed to the user
        self.assertIn(b"No courses to display", response.data)

        for course in courses:
            self.assertNotIn(course.title.encode(), response.data)
        for course_term in course_terms:
            self.assertNotIn(course_term.title.encode(), response.data)

    def test_your_classes_if_not_signed_in(self):
        response = self.test_client.get("/")
        self.assertEqual(response.status_code, 302)

    def test_sign_in_page(self):
        response = self.test_client.get("/sign-in")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Sign in", response.data)
        self.assertIn(b"<input", response.data)
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
        self.assertIn("session=", session_cookie)

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

    def test_sign_out(self):
        sample_fake_uuid = str(uuid.uuid4())
        with self.test_client.session_transaction() as session:
            session["user_uuid"] = sample_fake_uuid

        sign_out_response = self.test_client.get("/sign-out")
        self.assertEqual(sign_out_response.status_code, 302)

        with self.test_client.session_transaction() as session:
            self.assertNotIn("user_uuid", session)

    def test_sign_out_if_already_signed_out(self):
        sign_out_response = self.test_client.get("/sign-out")
        self.assertEqual(sign_out_response.status_code, 302)
