from typing import Optional

import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

from config import DATABASE_HOST, DATABASE_PORT, DATABASE_USER, DATABASE_PASSWORD, DATABASE_SCHEMA_NAME
from custom_exceptions import AlreadyExistsException
from models.user import User


class UserRepo:
    def __init__(self, connection = None):
        if not connection:
            self.connection = mysql.connector.connect(
                host=DATABASE_HOST,
                port=DATABASE_PORT,
                user=DATABASE_USER,
                password=DATABASE_PASSWORD,
                database=DATABASE_SCHEMA_NAME
            )
        else:
            self.connection = connection

        self.connection_is_open = True

    def get_user_role_in_class(self, user_id: str, class_id: str):
        # TODO implement after class data model is created
        raise NotImplemented

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
        SELECT user_id, email, full_name
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

    def add_new_user_and_get_id(self, user: User, given_password: str) -> str:
        if user.user_id:
            raise AlreadyExistsException

        hashed_password = generate_password_hash(given_password)

        # noinspection SqlInsertValues
        insert_query = '''
        INSERT INTO user(full_name, email, hashed_password) 
        VALUES (%s, %s, %s)
        '''
        params = (user.full_name, user.email, hashed_password)

        cursor = self.connection.cursor()
        cursor.execute(insert_query, params)
        row_id = cursor.lastrowid
        return row_id

    def close_connection(self):
        self.connection.close()
        self.connection_is_open = False
