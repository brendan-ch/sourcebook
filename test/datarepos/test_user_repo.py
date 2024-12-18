import uuid

from datarepos.user_repo import UserRepo
from custom_exceptions import AlreadyExistsException, NotFoundException, DependencyException
from models.course_enrollment import CourseEnrollment, Role
from models.file import File
from models.page import Page, VisibilitySetting
from test.test_with_database_container import TestWithDatabaseContainer
from werkzeug.security import check_password_hash

from models.user import User

class TestUserRepo(TestWithDatabaseContainer):
    def setUp(self):
        super().setUp()
        self.user_repo = UserRepo(self.connection)

    def test_get_user_id_if_credentials_match(self):
        new_user, sample_password = self.add_sample_user_to_test_db()

        user_id_to_validate = self.user_repo.get_user_id_if_credentials_match(new_user.email, sample_password)
        self.assertEqual(user_id_to_validate, new_user.user_id)


    def test_get_user_id_if_email_not_match(self):
        _, sample_password = self.add_sample_user_to_test_db()

        nonexistent_email = "example2@example.com"

        user_id_to_validate = self.user_repo.get_user_id_if_credentials_match(nonexistent_email, sample_password)
        self.assertEqual(user_id_to_validate, None)

    def test_get_user_id_if_password_not_match(self):
        new_user, _ = self.add_sample_user_to_test_db()

        incorrect_password = "12345"

        user_id_to_validate = self.user_repo.get_user_id_if_credentials_match(new_user.email, incorrect_password)
        self.assertEqual(user_id_to_validate, None)


    def test_get_user_from_id_if_exists(self):
        new_user, _ = self.add_sample_user_to_test_db()

        user_to_validate = self.user_repo.get_user_from_id_if_exists(new_user.user_id)
        self.assertEqual(user_to_validate, new_user)

    def test_get_user_from_id_if_not_exists(self):
        nonexistent_user_id = 1

        user_to_validate = self.user_repo.get_user_from_id_if_exists(nonexistent_user_id)
        self.assertIsNone(user_to_validate)

    def test_get_user_from_uuid_if_exists(self):
        new_user, _ = self.add_sample_user_to_test_db()
        user_to_validate = self.user_repo.get_user_from_uuid_if_exists(new_user.user_uuid)
        self.assertEqual(user_to_validate, new_user)

    def test_get_user_from_uuid_if_not_exists(self):
        nonexistent_uuid = str(uuid.uuid4())
        user_to_validate = self.user_repo.get_user_from_uuid_if_exists(nonexistent_uuid)
        self.assertIsNone(user_to_validate)

    def test_add_new_user_and_get_id(self):
        new_user = User(
            full_name="Test Name",
            email="example@example.com"
        )
        sample_password = "C4x6Fc4YbxUsWtz.Luj*ECo*xv@xGkQXv_h.-khVXqvAkmgiZgCoBn*Kj_.C-e9@"

        new_user.user_id = self.user_repo.add_new_user_and_get_id(new_user, sample_password)

        # Validate against the database
        get_user_query = '''
        SELECT user_id, full_name, email, hashed_password
        FROM user
        WHERE user_id = %s
            AND full_name = %s
            AND email = %s
        '''
        params = (new_user.user_id, new_user.full_name, new_user.email)

        cursor = self.connection.cursor()
        cursor.execute(get_user_query, params)

        cursor_result = cursor.fetchone()
        self.assertNotEqual(cursor_result, None)

        user_id, full_name, email, hashed_password = cursor_result
        self.assertEqual(user_id, new_user.user_id)
        self.assertEqual(full_name, new_user.full_name)
        self.assertEqual(email, new_user.email)
        self.assertTrue(check_password_hash(hashed_password, sample_password))

    def test_add_new_user_with_id(self):
        new_user = User(
            user_id=1,
            email="example@example.com",
            full_name="Test Name",
        )

        with self.assertRaises(AlreadyExistsException):
            self.user_repo.add_new_user_and_get_id(new_user, "Test")

        # Check side effects
        get_user_query = '''
        SELECT user_id, full_name, email, hashed_password
        FROM user
        WHERE user_id = %s
        '''
        params = (new_user.user_id,)

        cursor = self.connection.cursor()
        cursor.execute(get_user_query, params)

        cursor_result = cursor.fetchone()
        self.assertEqual(cursor_result, None)

    def test_add_new_user_with_duplicate_email(self):
        new_user, sample_password = self.add_sample_user_to_test_db()

        # Try to insert with a blank user ID but duplicate email
        new_user_original_user_id = new_user.user_id
        new_user.user_id = None

        with self.assertRaises(AlreadyExistsException):
            self.user_repo.add_new_user_and_get_id(new_user, "Test")

        # Check side effects
        get_user_query = '''
        SELECT user_id, full_name, email, hashed_password
        FROM user
        WHERE email = %s
        '''
        params = (new_user.email,)

        cursor = self.connection.cursor()
        cursor.execute(get_user_query, params)

        cursor_results = cursor.fetchall()
        self.assertEqual(len(cursor_results), 1)

        user_id, full_name, email, hashed_password = cursor_results[0]
        self.assertEqual(user_id, new_user_original_user_id)
        self.assertEqual(full_name, new_user.full_name)
        self.assertEqual(email, new_user.email)

    def test_delete_user_by_id(self):
        new_user, _ = self.add_sample_user_to_test_db()
        self.user_repo.delete_user_by_id(new_user.user_id)

        get_user_query = '''
        SELECT user_id
        FROM user
        WHERE user_id = %s
        '''
        params = (new_user.user_id,)

        cursor = self.connection.cursor()
        cursor.execute(get_user_query, params)
        cursor_result = cursor.fetchone()
        self.assertIsNone(cursor_result)


    def test_delete_nonexistent_user_by_id(self):
        nonexistent_user_id = 1
        with self.assertRaises(NotFoundException):
            self.user_repo.delete_user_by_id(nonexistent_user_id)

    def test_delete_user_with_course_enrollment_dependencies(self):
        new_user, sample_password = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()

        enrollment = CourseEnrollment(
            user_id=new_user.user_id,
            course_id=courses[0].course_id,
            role=Role.STUDENT
        )
        self.add_single_enrollment(enrollment)

        with self.assertRaises(DependencyException):
            self.user_repo.delete_user_by_id(new_user.user_id)

        get_user_query = '''
        SELECT user_id, full_name, email, hashed_password
        FROM user
        WHERE user_id = %s
        '''
        params = (new_user.user_id,)

        cursor = self.connection.cursor()
        cursor.execute(get_user_query, params)
        cursor_result = cursor.fetchone()
        self.assertIsNotNone(cursor_result)

        user_id, full_name, email, hashed_password = cursor_result
        self.assertEqual(user_id, new_user.user_id)
        self.assertEqual(full_name, new_user.full_name)
        self.assertEqual(email, new_user.email)
        self.assertTrue(check_password_hash(hashed_password, sample_password))

    def test_delete_user_with_page_creation_dependencies(self):
        new_user, sample_password = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        page = Page(
            created_by_user_id=new_user.user_id,
            page_content="Sample content",
            page_title="Sample title",
            page_visibility_setting=VisibilitySetting.LISTED,
            url_path_after_course_path="/",
            course_id=course.course_id
        )
        self.add_single_page_and_get_id(page)

        with self.assertRaises(DependencyException):
            self.user_repo.delete_user_by_id(new_user.user_id)

        get_user_query = '''
        SELECT user_id, full_name, email, hashed_password
        FROM user
        WHERE user_id = %s
        '''
        params = (new_user.user_id,)

        cursor = self.connection.cursor()
        cursor.execute(get_user_query, params)
        cursor_result = cursor.fetchone()
        self.assertIsNotNone(cursor_result)

        user_id, full_name, email, hashed_password = cursor_result
        self.assertEqual(user_id, new_user.user_id)
        self.assertEqual(full_name, new_user.full_name)
        self.assertEqual(email, new_user.email)
        self.assertTrue(check_password_hash(hashed_password, sample_password))

    def test_delete_user_with_file_creation_dependencies(self):
        # TODO implement with file attachments feature
        pass
