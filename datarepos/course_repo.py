from collections import defaultdict
from typing import Optional

from mysql.connector import IntegrityError

from custom_exceptions import AlreadyExistsException, NotFoundException, DependencyException
from models.course_enrollment import CourseEnrollment, Role
from datarepos.repo import Repo
from models.course import Course
from models.course_term_with_courses import CourseTermWithCourses


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

    def get_course_terms_with_courses_for_user_id(self, user_id: int) -> list[CourseTermWithCourses]:
        get_courses_and_course_terms_query = '''
        SELECT
            course.course_id,
            course.course_term_id,
            course.starting_url_path,
            course.title as course_title,
            course.user_friendly_class_code,
            course_term.title as course_term_title,
            course_term.position_from_top
        FROM course
        INNER JOIN course_term
            ON course.course_term_id = course_term.course_term_id
        INNER JOIN enrollment
            ON course.course_id = enrollment.course_id
        WHERE enrollment.user_id = %s
        ORDER BY course_term.position_from_top ASC, course.user_friendly_class_code ASC
        '''
        params = (user_id,)

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(get_courses_and_course_terms_query, params)
        results = cursor.fetchall()

        course_terms_dict = defaultdict(list[Course])

        # Group courses by course_term_id
        for result in results:
            course = Course(
                title=result["course_title"],
                user_friendly_class_code=result["user_friendly_class_code"],
                starting_url_path=result["starting_url_path"],
                course_term_id=result["course_term_id"],
                course_id=result["course_id"],
            )
            course_terms_dict[(
                result["course_term_id"],
                result["course_term_title"],
                result["position_from_top"]
            )].append(course)

        course_terms_with_courses = [
            CourseTermWithCourses(
                title=term_title,
                position_from_top=position_from_top,
                course_term_id=term_id,
                courses=courses,
            )
            for (
                term_id,
                term_title,
                position_from_top,
            ), courses in course_terms_dict.items()
        ]

        return course_terms_with_courses


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
        role = self.get_user_role_in_class_if_exists(user_id, course_id)
        if not role or role == Role.STUDENT:
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

        course_id = self.insert_single_entry_into_db_and_return_id(add_course_query, params)
        return course_id

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

        precheck_query = '''
        SELECT COUNT(*)
        FROM course
        WHERE course.course_id = %s;
        '''
        precheck_params = (course.course_id,)

        self.execute_dml_query(update_query, params, precheck_query, precheck_params)

    def delete_course_by_id(self, course_id: int):
        delete_course_query = '''
        DELETE FROM course
        WHERE course.course_id = %s;
        '''
        params = (course_id,)

        precheck_query = '''
        SELECT COUNT(*)
        FROM course
        WHERE course.course_id = %s;
        '''

        self.execute_dml_query(delete_course_query, params, precheck_query, params)

    def get_user_role_in_class_if_exists(self, user_id: str, course_id: str) -> Optional[Role]:
        get_enrollment_query = '''
        SELECT enrollment.role
        FROM enrollment
        WHERE enrollment.user_id = %s 
            AND enrollment.course_id = %s;
        '''
        params = (user_id, course_id)

        cursor = self.connection.cursor()
        cursor.execute(get_enrollment_query, params)
        result = cursor.fetchone()
        if not result:
            return None

        role_number, = result
        role = Role(role_number)

        return role

    def add_course_enrollment(self, course_enrollment: CourseEnrollment):
        add_course_enrollment_query = '''
        INSERT INTO enrollment(enrollment.course_id, enrollment.user_id, enrollment.role)
        VALUES (%s, %s, %s);
        '''
        params = (course_enrollment.course_id, course_enrollment.user_id, course_enrollment.role.value)

        self.insert_single_entry_into_db_and_return_id(add_course_enrollment_query, params)

    def update_role_by_course_and_user_id(self, course_enrollment: CourseEnrollment):
        update_course_enrollment_query = '''
        UPDATE enrollment
        SET enrollment.role = %s
        WHERE enrollment.course_id = %s
            AND enrollment.user_id = %s;
        '''
        params = (course_enrollment.role.value, course_enrollment.course_id, course_enrollment.user_id)

        cursor = self.connection.cursor()
        cursor.execute(update_course_enrollment_query, params)

        if cursor.rowcount < 1:
            raise NotFoundException

        self.connection.commit()

    def delete_course_enrollment_by_id(self, course_id: int, user_id: int):
        delete_course_enrollment_query = '''
        DELETE FROM enrollment
        WHERE course_id = %s AND user_id = %s;
        '''
        params = (course_id, user_id)

        cursor = self.connection.cursor()
        cursor.execute(delete_course_enrollment_query, params)

        if cursor.rowcount < 1:
            raise NotFoundException

        self.connection.commit()

