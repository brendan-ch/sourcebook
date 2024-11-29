import re

from bs4 import BeautifulSoup
from flask import Response, session

from models.course import Course
from models.course_enrollment import CourseEnrollment, Role
from models.page import Page, VisibilitySetting
from models.user import User
from test.test_flask_app import TestFlaskApp


class TestCourseBlueprint(TestFlaskApp):
    def assert_course_layout_content(self, response: Response, course: Course, user: User):
        # Check reused layout content for the course
        # Future work:
        # - pages that should be visible in navigation (future)
        # - pages that should be collapsed (future)

        soup = BeautifulSoup(response.data, "html.parser")

        sign_out_tag = soup.find("a", string=re.compile("sign out", re.IGNORECASE))
        self.assertEqual(sign_out_tag.attrs["href"], "/sign-out")

        view_all_classes_tag = soup.find("a", string=re.compile("view all classes", re.IGNORECASE))
        self.assertEqual(view_all_classes_tag.attrs["href"], "/")

        email_text = soup.find(string=re.compile(user.email))
        self.assertIsNotNone(email_text)

        full_name_text = soup.find(string=re.compile(user.full_name))
        self.assertIsNotNone(full_name_text)

    def test_course_home_page_content_if_enrolled(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        enrollment = CourseEnrollment(
            role=Role.STUDENT,
            user_id=user.user_id,
            course_id=course.course_id,
        )
        self.add_single_enrollment(enrollment)

        # markdown2 has comprehensive syntax testing, so we only need
        # to test basic rendering here
        home_page_content = """
# Home Page

## Another heading

### Yet another heading

This is the home page.
        """

        home_page = Page(
            url_path_after_course_path="/",
            page_title="Home Page",
            page_visibility_setting=VisibilitySetting.LISTED,
            page_content=home_page_content,
            course_id=course.course_id
        )
        self.add_single_page_and_get_id(home_page)

        self.sign_user_into_session(user)

        response = self.test_client.get(course.starting_url_path + "/")
        self.assertEqual(response.status_code, 200)
        self.assert_course_layout_content(response, course, user)

        soup = BeautifulSoup(response.data, "html.parser")

        self.assertEqual(soup.h1.string, "Home Page")
        self.assertEqual(soup.h2.string, "Another heading")
        self.assertEqual(soup.h3.string, "Yet another heading")

        paragraph_tag = soup.find("p", string="This is the home page.")
        self.assertIsNotNone(paragraph_tag)

    def test_course_home_page_content_if_not_enrolled_and_private(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        response = self.test_client.get(course.starting_url_path + "/")
        self.assertEqual(response.status_code, 401)

    def test_course_home_page_content_if_course_not_exists(self):
        response = self.test_client.get("/cpsc-236-f24/")
        self.assertEqual(response.status_code, 404)

    def test_course_home_page_content_if_course_exists_without_home_page(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        enrollment = CourseEnrollment(
            role=Role.STUDENT,
            user_id=user.user_id,
            course_id=course.course_id,
        )
        self.add_single_enrollment(enrollment)

        self.sign_user_into_session(user)

        response = self.test_client.get(course.starting_url_path + "/")
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.data, "html.parser")
        matching_tag = soup.find(string="This course does not have a home page.")
        self.assertIsNotNone(matching_tag)
