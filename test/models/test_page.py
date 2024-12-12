import unittest

from models.page import Page, VisibilitySetting


class TestPage(unittest.TestCase):
    # Test page validation logic
    def test_url_path_ends_with_slash(self):
        with self.assertRaises(ValueError):
            Page(
                page_title="Test Title",
                page_content="Test Content",
                page_visibility_setting=VisibilitySetting.LISTED,
                url_path_after_course_path="/invalid-path/",
                course_id=1
            )

    def test_url_path_startswith_forbidden_word(self):
        pass

    def test_url_path_contains_forbidden_word(self):
        pass