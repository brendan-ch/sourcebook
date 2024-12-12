from datarepos.repo import Repo
from models.attendance_record import AttendanceRecordStatus


class AttendanceRepo(Repo):
    def start_new_attendance_session_and_get_id(self, course_id: int):
        pass

    def close_in_progress_session(self, attendance_session_id: int):
        pass

    def delete_attendance_session_and_records(self, attendance_session_id: int):
        pass

    def edit_attendance_session_title(self, attendance_session_id: int, new_title: str):
        pass

    def update_attendance_record_status(self, user_id: int, attendance_session_id: int, status: AttendanceRecordStatus):
        pass
