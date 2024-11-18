from test.test_with_database_container import TestWithDatabaseContainer

class TestContainerSample(TestWithDatabaseContainer):
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
