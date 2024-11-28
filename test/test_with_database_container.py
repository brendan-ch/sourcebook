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
