from datetime import datetime

from custom_exceptions import NotFoundException
from datarepos.repo import Repo
from models.attendance_record import AttendanceRecordStatus, AttendanceRecord
from models.attendance_session import AttendanceSession
from models.course_enrollment import Role


class AttendanceRepo(Repo):
    def start_new_attendance_session_and_get_id(self, course_id: int):
        date_format_string = '%Y.%m.%d %H:%M'

        # TODO check if course id doesn't exist

        new_session = AttendanceSession(
            course_id=course_id,
            opening_time=datetime.now(),
            title=datetime.now().strftime(date_format_string),
        )

        cursor = self.connection.cursor()
        try:

            insert_new_session_query = '''
            INSERT INTO attendance_session (course_id, opening_time, closing_time, title)
            VALUES (%s, %s, %s, %s)
            '''
            params = (
                new_session.course_id,
                new_session.opening_time,
                new_session.closing_time,
                new_session.title,
            )
            cursor.execute(insert_new_session_query, params)

            attendance_session_id = cursor.lastrowid

            select_student_enrollments_query = '''
            SELECT enrollment.user_id
            FROM enrollment
            WHERE enrollment.course_id = %s
                AND enrollment.role = %s
            '''
            params = (course_id, Role.STUDENT.value)

            cursor.execute(select_student_enrollments_query, params)
            student_enrollment_results = cursor.fetchall()

            insert_record_query = '''
            INSERT INTO attendance_record (user_id, attendance_session_id, attendance_status) 
            VALUES (%s, %s, %s)
            '''
            insert_record_params = [
                (user_id, attendance_session_id, AttendanceRecordStatus.NONE.value)
                for user_id, in student_enrollment_results
            ]

            cursor.executemany(insert_record_query, insert_record_params)
            self.connection.commit()

            return attendance_session_id

        except Exception as e:
            self.connection.rollback()
            raise e

    def close_in_progress_session(self, attendance_session_id: int):
        update_query = '''
        UPDATE attendance_session ats
        SET ats.closing_time = %s
        WHERE ats.attendance_session_id = %s
            AND ats.closing_time IS NULL
        '''
        params = (
            datetime.now(),
            attendance_session_id,
        )

        precheck_query = '''
        SELECT COUNT(*)
        FROM attendance_session ats
        WHERE ats.attendance_session_id = %s
            AND ats.closing_time IS NULL
        '''
        precheck_params = (attendance_session_id,)

        self.execute_dml_query(update_query, params, precheck_query, precheck_params)

    def delete_attendance_session_and_records(self, attendance_session_id: int):
        delete_session_query = '''
        DELETE FROM attendance_session ats
        WHERE ats.attendance_session_id = %s
        '''
        delete_records_query = '''
        DELETE FROM attendance_record atr
        WHERE atr.attendance_session_id = %s
        '''
        params = (attendance_session_id,)
        try:
            cursor = self.connection.cursor()
            cursor.execute(delete_records_query, params)
            cursor.execute(delete_session_query, params)

            if cursor.rowcount < 1:
                raise NotFoundException
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e


    def edit_attendance_session_title(self, attendance_session_id: int, new_title: str):
        update_query = '''
        UPDATE attendance_session ats
        SET ats.title = %s
        WHERE ats.attendance_session_id = %s
        '''
        params = (
            new_title,
            attendance_session_id,
        )

        precheck_query = '''
        SELECT COUNT(*)
        FROM attendance_session ats
        WHERE ats.attendance_session_id = %s
            AND ats.closing_time IS NULL
        '''
        precheck_params = (attendance_session_id,)

        self.execute_dml_query(update_query, params, precheck_query, precheck_params)

    def update_status_by_attendance_session_and_user_id(self, attendance_record: AttendanceRecord):
        update_query = '''
        UPDATE attendance_record atr
        SET atr.attendance_status = %s
        WHERE atr.attendance_session_id = %s
            AND atr.user_id = %s
        '''
        params = (
            attendance_record.attendance_status.value,
            attendance_record.attendance_session_id,
            attendance_record.user_id,
        )

        precheck_query = '''
        SELECT COUNT(*)
        FROM attendance_record atr
        WHERE atr.attendance_session_id = %s
            AND atr.user_id = %s
        '''
        precheck_params = (
            attendance_record.attendance_session_id,
            attendance_record.user_id
        )

        self.execute_dml_query(update_query, params, precheck_query, precheck_params)

    def get_active_attendance_sessions_from_course_id(self, course_id: int):
        select_query = '''
        SELECT ats.title, ats.opening_time, ats.closing_time, ats.attendance_session_id, ats.course_id
        FROM attendance_session ats
        WHERE ats.course_id = %s
            AND ats.closing_time IS NULL
        ORDER BY ats.opening_time DESC;
        '''
        params = (course_id,)

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(select_query, params)
        results = cursor.fetchall()

        return [AttendanceSession(**result) for result in results]

    def get_closed_attendance_sessions_from_course_id(self, course_id: int):
        select_query = '''
        SELECT ats.title, ats.opening_time, ats.closing_time, ats.attendance_session_id, ats.course_id
        FROM attendance_session ats
        WHERE ats.course_id = %s
            AND ats.closing_time IS NOT NULL
        ORDER BY ats.opening_time DESC;
        '''
        params = (course_id,)

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(select_query, params)
        results = cursor.fetchall()

        return [AttendanceSession(**result) for result in results]
