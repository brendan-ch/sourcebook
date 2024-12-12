from datarepos.attendance_repo import AttendanceRepo
from test.test_with_database_container import TestWithDatabaseContainer


class TestAttendanceRepo(TestWithDatabaseContainer):
    def setUp(self):
        super().setUp()
        self.attendance_repo = AttendanceRepo(self.connection)

    def test_start_new_attendance_session(self):
        pass

    def test_close_in_progress_session(self):
        pass

    def test_close_not_in_progress_session(self):
        pass

