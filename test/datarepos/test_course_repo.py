import copy

from custom_exceptions import AlreadyExistsException, NotFoundException, DependencyException
from models.course_enrollment import CourseEnrollment, Role
from datarepos.course_repo import CourseRepo
from models.course import Course
from test.test_with_database_container import TestWithDatabaseContainer



class TestCourseRepo(TestWithDatabaseContainer):
    def setUp(self):
        super().setUp()
        self.course_repo = CourseRepo(self.connection)

    def assert_single_course_against_database_query(self, course_select_query, original_course: Course, params = None):
        cursor = self.connection.cursor()
        cursor.execute(course_select_query, params)
        results = cursor.fetchall()
        self.assertEqual(len(results), 1)

        course_id, course_term_id, starting_url_path, title, user_friendly_class_code = results[0]
        self.assertEqual(course_id, original_course.course_id)
        self.assertEqual(course_term_id, original_course.course_term_id)
        self.assertEqual(starting_url_path, original_course.starting_url_path)
        self.assertEqual(title, original_course.title)
        self.assertEqual(user_friendly_class_code, original_course.user_friendly_class_code)


    def assert_single_enrollment_against_database(self, enrollment):
        select_course_enrollment_query = '''
        SELECT enrollment.course_id, enrollment.user_id, enrollment.role
        FROM enrollment
        '''

        cursor = self.connection.cursor()
        cursor.execute(select_course_enrollment_query)
        results = cursor.fetchall()
        self.assertEqual(len(results), 1)

        course_id, user_id, role = results[0]
        self.assertEqual(course_id, enrollment.course_id)
        self.assertEqual(user_id, enrollment.user_id)
        self.assertEqual(role, enrollment.role.value)

    def test_get_all_course_enrollments_for_user_id(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()

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

        # Validate the result of running the method
        returned_course_enrollments = self.course_repo.get_all_course_enrollments_for_user_id(user.user_id)

        self.assertNotEqual(returned_course_enrollments, None)
        self.assertEqual(len(returned_course_enrollments), len(course_enrollments))

        # Validate ordering by role, then course ID
        for course_enrollment, returned_course_enrollment in zip(course_enrollments, returned_course_enrollments):
            self.assertEqual(course_enrollment.course_id, returned_course_enrollment.course_id)
            self.assertEqual(course_enrollment.role, returned_course_enrollment.role)
            self.assertEqual(course_enrollment.user_id, returned_course_enrollment.user_id)


    def test_get_course_enrollments_for_user_id_if_no_enrollments(self):
        user, _ = self.add_sample_user_to_test_db()

        returned_course_enrollments = self.course_repo.get_all_course_enrollments_for_user_id(user.user_id)

        self.assertNotEqual(returned_course_enrollments, None)
        self.assertEqual(len(returned_course_enrollments), 0)

    def test_get_course_terms_with_courses_for_user_id(self):
        user, _ = self.add_sample_user_to_test_db()
        (
            course_terms_to_enroll_user_in,
            courses_to_enroll_user_in_as_assistant,
            courses_to_enroll_user_in_as_student,
            courses_to_not_enroll_user_in
        ) = self.add_sample_course_term_and_course_enrollment_cluster(user.user_id)

        # Validate the course terms returned and the order
        course_terms_with_courses = self.course_repo.get_course_terms_with_courses_for_user_id(user.user_id)
        self.assertIsNotNone(course_terms_with_courses)
        for course_term_with_courses, original_course_term in zip(course_terms_with_courses, course_terms_to_enroll_user_in):
            self.assertEqual(course_term_with_courses.title, original_course_term.title)
            self.assertEqual(course_term_with_courses.course_term_id, original_course_term.course_term_id)
            self.assertEqual(course_term_with_courses.position_from_top, original_course_term.position_from_top)

            # Verify that each course present on the returned object is supposed to be there
            for course_to_check in course_term_with_courses.courses:
                matching_courses = [enrolled_course for enrolled_course in courses_to_enroll_user_in_as_student if enrolled_course.course_id == course_to_check.course_id]
                if not matching_courses:
                    matching_courses = [enrolled_course for enrolled_course in courses_to_enroll_user_in_as_assistant if enrolled_course.course_id == course_to_check.course_id]

                self.assertEqual(len(matching_courses), 1)
                matching_course = matching_courses[0]

                self.assertEqual(matching_course.course_term_id, course_to_check.course_term_id)
                self.assertEqual(matching_course.starting_url_path, course_to_check.starting_url_path)
                self.assertEqual(matching_course.title, course_to_check.title)
                self.assertEqual(matching_course.user_friendly_class_code, course_to_check.user_friendly_class_code)

            # Verify that courses which shouldn't appear shouldn't appear
            for non_appearing_course in courses_to_not_enroll_user_in:
                course_ids = [course.course_id for course in course_term_with_courses.courses]
                self.assertNotIn(non_appearing_course.course_id, course_ids)

    def test_get_course_terms_with_courses_if_no_enrollments(self):
        user, _ = self.add_sample_user_to_test_db()
        self.add_sample_course_term_and_course_cluster()

        course_terms = self.course_repo.get_course_terms_with_courses_for_user_id(user.user_id)
        self.assertIsNotNone(course_terms)
        self.assertEqual(len(course_terms), 0)

    def test_get_course_by_starting_url_if_exists(self):
        courses, _ = self.add_sample_course_term_and_course_cluster()

        returned_course = self.course_repo.get_course_by_starting_url_if_exists(courses[0].starting_url_path)
        self.assertNotEqual(returned_course, None)
        self.assertEqual(returned_course.course_id, courses[0].course_id)
        self.assertEqual(returned_course.course_term_id, courses[0].course_term_id)
        self.assertEqual(returned_course.starting_url_path, courses[0].starting_url_path)
        self.assertEqual(returned_course.user_friendly_class_code, courses[0].user_friendly_class_code)
        self.assertEqual(returned_course.title, courses[0].title)

    def test_get_course_by_starting_url_if_not_exists(self):
        nonexistent_starting_url = "/test"
        returned_course = self.course_repo.get_course_by_starting_url_if_exists(nonexistent_starting_url)
        self.assertEqual(returned_course, None)

    def test_get_course_by_id_if_exists(self):
        courses, _ = self.add_sample_course_term_and_course_cluster()

        returned_course = self.course_repo.get_course_by_id_if_exists(courses[0].course_id)
        self.assertNotEqual(returned_course, None)
        self.assertEqual(returned_course.course_id, courses[0].course_id)
        self.assertEqual(returned_course.course_term_id, courses[0].course_term_id)
        self.assertEqual(returned_course.starting_url_path, courses[0].starting_url_path)
        self.assertEqual(returned_course.user_friendly_class_code, courses[0].user_friendly_class_code)
        self.assertEqual(returned_course.title, courses[0].title)

    def test_get_course_by_id_if_not_exists(self):
        nonexistent_course_id = 1
        returned_course = self.course_repo.get_course_by_id_if_exists(nonexistent_course_id)
        self.assertEqual(returned_course, None)

    def test_check_whether_roles_has_editing_rights(self):
        roles = list(Role)

        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()

        for role in roles:
            with self.subTest(role=role):
                enrollment = CourseEnrollment(role=role, user_id=user.user_id, course_id=courses[0].course_id)
                self.add_single_enrollment(enrollment)

                result = self.course_repo.check_whether_user_has_editing_rights(user.user_id, courses[0].course_id)

                expected_result = False if role == Role.STUDENT else True
                self.assertEqual(result, expected_result)

            # Regardless of whether test fails or succeeds,
            # clear enrollments
            delete_query = '''
            DELETE FROM enrollment;
            '''
            cursor = self.connection.cursor()
            cursor.execute(delete_query)
            self.connection.commit()

    def test_check_if_user_has_editing_rights_if_not_enrolled(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()

        result = self.course_repo.check_whether_user_has_editing_rights(user.user_id, courses[0].course_id)
        self.assertEqual(result, False)

    def test_add_new_course_and_get_id(self):
        new_course = Course(
            title="Visual Programming",
            user_friendly_class_code="CPSC 236",
            starting_url_path="/cpsc-236-f24"
        )

        new_course.course_id = self.course_repo.add_new_course_and_get_id(new_course)
        self.assertNotEqual(new_course.course_id, None)

        # Validate the intended side effects
        course_select_query = '''
        SELECT course.course_id,
            course.course_term_id,
            course.starting_url_path,
            course.title,
            course.user_friendly_class_code
        FROM course
        '''

        self.assert_single_course_against_database_query(course_select_query, new_course)

    def test_add_course_with_id(self):
        courses, _ = self.add_sample_course_term_and_course_cluster()
        duplicate_course_id = courses[0].course_id

        course_with_id = Course(
            course_id=duplicate_course_id,
            title="Database Management",
            user_friendly_class_code="CPSC 408",
            starting_url_path="/cpsc-408-s24" # non-duplicate
        )

        with self.assertRaises(AlreadyExistsException):
            self.course_repo.add_new_course_and_get_id(course_with_id)

        # Validate the original course to make sure nothing changed
        course_select_query = '''
        SELECT course.course_id,
            course.course_term_id,
            course.starting_url_path,
            course.title,
            course.user_friendly_class_code
        FROM course
        WHERE course.course_id = %s
        '''
        params = (duplicate_course_id,)

        self.assert_single_course_against_database_query(course_select_query, courses[0], params)


    def test_add_course_with_duplicate_starting_url(self):
        courses, _ = self.add_sample_course_term_and_course_cluster()
        duplicate_starting_url = courses[0].starting_url_path

        course_with_duplicate_url = Course(
            title="Database Management",
            user_friendly_class_code="CPSC 408",
            starting_url_path=duplicate_starting_url
        )

        with self.assertRaises(AlreadyExistsException):
            self.course_repo.add_new_course_and_get_id(course_with_duplicate_url)

        course_select_query = '''
        SELECT course.course_id,
            course.course_term_id,
            course.starting_url_path,
            course.title,
            course.user_friendly_class_code
        FROM course
        WHERE course.starting_url_path = %s
        '''
        params = (duplicate_starting_url,)

        self.assert_single_course_against_database_query(
            course_select_query, courses[0], params
        )

    def test_update_course_metadata_by_id(self):
        courses, course_terms = self.add_sample_course_term_and_course_cluster()
        modified_course = courses[0]

        # Modify every field
        modified_course.starting_url_path = "/cpsc-350-f24"
        modified_course.title = "Data Structures and Algorithms"
        modified_course.user_friendly_class_code = "CPSC 350"
        modified_course.course_term_id = course_terms[1].course_term_id

        self.course_repo.update_course_metadata_by_id(modified_course)

        course_select_query = '''
        SELECT course.course_id,
            course.course_term_id,
            course.starting_url_path,
            course.title,
            course.user_friendly_class_code
        FROM course
        WHERE course.course_id = %s
        '''
        params = (modified_course.course_id,)
        self.assert_single_course_against_database_query(course_select_query, modified_course, params)


    def test_update_nonexistent_course_metadata(self):
        new_course = Course(
            course_id=1,
            title="Visual Programming",
            user_friendly_class_code="CPSC 236",
            starting_url_path="/cpsc-236-f24"
        )

        with self.assertRaises(NotFoundException):
            self.course_repo.update_course_metadata_by_id(new_course)

    def test_update_course_metadata_with_duplicate_starting_url(self):
        courses, _ = self.add_sample_course_term_and_course_cluster()
        original_course = copy.deepcopy(courses[0])
        modified_course = courses[0]

        modified_course.title = "Data Structures and Algorithms"
        modified_course.user_friendly_class_code = "CPSC 350"

        # Change the starting URL to that of another row
        other_starting_url = courses[1].starting_url_path
        modified_course.starting_url_path = other_starting_url

        with self.assertRaises(AlreadyExistsException):
            self.course_repo.update_course_metadata_by_id(modified_course)

        course_select_query = '''
        SELECT course.course_id,
            course.course_term_id,
            course.starting_url_path,
            course.title,
            course.user_friendly_class_code
        FROM course
        WHERE course.course_id = %s
        '''
        params = (original_course.course_id,)
        self.assert_single_course_against_database_query(course_select_query, original_course, params)

    def test_delete_course_by_id_if_exists_and_no_dependencies(self):
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course_to_delete = courses[0]

        self.course_repo.delete_course_by_id(course_to_delete.course_id)

        course_select_query = '''
        SELECT course.course_id
        FROM course
        WHERE course.course_id = %s
        '''
        params = (course_to_delete.course_id,)

        cursor = self.connection.cursor()
        cursor.execute(course_select_query, params)
        result = cursor.fetchone()
        self.assertEqual(result, None)

    def test_delete_course_by_id_if_not_exists(self):
        nonexistent_course_id = 1

        with self.assertRaises(NotFoundException):
            self.course_repo.delete_course_by_id(nonexistent_course_id)

    def test_delete_course_by_id_if_exists_and_dependencies(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course_to_delete = courses[0]

        # Add dependencies in the form of course enrollments
        enrollment = CourseEnrollment(
            course_id=course_to_delete.course_id,
            user_id = user.user_id,
            role=Role.STUDENT
        )
        self.add_single_enrollment(enrollment)

        with self.assertRaises(DependencyException):
            self.course_repo.delete_course_by_id(course_to_delete.course_id)

        # Validate that the course was not deleted
        course_select_query = '''
        SELECT course.course_id,
            course.course_term_id,
            course.starting_url_path,
            course.title,
            course.user_friendly_class_code
        FROM course
        WHERE course.course_id = %s
        '''
        params = (course_to_delete.course_id,)
        self.assert_single_course_against_database_query(course_select_query, course_to_delete, params)

    def test_get_user_role_in_class_if_different_roles_exist(self):
        roles = list(Role)

        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()

        for role in roles:
            with self.subTest(role=role):
                enrollment = CourseEnrollment(role=role, user_id=user.user_id, course_id=courses[0].course_id)
                self.add_single_enrollment(enrollment)

                result = self.course_repo.get_user_role_in_class_if_exists(user.user_id, courses[0].course_id)
                self.assertEqual(result, role)

            # Regardless of whether test fails or succeeds,
            # clear enrollments
            delete_query = '''
            DELETE FROM enrollment;
            '''
            cursor = self.connection.cursor()
            cursor.execute(delete_query)
            self.connection.commit()

    def test_get_user_role_in_class_if_not_exists(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()

        result = self.course_repo.get_user_role_in_class_if_exists(user.user_id, courses[0].course_id)
        self.assertIsNone(result)

    def test_add_course_enrollment(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()

        course_to_enroll = courses[0]

        enrollment = CourseEnrollment(
            course_id=course_to_enroll.course_id,
            user_id = user.user_id,
            role=Role.STUDENT
        )

        self.course_repo.add_course_enrollment(enrollment)
        self.assert_single_enrollment_against_database(enrollment)

    def test_add_duplicate_course_enrollment(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()

        course_to_enroll = courses[0]
        enrollment = CourseEnrollment(
            course_id=course_to_enroll.course_id,
            user_id = user.user_id,
            role=Role.STUDENT
        )

        # Add the enrollment before calling the method
        self.add_single_enrollment(enrollment)

        enrollment.role = Role.ASSISTANT

        with self.assertRaises(AlreadyExistsException):
            self.course_repo.add_course_enrollment(enrollment)

        # Switch back to original role for validation
        enrollment.role = Role.STUDENT

        self.assert_single_enrollment_against_database(enrollment)


    def test_update_role_by_course_and_user_id(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course_to_enroll = courses[0]

        enrollment = CourseEnrollment(
            course_id=course_to_enroll.course_id,
            user_id=user.user_id,
            role=Role.STUDENT
        )

        # Add the enrollment beforehand
        self.add_single_enrollment(enrollment)

        # Change the role on the enrollment
        enrollment.role = Role.ASSISTANT
        self.course_repo.update_role_by_course_and_user_id(enrollment)

        self.assert_single_enrollment_against_database(enrollment)

    def test_update_role_for_nonexistent_course_enrollment(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course_to_enroll = courses[0]

        enrollment = CourseEnrollment(
            course_id=course_to_enroll.course_id,
            user_id=user.user_id,
            role=Role.STUDENT
        )

        with self.assertRaises(NotFoundException):
            self.course_repo.update_role_by_course_and_user_id(enrollment)

    def test_delete_course_enrollment_by_id(self):
        user, _ = self.add_sample_user_to_test_db()
        courses, _ = self.add_sample_course_term_and_course_cluster()
        course_to_enroll = courses[0]

        enrollment = CourseEnrollment(
            course_id=course_to_enroll.course_id,
            user_id=user.user_id,
            role=Role.STUDENT
        )
        self.add_single_enrollment(enrollment)

        self.course_repo.delete_course_enrollment_by_id(enrollment.course_id, enrollment.user_id)

        # Validate that it was deleted
        select_enrollment_query = '''
        SELECT enrollment.course_id, enrollment.user_id
        FROM enrollment
        WHERE enrollment.course_id = %s AND enrollment.user_id = %s
        '''
        params = (enrollment.course_id, enrollment.user_id)

        cursor = self.connection.cursor()
        cursor.execute(select_enrollment_query, params)
        result = cursor.fetchone()
        self.assertEqual(result, None)

    def test_delete_course_enrollment_by_id_if_not_exists(self):
        nonexistent_course_id = 1
        nonexistent_user_id = 1

        with self.assertRaises(NotFoundException):
            self.course_repo.delete_course_enrollment_by_id(nonexistent_course_id, nonexistent_user_id)
