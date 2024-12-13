import unittest

from custom_exceptions import InvalidPathException
from models.page import Page, VisibilitySetting


class TestPage(unittest.TestCase):
    # TODO write unit tests for other validation logic

    # Test page validation logic
    def test_create_page(self):
        Page(
            page_title="Test Title",
            page_content="Test Content",
            page_visibility_setting=VisibilitySetting.LISTED,
            url_path_after_course_path="/valid-path",
            course_id=1
        )

    def test_url_path_ends_with_slash(self):
        with self.assertRaises(InvalidPathException):
            Page(
                page_title="Test Title",
                page_content="Test Content",
                page_visibility_setting=VisibilitySetting.LISTED,
                url_path_after_course_path="/invalid-path/",
                course_id=1
            )

    def test_url_path_startswith_forbidden_word(self):
        words_to_check = ["/attendance", "/new", "/foo/edit/bar"]
        for word in words_to_check:
            with self.subTest(word=word):
                with self.assertRaises(InvalidPathException):
                    Page(
                        page_title="Test Title",
                        page_content="Test Content",
                        page_visibility_setting=VisibilitySetting.LISTED,
                        url_path_after_course_path=word,
                        course_id=1
                    )

