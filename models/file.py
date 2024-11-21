from dataclasses import dataclass
from typing import Optional


@dataclass
class File:
    file_id: int
    file_uuid: str
    filepath: str

    uploaded_by_user_id: Optional[int]
    course_id: Optional[int]
