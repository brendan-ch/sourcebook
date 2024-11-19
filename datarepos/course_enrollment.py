from dataclasses import dataclass
from enum import Enum

from models.course import Course


class Role(Enum):
    STUDENT = 1
    ASSISTANT = 2
    PROFESSOR = 3
    ADMIN = 4


@dataclass
class CourseEnrollment:
    course: Course
    role: Role
    user_id: str