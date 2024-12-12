from datetime import datetime, timedelta

from custom_exceptions import NotFoundException
from datarepos.attendance_repo import AttendanceRepo
from models.attendance_record import AttendanceRecord, AttendanceRecordStatus
from models.attendance_session import AttendanceSession
from models.course_enrollment import CourseEnrollment, Role
from test.test_with_database_container import TestWithDatabaseContainer


class TestAttendanceRepo(TestWithDatabaseContainer):
    def setUp(self):
        super().setUp()
        self.attendance_repo = AttendanceRepo(self.connection)

    def add_course_and_users_for_attendance_test(self):
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
        return course, users

    def add_single_attendance_session_and_get_id(self, attendance_session):
        insert_session_query = '''
        INSERT INTO attendance_session (course_id, title, opening_time, closing_time, attendance_session_id) 
        VALUES (%s, %s, %s, %s, %s)
        '''
        params = (
            attendance_session.course_id,
            attendance_session.title,
            attendance_session.opening_time,
            attendance_session.closing_time,
            attendance_session.attendance_session_id,
        )

        cursor = self.connection.cursor()
        cursor.execute(insert_session_query, params)
        attendance_session_id = cursor.lastrowid
        self.connection.commit()

        return attendance_session_id

    def add_single_attendance_record(self, attendance_record: AttendanceRecord):
        insert_record_query = '''
        INSERT INTO attendance_record (user_id, attendance_session_id, attendance_status) 
        VALUES (%s, %s, %s)
        '''
        params = (
            attendance_record.user_id,
            attendance_record.attendance_session_id,
            attendance_record.attendance_status.value
        )

        cursor = self.connection.cursor()
        cursor.execute(insert_record_query, params)
        self.connection.commit()

    def test_start_new_attendance_session_and_get_id(self):
        course, users = self.add_course_and_users_for_attendance_test()

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

        cursor = self.connection.cursor(dictionary=True)
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

        cursor.execute(check_records_query, params)
        results = cursor.fetchall()
        returned_records = [AttendanceRecord(**result) for result in results]

        for record in returned_records:
            matching_user = [user for user in users if user.user_id == record.user_id]
            self.assertEqual(len(matching_user), 1)
            self.assertEqual(matching_user[0].user_id, record.user_id)
            self.assertEqual(returned_session.attendance_session_id, record.attendance_session_id)
            self.assertEqual(record.attendance_status, AttendanceRecordStatus.NONE)

    def test_close_in_progress_session(self):
        course, users = self.add_course_and_users_for_attendance_test()

        course_id = course.course_id
        attendance_session = AttendanceSession(
            course_id=course_id,
            opening_time=datetime.now(),
            title="Attendance Session",
        )

        attendance_session_id = self.add_single_attendance_session_and_get_id(attendance_session)
        self.attendance_repo.close_in_progress_session(attendance_session_id)

        select_session_query = '''
        SELECT ats.closing_time
        FROM attendance_session ats
        WHERE ats.attendance_session_id = %s
        '''
        params = (attendance_session_id,)

        cursor = self.connection.cursor()
        cursor.execute(select_session_query, params)
        closing_time, = cursor.fetchone()
        self.assertIsNotNone(closing_time)
        self.assertIsInstance(closing_time, datetime)

    def test_close_not_in_progress_session(self):
        course, users = self.add_course_and_users_for_attendance_test()

        course_id = course.course_id
        attendance_session = AttendanceSession(
            course_id=course_id,
            opening_time=datetime.now(),
            closing_time=datetime.now() + timedelta(hours=2),
            title="Attendance Session",
        )

        attendance_session_id = self.add_single_attendance_session_and_get_id(attendance_session)

        with self.assertRaises(NotFoundException):
            self.attendance_repo.close_in_progress_session(attendance_session_id)

    def test_delete_attendance_session_and_records(self):
        course, users = self.add_course_and_users_for_attendance_test()

        course_id = course.course_id
        attendance_session = AttendanceSession(
            course_id=course_id,
            opening_time=datetime.now(),
            closing_time=datetime.now() + timedelta(hours=2),
            title="Attendance Session",
        )
        attendance_session_id = self.add_single_attendance_session_and_get_id(attendance_session)

        self.add_student_attendance_records_for_users(attendance_session_id, users)

        self.attendance_repo.delete_attendance_session_and_records(attendance_session_id)

        check_session_query = '''
        SELECT
            ats.attendance_session_id
        FROM attendance_session ats
        WHERE ats.attendance_session_id = %s
        '''
        params = (attendance_session_id,)

        cursor = self.connection.cursor()
        cursor.execute(check_session_query, params)
        result = cursor.fetchone()
        self.assertIsNone(result)

        check_records_query = '''
        SELECT atr.user_id, atr.attendance_session_id, atr.attendance_status
        FROM attendance_record atr
        WHERE atr.attendance_session_id = %s
        '''
        cursor.execute(check_records_query, params)
        results = cursor.fetchall()
        self.assertEqual(len(results), 0)

    def add_student_attendance_records_for_users(self, attendance_session_id, users):
        attendance_records = [
            AttendanceRecord(
                attendance_session_id=attendance_session_id,
                user_id=user.user_id,
                attendance_status=AttendanceRecordStatus.NONE,
            )
            for user in users
        ]
        for attendance_record in attendance_records:
            self.add_single_attendance_record(attendance_record)

        return attendance_records

    def test_edit_attendance_session_title(self):
        course, users = self.add_course_and_users_for_attendance_test()
        course_id = course.course_id

        attendance_session = AttendanceSession(
            course_id=course_id,
            opening_time=datetime.now(),
            title="Attendance Session",
        )
        attendance_session.attendance_session_id = self.add_single_attendance_session_and_get_id(attendance_session)

        self.attendance_repo.edit_attendance_session_title(
            attendance_session_id=attendance_session.attendance_session_id,
            new_title="New Title"
        )

        check_new_title_query = '''
        SELECT ats.title
        FROM attendance_session ats
        WHERE ats.attendance_session_id = %s
        '''
        params = (attendance_session.attendance_session_id,)

        cursor = self.connection.cursor()
        cursor.execute(check_new_title_query, params)
        new_title, = cursor.fetchone()
        self.assertEqual(new_title, "New Title")

    def test_update_attendance_record_status(self):
        course, users = self.add_course_and_users_for_attendance_test()
        course_id = course.course_id

        attendance_session = AttendanceSession(
            course_id=course_id,
            opening_time=datetime.now(),
            title="Attendance Session",
        )
        attendance_session.attendance_session_id = self.add_single_attendance_session_and_get_id(attendance_session)

        records = self.add_student_attendance_records_for_users(attendance_session.attendance_session_id, users)

        records[0].attendance_status = AttendanceRecordStatus.PRESENT
        self.attendance_repo.update_status_by_attendance_session_and_user_id(
            records[0]
        )

        check_record_query = '''
        SELECT atr.attendance_status
        FROM attendance_record atr
        WHERE atr.attendance_session_id = %s
            AND atr.user_id = %s
        '''
        params = (attendance_session.attendance_session_id, records[0].user_id)

        cursor = self.connection.cursor()
        cursor.execute(check_record_query, params)
        attendance_status, = cursor.fetchone()

        self.assertEqual(attendance_status, records[0].attendance_status.value)

    def test_get_active_attendance_sessions_from_course_id(self):
        course, users = self.add_course_and_users_for_attendance_test()

        attendance_session = AttendanceSession(
            course_id=course.course_id,
            opening_time=datetime.now(),
            title="Attendance Session",
        )
        attendance_session.attendance_session_id = self.add_single_attendance_session_and_get_id(attendance_session)
        attendance_session.opening_time = attendance_session.opening_time.replace(microsecond=0)

        returned_sessions = self.attendance_repo.get_active_attendance_sessions_from_course_id(course.course_id)
        self.assertEqual(len(returned_sessions), 1)
        self.assertEqual(attendance_session, returned_sessions[0])

