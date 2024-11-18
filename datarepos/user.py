import mysql.connector

from config import DATABASE_HOST, DATABASE_PORT, DATABASE_USER, DATABASE_PASSWORD, DATABASE_SCHEMA_NAME


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
