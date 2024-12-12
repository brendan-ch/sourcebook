from dataclasses import dataclass


@dataclass
class AttendanceSession:
    attendance_session_id: str
    course_id: str
    opening_time: str
    closing_time: str
    title: str
