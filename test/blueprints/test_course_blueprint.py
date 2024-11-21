from flask import Response

from models.course import Course
from models.course_enrollment import CourseEnrollment, Role
from models.user import User
from test.test_flask_app import TestFlaskApp


class TestCourseBlueprint(TestFlaskApp):
    def assert_course_layout_content(self, response: Response, course: Course, user: User):
        # Check reused layout content for the course
        # Includes:
        # - all classes
        # - name and email
        # - sign out
        # - pages that should be visible in navigation (future)
        # - pages that should be collapsed (future)

        # TODO use BeautifulSoup for testing

        self.assertIn(b"Sign out", response.data)
        self.assertIn(b"View all classes", response.data)
        self.assertIn(user.email.encode(), response.data)
        self.assertIn(user.full_name.encode(), response.data)
        pass

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

        response = self.test_client.get(course.starting_url_path + "/")
        self.assertEqual(response.status_code, 200)
        self.assert_course_layout_content(response, course, user)

        # TODO assert home page content

    def test_course_home_page_content_if_not_enrolled_and_private(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        response = self.test_client.get(course.starting_url_path + "/")
        self.assertEqual(response.status_code, 401)

        # TODO assert 401 page content
