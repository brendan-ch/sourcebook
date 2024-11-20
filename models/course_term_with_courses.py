from dataclasses import dataclass
from typing import Optional

from models.course import Course
from models.course_term import CourseTerm

@dataclass(kw_only=True)
class CourseTermWithCourses(CourseTerm):
    courses: Optional[list[Course]] = None