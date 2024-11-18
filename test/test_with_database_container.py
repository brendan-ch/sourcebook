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

    @classmethod
    def tearDownClass(cls):
        cls.mysql_container.stop()

    def setUp(self):
        host = self.mysql_container.get_container_host_ip()
        port = self.mysql_container.get_exposed_port(3306)
        user = self.mysql_container.username
        password = self.mysql_container.password
        database = self.mysql_container.dbname

        self.connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )

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

        self.connection.close()
