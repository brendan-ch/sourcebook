import unittest
import mysql.connector
from testcontainers.mysql import MySqlContainer
from pathlib import Path

from config import TEST_CONTAINER_IMAGE


class TestContainerSample(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.mysql_container = MySqlContainer(TEST_CONTAINER_IMAGE)
        self.mysql_container.start()

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

    @classmethod
    def tearDownClass(self):
        self.connection.close()
        self.mysql_container.stop()

    def setUp(self):
        project_root = Path(__file__).resolve().parent.parent
        setup_sql_schema_path = project_root / 'sql' / 'setup_schema.sql'

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

    def test_first_select_query(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT 'Hello World';")
        result = cursor.fetchone()
        self.assertEqual(result[0], 'Hello World')

    def test_second_select_query(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        self.assertEqual(result[0], 1)
