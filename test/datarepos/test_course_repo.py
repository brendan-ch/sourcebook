from datarepos.course_enrollment import CourseEnrollment, Role
from datarepos.course_repo import CourseRepo
from models.course import Course
from models.course_term import CourseTerm
from test.test_with_database_container import TestWithDatabaseContainer


class TestCourseRepo(TestWithDatabaseContainer):
    def setUp(self):
        super().setUp()
        self.course_repo = CourseRepo(self.connection)

    def test_get_all_course_enrollments_for_user_id(self):
        user, _ = self.add_sample_user_to_test_db()

        course_terms = [
            CourseTerm(
                title="Fall 2024",
                position_from_top=1
            ),
            CourseTerm(
                title="Spring 2024",
                position_from_top=2
            ),
            CourseTerm(
                title="Interterm 2024",
                position_from_top=3
            ),
            CourseTerm(
                title="Fall 2023",
                position_from_top=4
            ),
        ]

        insert_course_term_query = '''
        INSERT INTO course_term(title, position_from_top)
        VALUES (%s, %s);
        '''
        for course_term in course_terms:
            params = (course_term.title, course_term.position_from_top)
            cursor = self.connection.cursor()
            cursor.execute(insert_course_term_query, params)

            course_term.course_term_id = cursor.lastrowid

        self.connection.commit()

        courses = [
            Course(
                title="Visual Programming",
                user_friendly_class_code="CPSC 236",
                starting_url_path="/cpsc-236-f24",
                course_term_id=course_terms[0].course_term_id,
            ),
            Course(
                title="Database Management",
                user_friendly_class_code="CPSC 408",
                starting_url_path="/cpsc-408-f24",
                course_term_id=course_terms[0].course_term_id,
            ),
            Course(
                title="Operating Systems",
                user_friendly_class_code="CPSC 380",
                starting_url_path="/cpsc-380-s24",
                course_term_id=course_terms[1].course_term_id,
            ),
        ]

        insert_course_query = '''
        INSERT INTO course(title, user_friendly_class_code, starting_url_path, course_term_id)
        VALUES (%s, %s, %s, %s);
        '''

        for course in courses:
            params = (course.title, course.user_friendly_class_code, course.starting_url_path, course.course_term_id)
            cursor = self.connection.cursor()
            cursor.execute(insert_course_query, params)

            course.course_id = cursor.lastrowid

        self.connection.commit()

        course_enrollments = [
            CourseEnrollment(
                course_id=courses[1].course_id,
                role=Role.STUDENT,
                user_id=user.user_id,
            ),
            CourseEnrollment(
                course_id=courses[0].course_id,
                role=Role.ASSISTANT,
                user_id=user.user_id,
            )
        ]

        insert_course_enrollment_query = '''
        INSERT INTO enrollment(course_id, role, user_id)
        VALUES (%s, %s, %s);
        '''

        for course_enrollment in course_enrollments:
            params = (course_enrollment.course_id, course_enrollment.role.value, course_enrollment.user_id)
            cursor = self.connection.cursor()
            cursor.execute(insert_course_enrollment_query, params)

        self.connection.commit()

        # Try running the method
        # Validate the result
        returned_course_enrollments = self.course_repo.get_all_course_enrollments_for_user_id(user.user_id)

        self.assertNotEqual(returned_course_enrollments, None)
        self.assertEqual(len(returned_course_enrollments), len(course_enrollments))

        # Validate the order by using strictly indices
        for course_enrollment, returned_course_enrollment in zip(course_enrollments, returned_course_enrollments):
            self.assertEqual(course_enrollment.course_id, returned_course_enrollment.course_id)
            self.assertEqual(course_enrollment.role, returned_course_enrollment.role)
            self.assertEqual(course_enrollment.user_id, returned_course_enrollment.user_id)

    def test_get_course_enrollments_for_user_id_if_no_enrollments(self):
        pass

    def test_get_course_by_id_if_exists(self):
        pass

    def test_get_course_by_id_if_not_exists(self):
        pass

    def test_check_whether_student_has_editing_rights(self):
        pass

    def test_check_whether_professor_has_editing_rights(self):
        pass

    def test_check_whether_assistant_has_editing_rights(self):
        pass

    def test_check_whether_admin_has_editing_rights(self):
        pass

    def test_add_new_course_and_get_id(self):
        pass

    def test_add_duplicate_course(self):
        pass

    def test_update_course_metadata_by_id(self):
        pass

    def test_update_nonexistent_course_metadata(self):
        pass

    def test_delete_course_by_id_if_exists(self):
        pass

    def test_delete_course_by_id_if_not_exists(self):
        pass

    def test_add_course_enrollment(self):
        pass

    def test_add_duplicate_course_enrollment(self):
        pass

    def test_update_role_by_course_and_user_id(self):
        pass

    def test_update_role_for_nonexistent_course_enrollment(self):
        pass

    def test_delete_course_enrollment_by_id(self):
        pass

    def test_delete_course_enrollment_by_id_if_not_exists(self):
        pass
