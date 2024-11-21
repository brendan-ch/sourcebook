from flask import Response

from models.course import Course
from test.test_flask_app import TestFlaskApp


class TestCourseBlueprint(TestFlaskApp):
    def assert_course_layout_content(self, response: Response, course: Course):
        # Check reused layout content for the course
        # Includes:
        # - all classes
        # - name and email
        # - sign out
        # - pages that should be visible in navigation (future)
        # - pages that should be collapsed (future)

        # TODO assert layout content (sidebar content)
        pass

    def test_course_home_page_content_if_enrolled(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, course_terms = self.add_sample_course_term_and_course_cluster()

        # TODO enroll the user

        response = self.test_client.get(courses[0].starting_url_path)
        self.assert_course_layout_content(response, courses[0])

        # TODO assert home page content

