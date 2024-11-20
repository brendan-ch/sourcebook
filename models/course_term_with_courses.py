from models.course import Course
from models.course_term import CourseTerm


class CourseTermWithCourses(CourseTerm):
    courses: list[Course]