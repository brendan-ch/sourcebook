import re
from typing import Optional

from bs4 import BeautifulSoup
from flask import Response

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
    def generate_nonexistence_assertion_callback(self, course: Course, page_dictionary: dict, page_to_assert_against: Page):
        def callback(role: Role):
            response = self.test_client.post(course.starting_url_path + "/new/", data=page_dictionary)

            if role == Role.STUDENT:
                self.assertEqual(response.status_code, 401)
            else:
                self.assertEqual(response.status_code, 400)

            self.assert_single_page_does_not_exist_by_course_id_and_url(page_to_assert_against)

        return callback

    def generate_sample_page_dictionary(self, course: Course):
        return {
            "page_title": "Office Hours",
            "page_content": self.static_page_content_for_testing,
            "page_visibility_setting": VisibilitySetting.LISTED.value,
            "course_id": course.course_id,
            "url_path_after_course_path": "/office-hours"
        }

    def execute_assertions_callback_based_on_roles_and_enrollment(self, user: User, course: Course, callback, cleanup_callbacks = []):
        roles = list(Role)
        for role in roles:
            with self.subTest(role=role):
                enrollment = CourseEnrollment(
                    user_id=user.user_id,
                    course_id=course.course_id,
                    role=role
                )
                self.add_single_enrollment(enrollment)

                callback(role)

            self.clear_all_enrollments()

            for cleanup_callback in cleanup_callbacks:
                cleanup_callback()

    def assert_course_layout_content(
        self,response: Response,
        course: Course,
        user: User,
        role: Optional[Role] = None,
        course_pages: Optional[list[Page]] = None
    ):
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

        new_page_button = soup.find("a", string=re.compile("new page", re.IGNORECASE))
        if role and (role == Role.ASSISTANT or role == Role.PROFESSOR):
            self.assertIsNotNone(new_page_button)
            self.assertEqual(new_page_button.attrs["href"], f"{course.starting_url_path}/new")
        else:
            self.assertIsNone(new_page_button)

        if course_pages:
            # TODO complete this check when implementing nested pages
            # For each course page, check if it's listed/unlisted/hidden

            # If listed and URL is nested under listed page,
            # show as nested page
            # What this looks like in code: <ul> nested within <li>
            # Parent <li> has adjacent with the title of the root page

            # If listed and URL is nested under hidden/nonexistent page,
            # show as root page

            # If listed and URL is not nested, show as root page

            # If unlisted/hidden, not shown in sidebar

            pass

    def assert_edit_page_content(self, response):
        # TODO check if page content is pre-populated with page information
        soup = BeautifulSoup(response.data, "html.parser")

        title_input = soup.find("input", id="page_title")
        self.assertIsNotNone(title_input)
        self.assertIn("required", title_input.attrs)

        url_input = soup.find("input", id="url_path_after_course_path")
        self.assertIsNotNone(url_input)
        self.assertIn("required", url_input.attrs)

        visibility_select = soup.find("select", id="page_visibility_setting")
        self.assertIsNotNone(visibility_select)
        self.assertIn("required", visibility_select.attrs)

        options = visibility_select.find_all("option")
        self.assertEqual(len(options), 3)
        self.assertEqual(options[0].attrs["value"], "2")
        self.assertEqual(options[0].string, "Listed")
        self.assertEqual(options[1].attrs["value"], "1")
        self.assertEqual(options[1].string, "Unlisted")
        self.assertEqual(options[2].attrs["value"], "0")
        self.assertEqual(options[2].string, "Hidden")

        content_textarea = soup.find("textarea", id="page_content")
        self.assertIsNotNone(content_textarea)

        submit_button = soup.find("button", type="submit")
        self.assertIsNotNone(submit_button)

        discard_button = soup.find("a", string=re.compile("discard", re.IGNORECASE))
        self.assertIsNotNone(discard_button)

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

    def test_new_page_button_for_different_roles(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        self.sign_user_into_session(user)

        def assertion_callback(role: Role):
            response = self.test_client.get(course.starting_url_path + "/")
            self.assert_course_layout_content(response, course, user, role)

        self.execute_assertions_callback_based_on_roles_and_enrollment(
            course=course,
            user=user,
            callback=assertion_callback,
        )

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
        user, _ = self.add_sample_user_to_test_db()
        self.sign_user_into_session(user)
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
        matching_tag = soup.find(string="This page does not exist within the course.")
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
        user, _ = self.add_sample_user_to_test_db()
        self.sign_user_into_session(user)

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

    def test_course_static_page_has_edit_button_for_editors(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        paths = ["/", "/custom-path"]

        for path in paths:
            with self.subTest(path=path):
                page = Page(
                    url_path_after_course_path=path,
                    page_title="Test Page",
                    page_visibility_setting=VisibilitySetting.LISTED,
                    page_content=self.static_page_content_for_testing,
                    course_id=course.course_id
                )
                page.page_id = self.add_single_page_and_get_id(page)

                # TODO write rest of test

            self.clear_all_pages()

    def test_new_page_rendering_for_different_roles(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        self.sign_user_into_session(user)

        def assertion_callback(role: Role):
            response = self.test_client.get(course.starting_url_path + "/new/")
            if role == Role.STUDENT:
                self.assertEqual(response.status_code, 401)
            else:
                self.assert_course_layout_content(response, course, user, role)
                self.assertEqual(response.status_code, 200)
                self.assert_edit_page_content(response)

        self.execute_assertions_callback_based_on_roles_and_enrollment(
            user=user,
            course=course,
            callback=assertion_callback,
        )

    def test_new_page_submission_for_different_roles(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        # Note that values are passed as strings in form
        # even when defined as ints here
        sample_page_dictionary = self.generate_sample_page_dictionary(course)
        page_to_assert_against = Page(**sample_page_dictionary)

        self.sign_user_into_session(user)

        def assertion_callback(role: Role):
            response = self.test_client.post(course.starting_url_path + "/new/", data=sample_page_dictionary)
            if role == Role.STUDENT:
                self.assertEqual(response.status_code, 401)
                self.assert_single_page_does_not_exist_by_course_id_and_url(page_to_assert_against)
            else:
                # Should redirect to the new page
                self.assertEqual(response.status_code, 302)
                self.assert_single_page_against_matching_course_id_and_url_in_db(page_to_assert_against, should_check_page_id=False)

        self.execute_assertions_callback_based_on_roles_and_enrollment(
            user=user,
            course=course,
            callback=assertion_callback,
            cleanup_callbacks=[self.clear_all_pages]
        )

    def test_new_page_submission_with_conflicting_url(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        # Note that values are passed as strings in form
        # even when defined as ints here
        sample_page_dictionary = self.generate_sample_page_dictionary(course)
        page_to_assert_against = Page(**sample_page_dictionary)

        # Insert the page first
        page_to_assert_against.page_id = self.add_single_page_and_get_id(page_to_assert_against)

        self.sign_user_into_session(user)

        def assertion_callback(role: Role):
            response = self.test_client.post(course.starting_url_path + "/new/", data=sample_page_dictionary)
            if role == Role.STUDENT:
                self.assertEqual(response.status_code, 401)
            else:
                self.assertEqual(response.status_code, 400)

            # Page should remain unchanged
            self.assert_single_page_against_matching_id_page_in_db(page_to_assert_against)

        self.execute_assertions_callback_based_on_roles_and_enrollment(
            user=user,
            course=course,
            callback=assertion_callback,
        )

    def test_new_page_submission_with_id(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        # Note that values are passed as strings in form
        # even when defined as ints here
        sample_page_dictionary = self.generate_sample_page_dictionary(course)
        sample_page_dictionary["page_id"] = 1
        page_to_assert_against = Page(**sample_page_dictionary)

        self.sign_user_into_session(user)

        assertion_callback = self.generate_nonexistence_assertion_callback(
            course=course,
            page_to_assert_against=page_to_assert_against,
            page_dictionary=sample_page_dictionary,
        )
        self.execute_assertions_callback_based_on_roles_and_enrollment(
            user=user,
            course=course,
            callback=assertion_callback,
        )


    def test_new_page_submission_with_missing_required_data(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        sample_page_dictionary = self.generate_sample_page_dictionary(course)
        page_to_assert_against = Page(**sample_page_dictionary)

        self.sign_user_into_session(user)

        required_data_types = ["page_title", "course_id", "url_path_after_course_path", "page_visibility_setting"]
        for required_data_type in required_data_types:
            with self.subTest(required_data_type=required_data_type):
                sample_page_dictionary[required_data_type] = None

                assertion_callback = self.generate_nonexistence_assertion_callback(
                    course=course,
                    page_to_assert_against=page_to_assert_against,
                    page_dictionary=sample_page_dictionary,
                )
                self.execute_assertions_callback_based_on_roles_and_enrollment(
                    user=user,
                    course=course,
                    callback=assertion_callback,
                )

    def test_edit_page_rendering_for_different_roles(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        self.sign_user_into_session(user)

        sample_page_dictionary = self.generate_sample_page_dictionary(course)
        existing_page = Page(**sample_page_dictionary)
        existing_page.page_id = self.add_single_page_and_get_id(existing_page)

        def assertion_callback(role: Role):
            response = self.test_client.get(course.starting_url_path + existing_page.url_path_after_course_path + "/edit/")
            if role == Role.STUDENT:
                self.assertEqual(response.status_code, 401)
            else:
                self.assert_course_layout_content(response, course, user, role)
                self.assertEqual(response.status_code, 200)
                self.assert_edit_page_content(response)

        self.execute_assertions_callback_based_on_roles_and_enrollment(
            user=user,
            course=course,
            callback=assertion_callback,
        )

    def test_edit_page_for_different_roles_if_page_does_not_exist(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        self.sign_user_into_session(user)

        sample_page_dictionary = self.generate_sample_page_dictionary(course)
        nonexistent_page = Page(**sample_page_dictionary)

        def assertion_callback(role: Role):
            # Previously returned 404 even for students, but would be more
            # consistent with other tests to check for 401
            response = self.test_client.get(course.starting_url_path + nonexistent_page.url_path_after_course_path + "/edit/")

            if role == Role.STUDENT:
                self.assertEqual(response.status_code, 401)
            else:
                self.assertEqual(response.status_code, 404)

        self.execute_assertions_callback_based_on_roles_and_enrollment(
            user=user,
            course=course,
            callback=assertion_callback,
        )

    def test_edit_page_submission_for_different_roles(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        self.sign_user_into_session(user)

        def assertion_callback(role: Role):
            # Insert the page every time, and call clear_all_pages when done
            sample_page_dictionary = self.generate_sample_page_dictionary(course)
            existing_page = Page(**sample_page_dictionary)

            existing_page.page_id = sample_page_dictionary["page_id"] = self.add_single_page_and_get_id(existing_page)
            sample_page_dictionary["page_title"] = "Updated Page Title"
            sample_page_dictionary["page_content"] = "# Updated Page Content"
            sample_page_dictionary["page_visibility_setting"] = VisibilitySetting.HIDDEN.value
            sample_page_dictionary["url_path_after_course_path"] = "/updated-page"
            expected_matching_page = Page(**sample_page_dictionary)

            result = self.test_client.post(course.starting_url_path + existing_page.url_path_after_course_path + "/edit/", data=sample_page_dictionary)
            if role == Role.STUDENT:
                self.assertEqual(result.status_code, 401)
            else:
                # Should redirect to the updated page
                self.assertEqual(result.status_code, 302)
                self.assert_single_page_against_matching_id_page_in_db(expected_matching_page)

        self.execute_assertions_callback_based_on_roles_and_enrollment(
            user=user,
            course=course,
            callback=assertion_callback,
            cleanup_callbacks=[self.clear_all_pages]
        )

    def test_edit_page_submission_with_conflicting_url(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        self.sign_user_into_session(user)

        def assertion_callback(role: Role):
            starting_page_dictionary = self.generate_sample_page_dictionary(course)
            page_to_not_edit = Page(**starting_page_dictionary)
            page_to_not_edit.page_id = self.add_single_page_and_get_id(page_to_not_edit)

            page_to_attempt_to_edit = Page(**starting_page_dictionary)
            page_to_attempt_to_edit.url_path_after_course_path += "/subpath"
            page_to_attempt_to_edit.page_id = self.add_single_page_and_get_id(page_to_attempt_to_edit)

            edit_page_dictionary = starting_page_dictionary.copy()
            edit_page_dictionary["page_id"] = page_to_attempt_to_edit.page_id
            edit_page_dictionary["url_path_after_course_path"] = page_to_not_edit.url_path_after_course_path

            result = self.test_client.post(course.starting_url_path + page_to_attempt_to_edit.url_path_after_course_path + "/edit/", data=edit_page_dictionary)
            if role == Role.STUDENT:
                self.assertEqual(result.status_code, 401)
            else:
                # The edit should fail
                self.assertEqual(result.status_code, 400)
                self.assert_single_page_against_matching_id_page_in_db(page_to_attempt_to_edit)

        self.execute_assertions_callback_based_on_roles_and_enrollment(
            user=user,
            course=course,
            callback=assertion_callback,
            cleanup_callbacks=[self.clear_all_pages]
        )

    def test_edit_page_submission_with_missing_required_data(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        self.sign_user_into_session(user)

        required_data_types = ["page_title", "course_id", "url_path_after_course_path", "page_visibility_setting", "page_id"]
        for required_data_type in required_data_types:
            with self.subTest(required_data_type=required_data_type):
                sample_page_dictionary = self.generate_sample_page_dictionary(course)
                sample_page = Page(**sample_page_dictionary)
                sample_page.page_id = self.add_single_page_and_get_id(sample_page)

                sample_page_dictionary[required_data_type] = None

                def assertion_callback(role: Role):
                    result = self.test_client.post(course.starting_url_path + sample_page.url_path_after_course_path + "/edit/", data=sample_page_dictionary)
                    if role == Role.STUDENT:
                        self.assertEqual(result.status_code, 401)
                    else:
                        self.assertEqual(result.status_code, 400)
                        self.assert_single_page_against_matching_id_page_in_db(sample_page)

                self.execute_assertions_callback_based_on_roles_and_enrollment(
                    user=user,
                    course=course,
                    callback=assertion_callback,
                )

            self.clear_all_pages()

    def test_delete_page_with_different_paths_and_roles(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]
        paths = ["/", "/custom-path"]

        self.sign_user_into_session(user)

        for path in paths:
            with self.subTest(path=path):
                def assertion_callback(role: Role):
                    page_dictionary = self.generate_sample_page_dictionary(course)
                    page_to_be_deleted = Page(**page_dictionary)
                    page_to_be_deleted.url_path_after_course_path = path
                    page_to_be_deleted.page_id = self.add_single_page_and_get_id(page_to_be_deleted)

                    full_request_path = course.starting_url_path + page_to_be_deleted.url_path_after_course_path
                    if not full_request_path.endswith("/"):
                        full_request_path += "/"
                    full_request_path += "delete/"

                    result = self.test_client.post(full_request_path)

                    if role == Role.STUDENT:
                        self.assertEqual(result.status_code, 401)
                    else:
                        # Redirect to the home page
                        self.assertEqual(result.status_code, 302)
                        self.assert_single_page_does_not_exist_by_id(page_to_be_deleted)

                self.execute_assertions_callback_based_on_roles_and_enrollment(
                    user=user,
                    course=course,
                    callback=assertion_callback,
                    cleanup_callbacks=[self.clear_all_pages]
                )

    def test_delete_nonexistent_page_with_different_paths_and_roles(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]
        paths = ["/", "/custom-path"]

        self.sign_user_into_session(user)

        for path in paths:
            with self.subTest(path=path):
                def assertion_callback(role: Role):
                    full_request_path = course.starting_url_path + path
                    if not full_request_path.endswith("/"):
                        full_request_path += "/"
                    full_request_path += "delete/"

                    result = self.test_client.post(full_request_path)
                    if role == Role.STUDENT:
                        self.assertEqual(result.status_code, 401)
                    else:
                        self.assertEqual(result.status_code, 404)

                self.execute_assertions_callback_based_on_roles_and_enrollment(
                    user=user,
                    course=course,
                    callback=assertion_callback,
                )
