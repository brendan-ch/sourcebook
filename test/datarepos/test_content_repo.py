import unittest

from datarepos.content_repo import ContentRepo
from models.course_enrollment import CourseEnrollment, Role
from models.page import Page, VisibilitySetting
from test.test_with_database_container import TestWithDatabaseContainer


class TestContentRepo(TestWithDatabaseContainer):
    def setUp(self):
        super().setUp()
        self.content_repo = ContentRepo(self.connection)

    def test_add_new_page_and_get_id(self):
        # For a course to exist it must be linked to a course,
        # and it *may* be linked to a user
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        sample_page_content = '''
# Home

Discover the art and science of creating immersive games! This course
offers a comprehensive foundation in game design and development, blending
creativity with technical skills.

## What You'll Learn

- Design Fundamentals: Explore game mechanics, storytelling, and player experience.
- Development Tools: Hands-on experience with industry-standard tools like Unity or Unreal Engine.
- Programming Basics: Learn essential coding for interactive gameplay.
- Collaborative Creativity: Work in teams to bring ideas to life.

Embark on your journey into the exciting world of game development today!

## Helpful Links

- [Office Hours](/office-hours)
- [Lecture Notes](/lecture-notes)
- [Assignments](/assignments)
- [Contact Me](/contact-me)

        '''
        new_page = Page(
            created_by_user_id=user.user_id,
            page_title="Home",
            page_content=sample_page_content,
            page_visibility_setting=VisibilitySetting.LISTED,
            url_path_after_course_path="/",
            course_id=course.course_id
        )

        new_page.page_id = self.content_repo.add_new_page_and_get_id(new_page)
        self.assertIsNotNone(new_page.page_id)

        # Validate some data in the database
        get_page_query = '''
        SELECT page.page_id,
            page.course_id,
            page.created_by_user_id,
            page.page_content,
            page.page_title,
            page.page_visibility_setting,
            page.url_path_after_course_path
        FROM page
        WHERE page.page_id = %s
        '''
        params = (new_page.page_id,)

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(get_page_query, params)
        result = cursor.fetchone()
        object_constructed_from_result = Page(**result)

        # With Python dataclass, the __eq__ method compares each attribute
        self.assertEqual(object_constructed_from_result, new_page)

    def test_add_new_page_with_id(self):
        pass

    def test_add_new_page_with_duplicate_start_url_and_course_id(self):
        pass

    def test_add_new_page_with_duplicate_start_url_but_diff_course_id(self):
        pass

    def test_update_page_by_id(self):
        pass

    def test_update_nonexistent_page(self):
        pass

    def test_update_new_page_with_id(self):
        pass

    def test_update_new_page_with_duplicate_start_url_and_course_id(self):
        pass

    def test_update_new_page_with_duplicate_start_url_but_diff_course_id(self):
        pass

    def test_delete_page_by_id(self):
        pass

    def test_delete_nonexistent_page(self):
        pass

    def test_delete_pages_with_course_id(self):
        pass

    def test_delete_pages_with_nonexistent_course_id(self):
        pass

    def test_get_page_by_id_if_exists(self):
        pass

    def test_get_page_by_id_if_nonexistent(self):
        pass

    def test_get_page_by_url_and_course_id_if_exists(self):
        pass

    def test_get_page_by_url_and_course_id_if_nonexistent(self):
        pass

    def test_get_listed_pages_for_course_id(self):
        pass

    def test_get_listed_pages_for_nonexistent_course_id(self):
        pass
