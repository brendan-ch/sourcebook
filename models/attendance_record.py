from dataclasses import dataclass
from enum import Enum


class AttendanceRecordStatus(Enum):
    NONE = 0
    PRESENT = 1
    LATE = 2
    ABSENT = 3
    EXCUSED = 4

@dataclass(kw_only=True)
class AttendanceRecord:
    user_id: int
    attendance_session_id: int
    attendance_status: AttendanceRecordStatus

    def __post_init__(self):
        if not isinstance(self.attendance_status, AttendanceRecordStatus):
            self.attendance_status = AttendanceRecordStatus(int(self.attendance_status))

        if not isinstance(self.user_id, int):
            self.user_id = int(self.user_id)

        if not isinstance(self.attendance_session_id, int):
            self.attendance_session_id = int(self.attendance_session_id)
