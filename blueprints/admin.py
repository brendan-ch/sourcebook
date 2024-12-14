import csv
import os

from flask import Blueprint, render_template, redirect, flash

from flask_repository_getters import get_content_repository, get_user_repository, get_course_repository, \
    get_attendance_repository

admin_bp = Blueprint('admin', __name__, url_prefix='')

def generate_one_set_of_exports(
    cursor,
    database_table_name: str,
    file_name: str,
    header = None
):
    get_all_courses_query = f'''SELECT * FROM {database_table_name};'''

    cursor.execute(get_all_courses_query)
    result = cursor.fetchall()

    writer = csv.writer(open(f'exports/{file_name}', 'w'))
    if header:
        writer.writerow(header)
    for line in result:
        writer.writerow(line)

@admin_bp.route('/')
def admin_options():
    return render_template("admin_options.html")

@admin_bp.route('/export-tables', methods=['POST'])
def export_tables():
    content_repo = get_content_repository()

    os.makedirs('exports', exist_ok=True)

    exports_to_generate = {
        'course': 'courses.csv',
        'user': 'users.csv',
        'page': 'pages.csv',
        'file': 'files.csv',
        'page_file_bridge': 'page_file_bridge.csv',
        'attendance_session': 'attendance_sessions.csv',
        'attendance_record': 'attendance_record.csv',
    }

    for key in exports_to_generate:
        value = exports_to_generate[key]

        # Using the underlying connection is an antipattern,
        # but I was pretty crunched for time when I wrote this
        generate_one_set_of_exports(
            cursor=content_repo.connection.cursor(),
            database_table_name=key,
            file_name=value
        )

    flash('Exports generated under exports directory in project root.')
    return redirect('/')

@admin_bp.route('/export-student-count-per-class', methods=['POST'])
def export_student_count_per_class():
    course_repo = get_course_repository()

    query = '''
    SELECT course.course_id, course.title, course.user_friendly_class_code, COUNT(filtered_enrollments.user_id)
    FROM course
    INNER JOIN (
        SELECT enrollment.course_id, enrollment.user_id
        FROM enrollment
        WHERE enrollment.role = 1
    ) as filtered_enrollments
        ON course.course_id = filtered_enrollments.course_id
    GROUP BY course.course_id
    '''

    cursor = course_repo.connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()

    writer = csv.writer(open(f'exports/student_count_per_class.csv', 'w'))
    writer.writerow(['course_id', 'title', 'user_friendly_class_code', 'student_count'])
    for line in result:
        writer.writerow(line)

    flash('Export generated under exports directory in project root.')
    return redirect('/')

@admin_bp.route('/export-attendance-records-and-students', methods=['POST'])
def export_all_attendance_records_and_students():
    attendance_repo = get_attendance_repository()

    query = '''
    SELECT * FROM attendance_records_students_classes;
    '''

    cursor = attendance_repo.connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()

    os.makedirs('exports', exist_ok=True)

    writer = csv.writer(open(f'exports/attendance_records_and_students.csv', 'w'))
    writer.writerow(['full_name', 'email', 'user_id', 'attendance_session_id', 'attendance_status', 'title', 'user_friendly_class_code'])
    for line in result:
        writer.writerow(line)

    flash('Export generated under exports directory in project root.')
    return redirect('/')
