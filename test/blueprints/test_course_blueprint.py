import re

from bs4 import BeautifulSoup
from flask import Response, session

from models.course import Course
from models.course_enrollment import CourseEnrollment, Role
from models.page import Page, VisibilitySetting
from models.user import User
from test.test_flask_app import TestFlaskApp


class TestCourseBlueprint(TestFlaskApp):
    static_page_content_for_testing = """
# Home Page

## Another heading

### Yet another heading

This is the home page.
        """

    static_page_content_with_links_for_testing = """
# Home Page

- [Office Hours](/office-hours)
- [Assignments](/assignments)
- [Chapman Course Catalog](https://catalog.chapman.edu)
"""
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

    def assert_static_page_main_content(self, response):
        soup = BeautifulSoup(response.data, "html.parser")
        soup = soup.main

        self.assertEqual(soup.h1.string.strip(), "Home Page")
        self.assertEqual(soup.h2.string.strip(), "Another heading")
        self.assertEqual(soup.h3.string.strip(), "Yet another heading")

        paragraph_tag = soup.find("p", string=re.compile("This is the home page", re.IGNORECASE))
        self.assertIsNotNone(paragraph_tag)

    def assert_static_page_content_with_links(self, course, response):
        soup = BeautifulSoup(response.data, "html.parser")
        soup = soup.main

        office_hours_link = soup.find("a", string=re.compile("Office Hours"))
        self.assertEqual(office_hours_link.attrs["href"], course.starting_url_path + "/office-hours")

        assignments_link = soup.find("a", string=re.compile("Assignments"))
        self.assertEqual(assignments_link.attrs["href"], course.starting_url_path + "/assignments")

        course_catalog_link = soup.find("a", string=re.compile("Chapman Course Catalog"))
        self.assertEqual(course_catalog_link.attrs["href"], "https://catalog.chapman.edu")

    def test_course_home_page_content_with_relative_urls(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        enrollment = CourseEnrollment(
            role=Role.STUDENT,
            user_id=user.user_id,
            course_id=course.course_id,
        )
        self.add_single_enrollment(enrollment)

        home_page_content_with_relative_links = self.static_page_content_with_links_for_testing
        home_page = Page(
            url_path_after_course_path="/",
            page_title="Home Page",
            page_visibility_setting=VisibilitySetting.LISTED,
            page_content=home_page_content_with_relative_links,
            course_id=course.course_id
        )
        self.add_single_page_and_get_id(home_page)

        self.sign_user_into_session(user)

        response = self.test_client.get(course.starting_url_path + "/")
        self.assertEqual(response.status_code, 200)
        self.assert_course_layout_content(response, course, user)

        self.assert_static_page_content_with_links(course, response)

    def test_course_home_page_content_if_not_enrolled(self):
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
        self.assertEqual(response.status_code, 404)

        soup = BeautifulSoup(response.data, "html.parser")
        matching_tag = soup.find(string="This course does not have a home page.")
        self.assertIsNotNone(matching_tag)

    def test_course_home_page_content_and_visibility_to_student(self):
        visibility_settings = list(VisibilitySetting)

        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        enrollment = CourseEnrollment(
            course_id=course.course_id,
            user_id=user.user_id,
            role=Role.STUDENT,
        )
        self.add_single_enrollment(enrollment)
        self.sign_user_into_session(user)

        for visibility_setting in visibility_settings:
            with self.subTest(visibility_setting=visibility_setting):
                page = Page(
                    page_content=self.static_page_content_for_testing,
                    page_title="Home",
                    page_visibility_setting=visibility_setting,
                    url_path_after_course_path="/",
                    course_id=course.course_id
                )
                self.add_single_page_and_get_id(page)

                response = self.test_client.get(course.starting_url_path + "/")
                if visibility_setting == VisibilitySetting.HIDDEN:
                    self.assertEqual(response.status_code, 401)
                else:
                    self.assertEqual(response.status_code, 200)
                    self.assert_static_page_main_content(response)

            delete_query = '''
            DELETE FROM page;
            '''
            cursor = self.connection.cursor()
            cursor.execute(delete_query)
            self.connection.commit()

    def test_course_home_page_content_and_visibility_to_editor(self):
        visibility_settings = list(VisibilitySetting)

        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        enrollment = CourseEnrollment(
            course_id=course.course_id,
            user_id=user.user_id,
            role=Role.ASSISTANT,
        )
        self.add_single_enrollment(enrollment)
        self.sign_user_into_session(user)

        for visibility_setting in visibility_settings:
            with self.subTest(visibility_setting=visibility_setting):
                page = Page(
                    page_content=self.static_page_content_for_testing,
                    page_title="Home",
                    page_visibility_setting=visibility_setting,
                    url_path_after_course_path="/",
                    course_id=course.course_id
                )
                self.add_single_page_and_get_id(page)

                response = self.test_client.get(course.starting_url_path + "/")
                self.assertEqual(response.status_code, 200)
                self.assert_static_page_main_content(response)

            delete_query = '''
            DELETE FROM page;
            '''
            cursor = self.connection.cursor()
            cursor.execute(delete_query)
            self.connection.commit()

    def test_course_custom_static_url_page_content_and_visibility_to_student(self):
        visibility_settings = list(VisibilitySetting)

        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        enrollment = CourseEnrollment(
            course_id=course.course_id,
            user_id=user.user_id,
            role=Role.STUDENT,
        )
        self.add_single_enrollment(enrollment)

        self.sign_user_into_session(user)

        for visibility_setting in visibility_settings:
            with self.subTest(visibility_setting=visibility_setting):
                page = Page(
                    page_content=self.static_page_content_for_testing,
                    url_path_after_course_path="/custom-page",
                    page_title="Custom Page",
                    page_visibility_setting=visibility_setting,
                    course_id=course.course_id
                )
                self.add_single_page_and_get_id(page)

                response = self.test_client.get(course.starting_url_path + page.url_path_after_course_path + "/")
                if visibility_setting == VisibilitySetting.HIDDEN:
                    self.assertEqual(response.status_code, 401)
                else:
                    self.assertEqual(response.status_code, 200)
                    self.assert_static_page_main_content(response)

            delete_query = '''
            DELETE FROM page;
            '''
            cursor = self.connection.cursor()
            cursor.execute(delete_query)
            self.connection.commit()


    def test_course_custom_static_url_page_content_and_visibility_to_editor(self):
        visibility_settings = list(VisibilitySetting)

        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        enrollment = CourseEnrollment(
            course_id=course.course_id,
            user_id=user.user_id,
            role=Role.ASSISTANT,
        )
        self.add_single_enrollment(enrollment)

        self.sign_user_into_session(user)

        for visibility_setting in visibility_settings:
            with self.subTest(visibility_setting=visibility_setting):
                page = Page(
                    page_content=self.static_page_content_for_testing,
                    url_path_after_course_path="/custom-page",
                    page_title="Custom Page",
                    page_visibility_setting=visibility_setting,
                    course_id=course.course_id
                )
                self.add_single_page_and_get_id(page)

                response = self.test_client.get(course.starting_url_path + page.url_path_after_course_path + "/")
                self.assertEqual(response.status_code, 200)
                self.assert_static_page_main_content(response)

            delete_query = '''
            DELETE FROM page;
            '''
            cursor = self.connection.cursor()
            cursor.execute(delete_query)
            self.connection.commit()

    def test_course_custom_static_url_page_content_if_course_not_exists(self):
        response = self.test_client.get("/cpsc-236-f24/custom-page/")
        self.assertEqual(response.status_code, 404)

    def test_course_custom_static_url_page_content_with_relative_urls(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        enrollment = CourseEnrollment(
            role=Role.STUDENT,
            user_id=user.user_id,
            course_id=course.course_id,
        )
        self.add_single_enrollment(enrollment)

        page_content_with_relative_links = self.static_page_content_with_links_for_testing
        page = Page(
            url_path_after_course_path="/custom-page",
            page_title="Custom Page",
            page_visibility_setting=VisibilitySetting.LISTED,
            page_content=page_content_with_relative_links,
            course_id=course.course_id
        )
        self.add_single_page_and_get_id(page)

        self.sign_user_into_session(user)

        response = self.test_client.get(course.starting_url_path + page.url_path_after_course_path + "/")
        self.assertEqual(response.status_code, 200)
        self.assert_course_layout_content(response, course, user)

        self.assert_static_page_content_with_links(course, response)
