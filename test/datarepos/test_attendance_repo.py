from datarepos.attendance_repo import AttendanceRepo
from test.test_with_database_container import TestWithDatabaseContainer


class TestAttendanceRepo(TestWithDatabaseContainer):
    def setUp(self):
        super().setUp()
        self.attendance_repo = AttendanceRepo(self.connection)

    def test_start_new_attendance_session(self):
        # Check that attendance records were created for
        # every student enrolled in the class
        pass

    def test_close_in_progress_session(self):
        pass

    def test_close_not_in_progress_session(self):
        pass

    def test_delete_attendance_session_and_records(self):
        pass

    def test_edit_attendance_session_title(self):
        pass

    def test_update_attendance_record_status(self):
        pass
