from dataclasses import dataclass


@dataclass
class AttendanceSession:
    attendance_session_id: int
    course_id: int
    opening_time: str
    closing_time: str
    title: str
