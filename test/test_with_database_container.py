import unittest
from pathlib import Path

import mysql.connector
from testcontainers.mysql import MySqlContainer

from config import TEST_CONTAINER_IMAGE


class TestWithDatabaseContainer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mysql_container = MySqlContainer(TEST_CONTAINER_IMAGE)
        cls.mysql_container.start()

        host = cls.mysql_container.get_container_host_ip()
        port = cls.mysql_container.get_exposed_port(3306)
        user = cls.mysql_container.username
        password = cls.mysql_container.password
        database = cls.mysql_container.dbname

        cls.connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )

    @classmethod
    def tearDownClass(cls):
        cls.connection.close()
        cls.mysql_container.stop()


    def setUp(self):
        project_root = Path(__file__).resolve().parent.parent
        setup_sql_schema_path = project_root / 'sql' / 'setup_schema.sql'

        cursor = self.connection.cursor()
        cursor.execute("USE test;")
        self.connection.commit()

        with setup_sql_schema_path.open('r') as f:
            sql_commands = f.read().split(';')
            cursor = self.connection.cursor()
            for command in sql_commands:
                if command:
                    cursor.execute(command)
            self.connection.commit()

    def tearDown(self):
        project_root = Path(__file__).resolve().parent.parent
        teardown_sql_file_path = project_root / 'sql' / 'teardown_schema.sql'

        with teardown_sql_file_path.open('r') as f:
            sql_commands = f.read().split(';')
            cursor = self.connection.cursor()
            for command in sql_commands:
                if command:
                    cursor.execute(command)
            self.connection.commit()