import re

from bs4 import BeautifulSoup

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
        self.sign_user_into_session(user)

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

        self.sign_user_into_session(user)

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

    def test_sign_in_page_has_correct_ui(self):
        response = self.test_client.get("/sign-in")
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.data, "html.parser")
        inputs = soup.find_all("input")
        self.assertEqual(len(inputs), 2)

        self.assertEqual(inputs[0].attrs["name"], "email")
        self.assertIn("required", inputs[0].attrs)
        self.assertEqual(inputs[1].attrs["name"], "password")
        self.assertIn("required", inputs[1].attrs)
        self.assertEqual(inputs[1].attrs["type"], "password")

        self.assertEqual(soup.button.attrs["type"], "submit")
        self.assertIn("sign in", soup.button.string.lower())

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

        soup = BeautifulSoup(response.data, "html.parser")
        elements = soup.find_all(string=re.compile("incorrect email or password, please try again", re.IGNORECASE))
        self.assertEqual(len(elements), 1)

    def test_sign_in_with_missing_email(self):
        new_user, sample_password = self.add_sample_user_to_test_db()

        response = self.test_client.post("/sign-in", data={
            "password": sample_password
        })

        soup = BeautifulSoup(response.data, "html.parser")
        elements = soup.find_all(string=re.compile("please fill out all missing fields", re.IGNORECASE))
        self.assertEqual(len(elements), 1)

    def test_sign_in_with_missing_password(self):
        new_user, sample_password = self.add_sample_user_to_test_db()

        response = self.test_client.post("/sign-in", data={
            "email": new_user.email,
        })

        soup = BeautifulSoup(response.data, "html.parser")
        elements = soup.find_all(string=re.compile("please fill out all missing fields", re.IGNORECASE))
        self.assertEqual(len(elements), 1)

    def test_sign_out(self):
        self.sign_user_into_session()

        sign_out_response = self.test_client.get("/sign-out")
        self.assertEqual(sign_out_response.status_code, 302)

        with self.test_client.session_transaction() as session:
            self.assertNotIn("user_uuid", session)

    def test_sign_out_if_already_signed_out(self):
        sign_out_response = self.test_client.get("/sign-out")
        self.assertEqual(sign_out_response.status_code, 302)
