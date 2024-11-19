from dataclasses import dataclass
from enum import Enum
from typing import Optional

from models.course import Course


class Role(Enum):
    STUDENT = 1
    ASSISTANT = 2
    PROFESSOR = 3


@dataclass
class CourseEnrollment:
    role: Role
    user_id: int

    course_id: int
    course: Optional[Course] = None

    def __post_init__(self):
        if isinstance(self.role, int):
            self.role = Role(self.role)
