from typing import Optional

from datarepos.course_enrollment import CourseEnrollment
from datarepos.repo import Repo
from models.course import Course


class CourseRepo(Repo):
    def get_all_course_enrollments_for_user_id(self, user_id: int) -> list[CourseEnrollment]:
        pass

    def get_course_by_starting_url_if_exists(self, url: str) -> Optional[Course]:
        pass

    def get_course_by_id_if_exists(self, course_id: int) -> Optional[Course]:
        pass

    def check_whether_user_has_editing_rights(self, user_id: int, course_id: int) -> bool:
        pass

    def add_new_course_and_get_id(self, course: Course):
        pass

    def update_course_metadata_by_id(self, course: Course):
        pass

    def delete_course_by_id(self, course_id: int):
        pass

    def add_course_enrollment(self, course_enrollment: CourseEnrollment):
        pass

    def update_role_by_course_and_user_id(self, course_enrollment: CourseEnrollment):
        pass

    def delete_course_enrollment_by_id(self, course_id: int, user_id: int):
        pass
