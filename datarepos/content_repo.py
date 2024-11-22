from typing import Optional

from datarepos.repo import Repo
from models.page import Page


class ContentRepo(Repo):
    def add_new_page_and_get_id(self, page: Page) -> int:
        pass

    def update_page_by_id(self, page: Page):
        pass

    def delete_page_by_id(self, page_id: int):
        pass

    def delete_pages_with_course_id(self, course_id: int):
        pass

    def get_page_by_id_if_exists(self, page_id: int) -> Optional[Page]:
        pass

    def get_page_by_url_and_course_id_if_exists(self, course_id: int, url_path: str) -> Optional[Page]:
        pass

    def get_listed_pages_for_course_id(self, course_id: int) -> list[Page]:
        pass
