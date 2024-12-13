from typing import Optional

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

    def execute_dml_query(
        self,
        update_query,
        params,
        not_found_precheck_query: Optional[str] = None,
        not_found_precheck_params: Optional[tuple] = None
    ):
        """
        Execute a DML query with commit/rollback.

        :param update_query: DML query to be executed.
        :param params: Params to pass into the DML query.
        :param not_found_precheck_query: Optional `SELECT COUNT(*) FROM table_name`
        query run before the update query, raising a NotFoundException if
        count < 1.
        :param not_found_precheck_params: Params to pass into `not_found_precheck_query`.
        :raises DependencyException if foreign key constraint violated
        :raises AlreadyExistsException if primary key or unique constraint violated
        """
        # If provided, this query checks whether the value exists
        # by checking the row count
        if not_found_precheck_query:
            cursor = self.connection.cursor()
            cursor.execute(not_found_precheck_query, not_found_precheck_params)
            count, = cursor.fetchone()

            if count < 1:
                raise NotFoundException

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

        self.connection.commit()
