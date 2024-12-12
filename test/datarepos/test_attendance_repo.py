from datarepos.attendance_repo import AttendanceRepo
from models.attendance_record import AttendanceRecord, AttendanceRecordStatus
from models.attendance_session import AttendanceSession
from models.course_enrollment import CourseEnrollment, Role
from test.test_with_database_container import TestWithDatabaseContainer


class TestAttendanceRepo(TestWithDatabaseContainer):
    def setUp(self):
        super().setUp()
        self.attendance_repo = AttendanceRepo(self.connection)

    def test_start_new_attendance_session_and_get_id(self):
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course = courses[0]

        users = self.add_many_sample_users_to_test_db()
        for user in users:
            enrollment = CourseEnrollment(
                user_id=user.user_id,
                course_id=course.course_id,
                role=Role.STUDENT
            )
            self.add_single_enrollment(enrollment)

        session_id = self.attendance_repo.start_new_attendance_session_and_get_id(course.course_id)

        check_session_query = '''
        SELECT
            ats.course_id,
            ats.attendance_session_id,
            ats.title,
            ats.closing_time,
            ats.opening_time
        FROM attendance_session ats
        WHERE ats.attendance_session_id = %s
        '''
        params = (session_id,)

        cursor = self.connection.cursor()
        cursor.execute(check_session_query, params)
        result = cursor.fetchone()
        returned_session = AttendanceSession(**result)

        self.assertEqual(returned_session.course_id, course.course_id)
        self.assertEqual(returned_session.attendance_session_id, session_id)

        check_records_query = '''
        SELECT atr.user_id, atr.attendance_session_id, atr.attendance_status
        FROM attendance_record atr
        WHERE atr.attendance_session_id = %s
        '''

        cursor.execute(check_session_query, params)
        results = cursor.fetchall()
        returned_records = [AttendanceRecord(**result) for result in results]

        for record in returned_records:
            matching_user = [user for user in users if user.user_id == record.user_id]
            self.assertEqual(len(matching_user), 1)
            self.assertEqual(matching_user[0].user_id, record.user_id)
            self.assertEqual(returned_session.attendance_session_id, record.attendance_session_id)
            self.assertEqual(record.attendance_status, AttendanceRecordStatus.NONE)

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
