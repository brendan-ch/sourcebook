from custom_exceptions import NotFoundException
from datarepos.repo import Repo
from test.test_with_database_container import TestWithDatabaseContainer


class TestRepo(TestWithDatabaseContainer):
    def setUp(self):
        super().setUp()
        self.repo = Repo(self.connection)

    def test_execute_dml_query_with_same_values_as_previous(self):
        # Test that an UPDATE call without any visible changes goes through

        insertion_query = '''
        INSERT INTO course_term (title, position_from_top)
        VALUES ('Fall 2024', 1);
        '''

        cursor = self.connection.cursor()
        cursor.execute(insertion_query)
        self.connection.commit()

        row_id = cursor.lastrowid

        test_update_query = '''
        UPDATE course_term
        SET title = 'Fall 2024', position_from_top = 1
        WHERE course_term_id = %s
        '''
        params = (row_id,)

        self.repo.execute_dml_query(test_update_query, params)

    def test_execute_dml_query_with_not_found_precheck(self):
        precheck_query = '''
        SELECT COUNT(*)
        FROM course_term
        WHERE course_term_id = 1
        '''

        test_update_query = '''
        UPDATE course_term
        SET title = 'Fall 2024', position_from_top = 1
        WHERE course_term_id = 1
        '''

        with self.assertRaises(NotFoundException):
            self.repo.execute_dml_query(test_update_query, (), precheck_query)
