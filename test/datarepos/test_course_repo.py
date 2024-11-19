from datarepos.course_repo import CourseRepo
from test.test_with_database_container import TestWithDatabaseContainer


class TestCourseRepo(TestWithDatabaseContainer):
    def setUp(self):
        super().setUp()
        self.course_repo = CourseRepo(self.connection)

    def test_get_all_course_enrollments_for_user_id(self):
        # Add a user to the database
        # Add a few sample courses
        # Add a few course enrollments (student and TA)
        # Try running the method
        # Validate the result

        pass

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
