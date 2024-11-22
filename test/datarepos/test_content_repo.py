from typing import Optional

from custom_exceptions import AlreadyExistsException, NotFoundException
from datarepos.content_repo import ContentRepo
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

    def return_sample_page(self, course_id: int, created_by_user_id: Optional[int] = None):
        return Page(
            page_title="Page 1",
            page_content=self.sample_page_content,
            page_visibility_setting=VisibilitySetting.LISTED,
            url_path_after_course_path="/page-1",
            course_id=course_id,
            created_by_user_id=created_by_user_id,
        )

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

        new_page = self.return_sample_page(course.course_id, user.user_id)

        new_page.page_id = self.content_repo.add_new_page_and_get_id(new_page)
        self.assertIsNotNone(new_page.page_id)

        # Validate some data in the database
        self.assert_single_page_against_matching_id_page_in_db(new_page)

    def test_add_new_page_with_id(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        new_page = self.return_sample_page(course.course_id, user.user_id)
        new_page.page_id = 1

        with self.assertRaises(AlreadyExistsException):
            self.content_repo.add_new_page_and_get_id(new_page)

        # Validate the database to ensure no changes were made
        self.assert_single_page_does_not_exist_by_id(new_page)


    def test_add_new_page_with_duplicate_start_url_and_course_id(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        new_page = self.return_sample_page(course.course_id, user.user_id)

        self.add_single_page_and_get_id(new_page)

        with self.assertRaises(AlreadyExistsException):
            self.content_repo.add_new_page_and_get_id(new_page)

    def test_add_new_page_with_duplicate_start_url_but_diff_course_id(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()

        new_pages = [
            self.return_sample_page(courses[0].course_id, user.user_id),
            self.return_sample_page(courses[1].course_id, user.user_id)
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
        course = courses[0]

        page_to_update = self.return_sample_page(course.course_id, user.user_id)
        page_to_update.page_id = self.add_single_page_and_get_id(page_to_update)

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

        nonexistent_page = self.return_sample_page(course.course_id, user.user_id)
        nonexistent_page.page_id = 1

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
            self.return_sample_page(courses[0].course_id, user.user_id),
            self.return_sample_page(courses[1].course_id, user.user_id),
        ]
        new_pages[1].page_title = "Page 2"
        new_pages[1].url_path_after_course_path = "/page-2"

        for page in new_pages:
            page.page_id = self.add_single_page_and_get_id(page)

        new_pages[1].url_path_after_course_path = "/page-1"

        self.content_repo.update_page_by_id(new_pages[1])

        self.assert_single_page_against_matching_id_page_in_db(new_pages[0])
        self.assert_single_page_against_matching_id_page_in_db(new_pages[1])

    def test_delete_page_by_id(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        page_to_delete = self.return_sample_page(course.course_id, user.user_id)
        page_to_delete.page_id = self.add_single_page_and_get_id(page_to_delete)

        self.content_repo.delete_page_by_id(page_to_delete.page_id)

        self.assert_single_page_does_not_exist_by_id(page_to_delete)

    def test_delete_nonexistent_page(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        nonexistent_page_to_delete = self.return_sample_page(course.course_id, user.user_id)
        nonexistent_page_to_delete.page_id = 1

        with self.assertRaises(NotFoundException):
            self.content_repo.delete_page_by_id(nonexistent_page_to_delete.page_id)

    def test_delete_pages_with_course_id(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        pages_to_delete = [
            self.return_sample_page(course.course_id, user.user_id),
            self.return_sample_page(course.course_id, user.user_id),
        ]
        pages_to_delete[1].page_title = "Page 2"
        pages_to_delete[1].url_path_after_course_path = "/page-2"

        for page in pages_to_delete:
            page.page_id = self.add_single_page_and_get_id(page)

        self.content_repo.delete_pages_with_course_id(course.course_id)

        for page in pages_to_delete:
            self.assert_single_page_does_not_exist_by_id(page)

    def test_delete_pages_with_course_id_if_no_pages(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        # Test that no exception is thrown
        self.content_repo.delete_pages_with_course_id(course.course_id)

    def test_get_page_by_id_if_exists(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        new_page = self.return_sample_page(course.course_id, user.user_id)
        new_page.page_id = self.add_single_page_and_get_id(new_page)

        page_from_repo = self.content_repo.get_page_by_id_if_exists(new_page.page_id)
        self.assertEqual(new_page, page_from_repo)

    def test_get_page_by_id_if_nonexistent(self):
        nonexistent_page = self.content_repo.get_page_by_id_if_exists(1)
        self.assertIsNone(nonexistent_page)

    def test_get_page_by_url_and_course_id_if_exists(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        new_page = self.return_sample_page(course.course_id, user.user_id)
        new_page.page_id = self.add_single_page_and_get_id(new_page)

        page_from_repo = self.content_repo.get_page_by_url_and_course_id_if_exists(new_page.course_id, new_page.url_path_after_course_path)
        self.assertEqual(new_page, page_from_repo)

    def test_get_page_by_url_and_course_id_if_nonexistent(self):
        page_from_repo = self.content_repo.get_page_by_url_and_course_id_if_exists(1, "/")
        self.assertIsNone(page_from_repo)

    def test_get_listed_pages_for_course_id(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        new_pages = [
            self.return_sample_page(course.course_id, user.user_id),
            self.return_sample_page(course.course_id, user.user_id),
            self.return_sample_page(course.course_id, user.user_id),
        ]
        new_pages[1].page_title = "Page 2"
        new_pages[1].url_path_after_course_path = "/page-2"
        new_pages[2].page_title = "Page 3"
        new_pages[2].url_path_after_course_path = "/page-3"
        new_pages[2].page_visibility_setting = VisibilitySetting.HIDDEN

        for page in new_pages:
            page.page_id = self.add_single_page_and_get_id(page)

        pages_from_repo = self.content_repo.get_listed_pages_for_course_id(course.course_id)
        self.assertIsNotNone(pages_from_repo)
        self.assertEqual(2, len(pages_from_repo))

        for page_from_repo in pages_from_repo:
            matching_page = [page for page in new_pages if page.page_id == page_from_repo.page_id]
            self.assertEqual(page_from_repo, matching_page[0])

        non_matching_pages = [page for page in pages_from_repo if page.page_id == new_pages[2].page_id]
        self.assertEqual(len(non_matching_pages), 0)

    def test_get_listed_pages_for_nonexistent_course_id(self):
        pages_from_repo = self.content_repo.get_listed_pages_for_course_id(1)
        self.assertIsNotNone(pages_from_repo)
        self.assertEqual(len(pages_from_repo), 0)
