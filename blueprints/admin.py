import csv
import os

from flask import Blueprint, render_template, redirect, flash

from flask_repository_getters import get_content_repository

admin_bp = Blueprint('admin', __name__, url_prefix='')

@admin_bp.route('/')
def admin_options():
    return render_template("admin_options.html")

@admin_bp.route('/export-tables', methods=['POST'])
def export_tables():
    content_repo = get_content_repository()

    os.makedirs('exports', exist_ok=True)

    get_all_courses_query = '''SELECT * FROM course;'''

    cursor = content_repo.connection.cursor()
    cursor.execute(get_all_courses_query)
    result = cursor.fetchall()

    writer = csv.writer(open('exports/courses.csv', 'w'))
    for line in result:
        writer.writerow(line)

    flash('Export generated under exports directory in project root.')
    return redirect('/')
