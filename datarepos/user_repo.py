from typing import Optional

import mysql.connector
from werkzeug.security import generate_password_hash

from config import DATABASE_HOST, DATABASE_PORT, DATABASE_USER, DATABASE_PASSWORD, DATABASE_SCHEMA_NAME
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
        pass

    def get_user_from_id_if_exists(self, user_id: str) -> Optional[User]:
        pass

    def add_new_user_and_get_id(self, user: User, given_password: str):
        pass

    def close_connection(self):
        self.connection.close()
        self.connection_is_open = False
