import unittest
from pathlib import Path
from os import system

import mysql.connector
from testcontainers.mysql import MySqlContainer
from werkzeug.security import generate_password_hash

from config import TEST_CONTAINER_IMAGE
from db_connection_details import DBConnectionDetails
from models.course import Course
from models.course_enrollment import CourseEnrollment, Role
from models.course_term import CourseTerm
from models.page import Page
from models.user import User

TEST_ROOT_PASSWORD = "12345"

class TestWithDatabaseContainer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mysql_container = MySqlContainer(
            image=TEST_CONTAINER_IMAGE,
            root_password=TEST_ROOT_PASSWORD,
        )
        cls.mysql_container.start()

    @classmethod
    def tearDownClass(cls):
        cls.mysql_container.stop()

    def setUp(self):
        self.database_config = DBConnectionDetails(
            host=self.mysql_container.get_container_host_ip(),
            port=self.mysql_container.get_exposed_port(3306),
            user=self.mysql_container.username,
            password=self.mysql_container.password,
            database=self.mysql_container.dbname
        )
        config_vars = vars(self.database_config)

        self.connection = mysql.connector.connect(**config_vars)

        cursor = self.connection.cursor()
        cursor.execute("USE test;")
        self.connection.commit()

        project_root = Path(__file__).resolve().parent.parent
        setup_sql_schema_path = project_root / 'sql' / 'setup_schema.sql'

        # Login as root to execute CREATE TRIGGER statements
        command = f'mysql -u root -p{TEST_ROOT_PASSWORD} --host={'127.0.0.1' if self.database_config.host == 'localhost' else self.database_config.host} --port={self.database_config.port} {self.database_config.database} < "{setup_sql_schema_path}"'
        system(command)

    def tearDown(self):
        host = self.mysql_container.get_container_host_ip()
        port = self.mysql_container.get_exposed_port(3306)
        database = self.mysql_container.dbname

        project_root = Path(__file__).resolve().parent.parent
        teardown_sql_file_path = project_root / 'sql' / 'teardown_schema.sql'

        self.connection.close()

        command = f'mysql -u root -p{TEST_ROOT_PASSWORD} --host={'127.0.0.1' if host == 'localhost' else host} --port={port} {database} < "{teardown_sql_file_path}"'
        system(command)

    def add_sample_user_to_test_db(self):
        new_user = User(user_id=1,
                        full_name="Test Name",
                        email="example@example.com")

        sample_password = "C4x6Fc4YbxUsWtz.Luj*ECo*xv@xGkQXv_h.-khVXqvAkmgiZgCoBn*Kj_.C-e9@"
        hashed_password = generate_password_hash(sample_password)
        add_query = '''
        INSERT INTO user (user_id, full_name, email, hashed_password)
        VALUES (%s, %s, %s, %s)
        '''
        params = (
            new_user.user_id,
            new_user.full_name,
            new_user.email,
            hashed_password
        )
        cursor = self.connection.cursor()
        cursor.execute(add_query, params)

        select_uuid_query = '''
        SELECT user.user_uuid
        FROM user
        WHERE user.user_id = %s
        '''
        params = (new_user.user_id,)

        cursor = self.connection.cursor()
        cursor.execute(select_uuid_query, params)
        new_user.user_uuid, = cursor.fetchone()

        self.connection.commit()

        return new_user, sample_password

    def add_sample_course_term_and_course_cluster(self):
        course_terms = [
            CourseTerm(
                title="Fall 2024",
                position_from_top=1
            ),
            CourseTerm(
                title="Spring 2024",
                position_from_top=2
            ),
            CourseTerm(
                title="Interterm 2024",
                position_from_top=3
            ),
            CourseTerm(
                title="Fall 2023",
                position_from_top=4
            ),
        ]
        insert_course_term_query = '''
        INSERT INTO course_term(title, position_from_top)
        VALUES (%s, %s);
        '''
        for course_term in course_terms:
            params = (course_term.title, course_term.position_from_top)
            cursor = self.connection.cursor()
            cursor.execute(insert_course_term_query, params)

            course_term.course_term_id = cursor.lastrowid
        self.connection.commit()

        courses = [
            Course(
                title="Visual Programming",
                user_friendly_class_code="CPSC 236",
                starting_url_path="/cpsc-236-f24",
                course_term_id=course_terms[0].course_term_id,
            ),
            Course(
                title="Database Management",
                user_friendly_class_code="CPSC 408",
                starting_url_path="/cpsc-408-f24",
                course_term_id=course_terms[0].course_term_id,
            ),
            Course(
                title="Operating Systems",
                user_friendly_class_code="CPSC 380",
                starting_url_path="/cpsc-380-s24",
                course_term_id=course_terms[1].course_term_id,
            ),
        ]
        insert_course_query = '''
        INSERT INTO course(title, user_friendly_class_code, starting_url_path, course_term_id)
        VALUES (%s, %s, %s, %s);
        '''
        for course in courses:
            params = (course.title, course.user_friendly_class_code, course.starting_url_path, course.course_term_id)
            cursor = self.connection.cursor()
            cursor.execute(insert_course_query, params)

            course.course_id = cursor.lastrowid
        self.connection.commit()
        return courses, course_terms

    def add_single_enrollment(self, enrollment: CourseEnrollment):
        insert_enrollment_query = '''
        INSERT INTO enrollment(course_id, role, user_id)
        VALUES (%s, %s, %s);
        '''
        params = (enrollment.course_id, enrollment.role.value, enrollment.user_id)
        cursor = self.connection.cursor()
        cursor.execute(insert_enrollment_query, params)
        self.connection.commit()

    def add_sample_course_term_and_course_enrollment_cluster(self, user_id: int):
        courses, course_terms = self.add_sample_course_term_and_course_cluster()

        # Enroll the user in some of the courses
        course_terms_to_enroll_user_in = course_terms[:2]
        courses_to_enroll_user_in_as_student = courses[:2]
        courses_to_enroll_user_in_as_assistant = courses[2:3]
        courses_to_not_enroll_user_in = courses[3:]

        for course_to_check in courses_to_enroll_user_in_as_student:
            enrollment = CourseEnrollment(
                user_id=user_id,
                course_id=course_to_check.course_id,
                role=Role.STUDENT,
            )
            self.add_single_enrollment(enrollment)
        for course_to_check in courses_to_enroll_user_in_as_assistant:
            enrollment = CourseEnrollment(
                user_id=user_id,
                course_id=course_to_check.course_id,
                role=Role.ASSISTANT,
            )
            self.add_single_enrollment(enrollment)
        return course_terms_to_enroll_user_in, courses_to_enroll_user_in_as_assistant, courses_to_enroll_user_in_as_student, courses_to_not_enroll_user_in

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

    def clear_all_enrollments(self):
        delete_query = '''
        DELETE FROM enrollment;
        '''
        cursor = self.connection.cursor()
        cursor.execute(delete_query)
        self.connection.commit()

    def clear_all_pages(self):
        delete_query = '''
        DELETE FROM page;
        '''
        cursor = self.connection.cursor()
        cursor.execute(delete_query)
        self.connection.commit()

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

    def assert_single_page_against_matching_course_id_and_url_in_db(self, page_to_update: Page, should_check_page_id = True):
        get_page_query = '''
        SELECT page.page_id,
            page.course_id,
            page.created_by_user_id,
            page.page_content,
            page.page_title,
            page.page_visibility_setting,
            page.url_path_after_course_path
        FROM page
        WHERE page.course_id = %s
            AND page.url_path_after_course_path = %s
        '''
        params = (page_to_update.course_id, page_to_update.url_path_after_course_path)
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(get_page_query, params)
        result = cursor.fetchone()

        constructed_page = Page(**result)
        if not should_check_page_id:
            constructed_page.page_id = page_to_update.page_id

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

    def assert_single_page_does_not_exist_by_course_id_and_url(self, nonexistent_page: Page):
        get_page_query = '''
        SELECT page.page_id,
            page.course_id,
            page.created_by_user_id,
            page.page_content,
            page.page_title,
            page.page_visibility_setting,
            page.url_path_after_course_path
        FROM page
        WHERE page.course_id = %s
            AND page.url_path_after_course_path = %s
        '''
        params = (nonexistent_page.course_id, nonexistent_page.url_path_after_course_path)
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(get_page_query, params)
        result = cursor.fetchone()
        self.assertIsNone(result)

