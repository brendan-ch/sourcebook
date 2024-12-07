from typing import Optional

from mysql.connector import IntegrityError

from custom_exceptions import AlreadyExistsException
from datarepos.repo import Repo
from models.page import Page, VisibilitySetting
from models.page_navigation_link import PageNavigationLink


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
        update_query = '''
        UPDATE page
        SET
            page.page_visibility_setting = %s,
            page.url_path_after_course_path = %s,
            page.course_id = %s,
            page.created_by_user_id = %s,
            page.page_content = %s,
            page.page_title = %s
        WHERE page.page_id = %s;
        '''
        params = (
            page.page_visibility_setting.value,
            page.url_path_after_course_path,
            page.course_id,
            page.created_by_user_id,
            page.page_content,
            page.page_title,
            page.page_id,
        )

        self.execute_dml_query_and_check_rowcount_greater_than_0(update_query, params)

    def delete_page_by_id(self, page_id: int):
        delete_query = '''
        DELETE FROM page
        WHERE page.page_id = %s;
        '''
        params = (page_id,)

        self.execute_dml_query_and_check_rowcount_greater_than_0(delete_query, params)

    def delete_pages_with_course_id(self, course_id: int):
        delete_from_course_query = '''
        DELETE FROM page
        WHERE page.course_id = %s
        '''
        params = (course_id,)

        cursor = self.connection.cursor()
        try:
            cursor.execute(delete_from_course_query, params)
        except IntegrityError as e:
            raise e

        self.connection.commit()

    def get_page_by_id_if_exists(self, page_id: int) -> Optional[Page]:
        get_page_query = '''
        SELECT
            page.page_title,
            page.page_content,
            page.created_by_user_id,
            page.course_id,
            page.url_path_after_course_path,
            page.page_visibility_setting,
            page.page_id
        FROM page
        WHERE page.page_id = %s
        '''
        params = (page_id,)

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(get_page_query, params)
        result = cursor.fetchone()

        if not result:
            return None

        return Page(**result)

    def get_page_by_url_and_course_id_if_exists(self, course_id: int, url_path: str) -> Optional[Page]:
        get_page_query = '''
        SELECT
            page.page_title,
            page.page_content,
            page.created_by_user_id,
            page.course_id,
            page.url_path_after_course_path,
            page.page_visibility_setting,
            page.page_id
        FROM page
        WHERE page.course_id = %s AND page.url_path_after_course_path = %s
        '''
        params = (course_id, url_path)

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(get_page_query, params)
        result = cursor.fetchone()

        if not result:
            return None

        return Page(**result)

    def get_listed_pages_for_course_id(self, course_id: int) -> list[Page]:
        get_pages_query = '''
        SELECT
            page.page_title,
            page.page_content,
            page.created_by_user_id,
            page.course_id,
            page.url_path_after_course_path,
            page.page_visibility_setting,
            page.page_id
        FROM page
        WHERE page.course_id = %s AND page.page_visibility_setting = %s
        '''
        params = (course_id, VisibilitySetting.LISTED.value)

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(get_pages_query, params)
        results = cursor.fetchall()

        return [Page(**result) for result in results]

    def generate_page_navigation_link_tree_for_course_id(self, course_id: int) -> list[PageNavigationLink]:
        pass
