import csv
import os

from flask import Blueprint, render_template, redirect, flash

from flask_repository_getters import get_content_repository, get_user_repository

admin_bp = Blueprint('admin', __name__, url_prefix='')

def generate_one_set_of_exports(
    cursor,
    database_table_name: str,
    file_name: str
):
    get_all_courses_query = f'''SELECT * FROM {database_table_name};'''

    cursor.execute(get_all_courses_query)
    result = cursor.fetchall()

    writer = csv.writer(open(f'exports/{file_name}', 'w'))
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

        generate_one_set_of_exports(
            cursor=content_repo.connection.cursor(),
            database_table_name=key,
            file_name=value
        )

    generate_one_set_of_exports(
        cursor=content_repo.connection.cursor(),
        database_table_name='user',
        file_name='users.csv'
    )

    flash('Export generated under exports directory in project root.')
    return redirect('/')
