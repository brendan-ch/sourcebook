from dataclasses import dataclass

from models.attendance_record import AttendanceRecord


@dataclass(kw_only=True)
class AttendanceRecordWithName(AttendanceRecord):
    full_name: str