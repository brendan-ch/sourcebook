from flask import Blueprint, render_template, session, abort

from flask_helpers import get_user_from_session
from flask_repository_getters import get_course_repository, get_user_repository
from models.page import Page, VisibilitySetting

course_bp = Blueprint("course", __name__)

@course_bp.route("/<string:course_url>/", methods=["GET"])
def course_home_page(course_url: str):
    user = get_user_from_session()
    course_repo = get_course_repository()

    course = course_repo.get_course_by_starting_url_if_exists("/" + course_url)
    if not course:
        return render_template("404.html"), 404

    role = None
    if user:
        role = course_repo.get_user_role_in_class_if_exists(user.user_id, course.course_id)

    # In the future add a check to see if the class has pages
    # set to public or private

    if not role:
        return render_template(
            "401.html",
            custom_error_message="You need to be enrolled in this course to see it."
        ), 401

    return render_template(
        "course_static_page.html",
        course=course,
        user=user,
        role=role,
        # page_html_content=sample_html_content,
    )

@course_bp.route("/<string:course_url>/<path:custom_static_path>/", methods=["GET"])
def course_custom_static_url_page(course_url: str, custom_static_path: str):
    # TODO render static page
    return f"Custom static path for {course_url}: {custom_static_path}"

@course_bp.route("/<string:course_url>/<path:custom_static_path>/edit/", methods=["GET", "POST"])
def course_custom_static_url_edit_page(course_url: str, custom_static_path: str):
    # TODO render edit page
    return f"Edit page for static path for {course_url}: {custom_static_path}"

