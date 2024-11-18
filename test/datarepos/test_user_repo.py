import unittest

from datarepos.user_repo import UserRepo
from test.test_with_database_container import TestWithDatabaseContainer
from werkzeug.security import generate_password_hash

from models.user import User

class TestUserRepo(TestWithDatabaseContainer):
    def setUp(self):
        super().setUp()
        self.user_repo = UserRepo(self.connection)

    def add_sample_user_to_test_db(self):
        new_user = User(user_id="1",
                        full_name="Test Name",
                        email="example@example.com")
        sample_password = "C4x6Fc4YbxUsWtz.Luj*ECo*xv@xGkQXv_h.-khVXqvAkmgiZgCoBn*Kj_.C-e9@"
        hashed_password = generate_password_hash(sample_password)
        add_query = '''
        INSERT INTO user (user_id, full_name, email, hashed_password)
        VALUES (%s, %s, %s, %s)
        '''
        params = (new_user.user_id, new_user.full_name, new_user.email, hashed_password)
        cursor = self.connection.cursor()
        cursor.execute(add_query, params)
        return new_user, sample_password

    def test_get_user_id_if_credentials_match(self):
        new_user, sample_password = self.add_sample_user_to_test_db()

        user_id_to_validate = self.user_repo.get_user_id_if_credentials_match(new_user.email, sample_password)
        self.assertEqual(user_id_to_validate, new_user.user_id)


    def test_get_user_id_if_credentials_not_match(self):
        nonexistent_email = "example@example.com"
        nonexistent_password = "C4x6Fc4YbxUsWtz.Luj*ECo*xv@xGkQXv_h.-khVXqvAkmgiZgCoBn*Kj_.C-e9@"

        user_id_to_validate = self.user_repo.get_user_id_if_credentials_match(nonexistent_email, nonexistent_password)
        self.assertEqual(user_id_to_validate, None)

    def test_get_user_from_id_if_exists(self):
        pass

    def test_get_user_from_id_if_not_exists(self):
        pass
