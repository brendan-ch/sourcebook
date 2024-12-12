from datarepos.attendance_repo import AttendanceRepo
from test.test_with_database_container import TestWithDatabaseContainer


class TestAttendanceRepo(TestWithDatabaseContainer):
    def setUp(self):
        super().setUp()
        self.attendance_repo = AttendanceRepo(self.connection)

    def test_start_new_attendance_session_and_get_id(self):
        courses, _ = self.add_sample_course_term_and_course_cluster()
        users = self.add_many_sample_users_to_test_db()

        # Check that a new session was created
        # Check that attendance records were created for
        # every student enrolled in the class
        pass

    def test_close_in_progress_session(self):
        # Test that a closing time was added to the data
        pass

    def test_close_not_in_progress_session(self):
        pass

    def test_delete_attendance_session_and_records(self):
        pass

    def test_edit_attendance_session_title(self):
        pass

    def test_update_attendance_record_status(self):
        pass
