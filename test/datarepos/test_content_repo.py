import unittest

from sqlalchemy.dialects.mssql.information_schema import constraints

from custom_exceptions import AlreadyExistsException, NotFoundException
from datarepos.content_repo import ContentRepo
from models.course_enrollment import CourseEnrollment, Role
from models.page import Page, VisibilitySetting
from test.test_with_database_container import TestWithDatabaseContainer


class TestContentRepo(TestWithDatabaseContainer):

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

    def setUp(self):
        super().setUp()
        self.content_repo = ContentRepo(self.connection)

    def assert_single_page_against_matching_id_page_in_db(self, page_to_update):
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
        params = (page_to_update.page_id,)
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(get_page_query, params)
        result = cursor.fetchone()
        constructed_page = Page(**result)
        self.assertEqual(constructed_page, page_to_update)

    def assert_single_page_does_not_exist_by_id(self, nonexistent_page):
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
        params = (nonexistent_page.page_id,)
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(get_page_query, params)
        result = cursor.fetchone()
        self.assertIsNone(result)

    def add_single_page_and_get_id(self, page: Page) -> int:
        insert_page_query = '''
        INSERT INTO page (
            page_visibility_setting,
            page_content,
            page_title,
            url_path_after_course_path,
            course_id,
            created_by_user_id
        ) 
        VALUES (%s, %s, %s, %s, %s, %s);
        '''
        params = (
            page.page_visibility_setting.value,
            page.page_content,
            page.page_title,
            page.url_path_after_course_path,
            page.course_id,
            page.created_by_user_id
        )

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(insert_page_query, params)
        self.connection.commit()

        return cursor.lastrowid

    def test_add_new_page_and_get_id(self):
        # For a course to exist it must be linked to a course,
        # and it *may* be linked to a user
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        new_page = Page(
            created_by_user_id=user.user_id,
            page_title="Home",
            page_content=self.sample_page_content,
            page_visibility_setting=VisibilitySetting.LISTED,
            url_path_after_course_path="/",
            course_id=course.course_id
        )

        new_page.page_id = self.content_repo.add_new_page_and_get_id(new_page)
        self.assertIsNotNone(new_page.page_id)

        # Validate some data in the database
        self.assert_single_page_against_matching_id_page_in_db(new_page)

    def test_add_new_page_with_id(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        new_page = Page(
            page_id=1,
            created_by_user_id=user.user_id,
            page_title="Home",
            page_content=self.sample_page_content,
            page_visibility_setting=VisibilitySetting.LISTED,
            url_path_after_course_path="/",
            course_id=course.course_id
        )

        with self.assertRaises(AlreadyExistsException):
            self.content_repo.add_new_page_and_get_id(new_page)

        # Validate the database to ensure no changes were made
        self.assert_single_page_does_not_exist_by_id(new_page)


    def test_add_new_page_with_duplicate_start_url_and_course_id(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        new_page = Page(
            created_by_user_id=user.user_id,
            page_title="Home",
            page_content=self.sample_page_content,
            page_visibility_setting=VisibilitySetting.LISTED,
            url_path_after_course_path="/",
            course_id=course.course_id
        )

        self.add_single_page_and_get_id(new_page)

        with self.assertRaises(AlreadyExistsException):
            self.content_repo.add_new_page_and_get_id(new_page)

    def test_add_new_page_with_duplicate_start_url_but_diff_course_id(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()

        new_pages = [
            Page(
                created_by_user_id=user.user_id,
                page_title="Page 1",
                page_content=self.sample_page_content,
                page_visibility_setting=VisibilitySetting.LISTED,
                url_path_after_course_path="/",
                course_id=courses[0].course_id
            ),
            Page(
                created_by_user_id=user.user_id,
                page_title="Page 2",
                page_content=self.sample_page_content,
                page_visibility_setting=VisibilitySetting.HIDDEN,
                url_path_after_course_path="/",
                course_id=courses[1].course_id
            )
        ]

        new_pages[0].page_id = self.add_single_page_and_get_id(new_pages[0])
        new_pages[1].page_id = self.content_repo.add_new_page_and_get_id(new_pages[1])

        # Validate both pages exist
        select_pages_query = '''
        SELECT page.page_id,
            page.course_id,
            page.created_by_user_id,
            page.page_content,
            page.page_title,
            page.page_visibility_setting,
            page.url_path_after_course_path
        FROM page
        WHERE page.url_path_after_course_path = %s
        '''
        params = (new_pages[0].url_path_after_course_path,)

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(select_pages_query, params)
        results = cursor.fetchall()

        self.assertEqual(len(results), 2)
        pages_constructed_from_results = [Page(**result) for result in results]
        for constructed_page in pages_constructed_from_results:
            matching_page = [page for page in new_pages if page.page_id == constructed_page.page_id]
            self.assertEqual(constructed_page, matching_page[0])

    def test_update_page_by_id(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()

        page_to_update = Page(
            created_by_user_id=user.user_id,
            page_title="Home",
            page_content=self.sample_page_content,
            page_visibility_setting=VisibilitySetting.LISTED,
            url_path_after_course_path="/",
            course_id=courses[0].course_id
        )

        insert_query = '''
        INSERT INTO page (
            page_visibility_setting,
            page_content,
            page_title,
            url_path_after_course_path,
            course_id,
            created_by_user_id
        ) 
        VALUES (%s, %s, %s, %s, %s, %s);
        '''
        params = (
            page_to_update.page_visibility_setting.value,
            page_to_update.page_content,
            page_to_update.page_title,
            page_to_update.url_path_after_course_path,
            page_to_update.course_id,
            page_to_update.created_by_user_id
        )

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(insert_query, params)
        self.connection.commit()
        page_to_update.page_id = cursor.lastrowid

        page_to_update.course_id = courses[1].course_id
        page_to_update.page_content = "New page content"
        page_to_update.page_title = "New title"
        page_to_update.page_visibility_setting = VisibilitySetting.HIDDEN
        page_to_update.url_path_after_course_path = "/new-title"

        self.content_repo.update_page_by_id(page_to_update)
        self.assert_single_page_against_matching_id_page_in_db(page_to_update)


    def test_update_nonexistent_page(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        nonexistent_page = Page(
            created_by_user_id=user.user_id,
            page_title="Home",
            page_content=self.sample_page_content,
            page_visibility_setting=VisibilitySetting.LISTED,
            url_path_after_course_path="/",
            course_id=course.course_id,
            page_id=1
        )

        with self.assertRaises(NotFoundException):
            self.content_repo.update_page_by_id(nonexistent_page)

        # Check that nothing's been added to the database
        self.assert_single_page_does_not_exist_by_id(nonexistent_page)

    def test_update_page_with_duplicate_start_url_and_course_id(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()

        new_pages = [
            Page(
                created_by_user_id=user.user_id,
                page_title="Page 1",
                page_content=self.sample_page_content,
                page_visibility_setting=VisibilitySetting.LISTED,
                url_path_after_course_path="/page-1",
                course_id=courses[0].course_id
            ),
            Page(
                created_by_user_id=user.user_id,
                page_title="Page 2",
                page_content=self.sample_page_content,
                page_visibility_setting=VisibilitySetting.HIDDEN,
                url_path_after_course_path="/page-2",
                course_id=courses[0].course_id
            )
        ]

        for page in new_pages:
            page.page_id = self.add_single_page_and_get_id(page)

        # Try to update the second page
        new_pages[1].url_path_after_course_path = "/page-1"

        with self.assertRaises(AlreadyExistsException):
            self.content_repo.update_page_by_id(new_pages[1])

        # Validate that neither page has been changed
        new_pages[1].url_path_after_course_path = "/page-2"

        self.assert_single_page_against_matching_id_page_in_db(new_pages[0])
        self.assert_single_page_against_matching_id_page_in_db(new_pages[1])

    def test_update_page_with_duplicate_start_url_but_diff_course_id(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()

        new_pages = [
            Page(
                created_by_user_id=user.user_id,
                page_title="Page 1",
                page_content=self.sample_page_content,
                page_visibility_setting=VisibilitySetting.LISTED,
                url_path_after_course_path="/page-1",
                course_id=courses[0].course_id
            ),
            Page(
                created_by_user_id=user.user_id,
                page_title="Page 2",
                page_content=self.sample_page_content,
                page_visibility_setting=VisibilitySetting.HIDDEN,
                url_path_after_course_path="/page-2",
                course_id=courses[1].course_id
            )
        ]

        for page in new_pages:
            page.page_id = self.add_single_page_and_get_id(page)

        new_pages[1].url_path_after_course_path = "/page-1"

        self.content_repo.update_page_by_id(new_pages[1])

        self.assert_single_page_against_matching_id_page_in_db(new_pages[0])
        self.assert_single_page_against_matching_id_page_in_db(new_pages[1])

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
