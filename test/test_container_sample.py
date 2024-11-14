import unittest
import mysql.connector
from testcontainers.mysql import MySqlContainer

class TestContainerSample(unittest.TestCase):
    # Try to open a MySQL test container and run a query in it
    # Perform validation on the query

    def setUp(self):
        self.mysql_container = MySqlContainer('mysql:5.7.17')
        self.mysql_container.start()

        host = self.mysql_container.get_container_host_ip()
        port = self.mysql_container.get_exposed_port(3306)
        user = self.mysql_container.MYSQL_USER
        password = self.mysql_container.MYSQL_PASSWORD
        database = self.mysql_container.MYSQL_DATABASE

        self.connection = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            ssl_disabled=True
        )

    def tearDown(self):
        self.connection.close()
        self.mysql_container.stop()

    def test_select_query(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT 'Hello World';")
        result = cursor.fetchone()
        self.assertEqual(result[0], 'Hello World')