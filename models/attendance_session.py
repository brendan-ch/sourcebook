from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AttendanceSession:
    course_id: int
    title: str
    opening_time: datetime
    closing_time: Optional[datetime]
    attendance_session_id: Optional[int]
