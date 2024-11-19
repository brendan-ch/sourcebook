from typing import Optional

from datarepos.repo import Repo
from models.course import Course


class CourseRepo(Repo):
    def get_all_course_enrollments_for_user_id(self, user_id: int) -> list[Course]:
        pass

    def get_course_by_starting_url_if_exists(self, url: str) -> Optional[Course]:
        pass

    def get_course_by_id_if_exists(self, course_id: int) -> Optional[Course]:
        pass

