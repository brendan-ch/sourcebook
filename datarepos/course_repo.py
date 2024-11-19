from typing import Optional

from mysql.connector import IntegrityError

from custom_exceptions import AlreadyExistsException, NotFoundException
from datarepos.course_enrollment import CourseEnrollment, Role
from datarepos.repo import Repo
from models.course import Course


class CourseRepo(Repo):
    def get_all_course_enrollments_for_user_id(self, user_id: int) -> list[CourseEnrollment]:
        get_all_enrollments_query = '''
        SELECT enrollment.course_id, enrollment.user_id, enrollment.role
        FROM enrollment
        WHERE enrollment.user_id = %s 
        ORDER BY enrollment.role ASC, enrollment.course_id ASC;
        '''
        params = (user_id,)

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(get_all_enrollments_query, params)
        results = cursor.fetchall()

        enrollments = [CourseEnrollment(**result) for result in results]
        return enrollments

    def get_course_by_starting_url_if_exists(self, url: str) -> Optional[Course]:
        get_course_query = '''
        SELECT
            course.course_id,
            course.course_term_id,
            course.starting_url_path,
            course.title,
            course.user_friendly_class_code
        FROM course
        WHERE course.starting_url_path = %s;
        '''
        params = (url,)

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(get_course_query, params)
        result = cursor.fetchone()

        if result:
            return Course(**result)
        return None

    def get_course_by_id_if_exists(self, course_id: int) -> Optional[Course]:
        get_course_query = '''
        SELECT
            course.course_id,
            course.course_term_id,
            course.starting_url_path,
            course.title,
            course.user_friendly_class_code
        FROM course
        WHERE course.course_id = %s;
        '''
        params = (course_id,)

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(get_course_query, params)
        result = cursor.fetchone()

        if result:
            return Course(**result)
        return None

    def check_whether_user_has_editing_rights(self, user_id: int, course_id: int) -> bool:
        get_enrollment_query = '''
        SELECT enrollment.role
        FROM enrollment
        WHERE enrollment.user_id = %s 
            AND enrollment.course_id = %s;
        '''
        params = (user_id, course_id)

        cursor = self.connection.cursor()
        cursor.execute(get_enrollment_query, params)
        result, = cursor.fetchone()
        role = Role(result)

        if role == Role.STUDENT:
            return False
        return True

    def add_new_course_and_get_id(self, course: Course):
        if course.course_id:
            raise AlreadyExistsException

        add_course_query = '''
        INSERT INTO course(
            course.title,
            course.course_term_id,
            course.starting_url_path,
            course.user_friendly_class_code
        )
        VALUES (%s, %s, %s, %s);
        '''
        params = (course.title,
                  course.course_term_id,
                  course.starting_url_path,
                  course.user_friendly_class_code)

        cursor = self.connection.cursor()

        try:
            cursor.execute(add_course_query, params)
            self.connection.commit()
        except IntegrityError as e:
            if e.errno == self.MYSQL_DUPLICATE_ENTRY_EXCEPTION_CODE:
                raise AlreadyExistsException
            else:
                raise IntegrityError

        id = cursor.lastrowid
        return id

    def update_course_metadata_by_id(self, course: Course):
        update_query = '''
        UPDATE course
        SET
            course.course_term_id = %s,
            course.user_friendly_class_code = %s,
            course.starting_url_path = %s,
            course.title = %s
        WHERE course.course_id = %s;
        '''
        params = (
            course.course_term_id,
            course.user_friendly_class_code,
            course.starting_url_path,
            course.title,
            course.course_id
        )

        cursor = self.connection.cursor()

        try:
            cursor.execute(update_query, params)
        except IntegrityError as e:
            if e.errno == self.MYSQL_DUPLICATE_ENTRY_EXCEPTION_CODE:
                raise AlreadyExistsException
            else:
                raise IntegrityError

        row_count = cursor.rowcount
        if row_count < 1:
            raise NotFoundException

        self.connection.commit()


    def delete_course_by_id(self, course_id: int):
        pass

    def add_course_enrollment(self, course_enrollment: CourseEnrollment):
        pass

    def update_role_by_course_and_user_id(self, course_enrollment: CourseEnrollment):
        pass

    def delete_course_enrollment_by_id(self, course_id: int, user_id: int):
        pass
