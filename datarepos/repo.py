import mysql.connector
from mysql.connector import IntegrityError

from config import DATABASE_HOST, DATABASE_PORT, DATABASE_USER, DATABASE_PASSWORD, DATABASE_SCHEMA_NAME
from custom_exceptions import AlreadyExistsException, NotFoundException, DependencyException


class Repo:
    MYSQL_DUPLICATE_ENTRY_EXCEPTION_CODE = 1062
    MYSQL_FOREIGN_KEY_CONSTRAINT_EXCEPTION_CODE = 1451

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

    def close_connection(self):
        self.connection.close()
        self.connection_is_open = False

    def insert_single_entry_into_db_and_return_id(self, insert_query, params):
        cursor = self.connection.cursor()
        try:
            cursor.execute(insert_query, params)
            self.connection.commit()
        except IntegrityError as e:
            if e.errno == self.MYSQL_DUPLICATE_ENTRY_EXCEPTION_CODE:
                raise AlreadyExistsException
            else:
                raise e
        id = cursor.lastrowid
        return id

    def execute_dml_query_and_check_rowcount_greater_than_0(self, update_query, params):
        cursor = self.connection.cursor()
        try:
            cursor.execute(update_query, params)
        except IntegrityError as e:
            if e.errno == self.MYSQL_DUPLICATE_ENTRY_EXCEPTION_CODE:
                raise AlreadyExistsException
            elif e.errno == self.MYSQL_FOREIGN_KEY_CONSTRAINT_EXCEPTION_CODE:
                raise DependencyException
            else:
                raise e
        row_count = cursor.rowcount
        if row_count < 1:
            raise NotFoundException

        self.connection.commit()
