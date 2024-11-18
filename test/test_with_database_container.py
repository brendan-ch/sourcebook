import unittest

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
