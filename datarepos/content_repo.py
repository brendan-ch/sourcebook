from typing import Optional

from custom_exceptions import AlreadyExistsException
from datarepos.repo import Repo
from models.page import Page


class ContentRepo(Repo):
    def add_new_page_and_get_id(self, page: Page) -> int:
        if page.page_id:
            raise AlreadyExistsException

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

        page_id = self.insert_single_entry_into_db_and_return_id(insert_page_query, params)
        return page_id

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
