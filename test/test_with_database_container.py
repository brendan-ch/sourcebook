import unittest
from pathlib import Path
from os import system
from subprocess import Popen, PIPE

import mysql.connector
from testcontainers.mysql import MySqlContainer

from config import TEST_CONTAINER_IMAGE

TEST_ROOT_PASSWORD = "12345"

class TestWithDatabaseContainer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mysql_container = MySqlContainer(
            image=TEST_CONTAINER_IMAGE,
            root_password=TEST_ROOT_PASSWORD,
        )
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

        cursor = self.connection.cursor()
        cursor.execute("USE test;")
        self.connection.commit()

        project_root = Path(__file__).resolve().parent.parent
        setup_sql_schema_path = project_root / 'sql' / 'setup_schema.sql'

        # Login as root to execute CREATE TRIGGER statements
        command = f'mysql -u root -p{TEST_ROOT_PASSWORD} --host={'127.0.0.1' if host == 'localhost' else host} --port={port} {database} < "{setup_sql_schema_path}"'
        system(command)

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
