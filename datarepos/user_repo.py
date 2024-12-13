from typing import Optional

import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

from custom_exceptions import AlreadyExistsException, DependencyException
from datarepos.repo import Repo
from models.user import User



class UserRepo(Repo):
    def get_user_id_if_credentials_match(self, email: str, given_password: str) -> Optional[str]:
        get_user_query = '''
        SELECT user_id, hashed_password
        FROM user
        WHERE user.email = %s
        '''
        params = (email,)

        cursor = self.connection.cursor()
        cursor.execute(get_user_query, params)

        cursor_result = cursor.fetchone()
        if not cursor_result:
            return None

        user_id, hashed_password = cursor_result
        if check_password_hash(hashed_password, given_password):
            return user_id

        return None

    def get_user_from_id_if_exists(self, user_id: int) -> Optional[User]:
        get_user_query = '''
        SELECT user_id, user_uuid, email, full_name
        FROM user
        WHERE user.user_id = %s
        '''
        params = (user_id,)

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(get_user_query, params)
        cursor_result = cursor.fetchone()

        if cursor_result:
            return User(**cursor_result)
        return None

    def get_user_from_uuid_if_exists(self, user_uuid: str) -> Optional[User]:
        get_user_query = '''
        SELECT user_id, user_uuid, email, full_name
        FROM user
        WHERE user.user_uuid = %s
        '''
        params = (user_uuid,)

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(get_user_query, params)
        cursor_result = cursor.fetchone()

        if cursor_result:
            return User(**cursor_result)
        return None

    def add_new_user_and_get_id(self, user: User, given_password: str) -> str:
        if user.user_id or user.user_uuid:
            raise AlreadyExistsException

        hashed_password = generate_password_hash(given_password)

        # noinspection SqlInsertValues
        insert_query = '''
        INSERT INTO user(full_name, email, hashed_password) 
        VALUES (%s, %s, %s)
        '''
        params = (user.full_name, user.email, hashed_password)

        try:
            cursor = self.connection.cursor()
            cursor.execute(insert_query, params)
            self.connection.commit()
            row_id = cursor.lastrowid
            return row_id
        except mysql.connector.errors.IntegrityError as e:
            if e.errno == self.MYSQL_DUPLICATE_ENTRY_EXCEPTION_CODE:
                raise AlreadyExistsException

    def delete_user_by_id(self, user_id: int):
        delete_user_query = '''
        DELETE FROM user
        WHERE user.user_id = %s
        '''
        params = (user_id,)

        precheck_query = '''
        SELECT COUNT(*)
        FROM user
        WHERE user.user_id = %s;
        '''

        self.execute_dml_query(delete_user_query, params, precheck_query, params)
