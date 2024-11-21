from flask import Blueprint, render_template, session

from flask_repository_getters import get_course_repository, get_user_repository

course_bp = Blueprint("course", __name__)

@course_bp.route("/<string:course_url>/", methods=["GET"])
def course_home_page(course_url: str):
    course_repo = get_course_repository()

    user = None
    if "user_id" in session and session["user_id"]:
        user_repo = get_user_repository()
        user = user_repo.get_user_from_id_if_exists(session["user_id"])

    course = course_repo.get_course_by_starting_url_if_exists("/" + course_url)
    if not course:
        # TODO render 404 page template
        return "Course not found", 404

    role = None
    if user:
        role = course_repo.get_user_role_in_class_if_exists(user.user_id, course.course_id)

    # In the future add a check to see if the class has pages
    # set to public or private

    if not role:
        # TODO render 401 page template
        return "Not enrolled in course", 401

    return render_template(
        "course_static_page.html",
        course=course,
        user=user,
        role=role,
    )



@course_bp.route("/<string:course_url>/<path:custom_static_path>/", methods=["GET"])
def course_custom_static_url_page(course_url: str, custom_static_path: str):
    # TODO render static page
    return f"Custom static path for {course_url}: {custom_static_path}"

@course_bp.route("/<string:course_url>/<path:custom_static_path>/edit/", methods=["GET", "POST"])
def course_custom_static_url_edit_page(course_url: str, custom_static_path: str):
    # TODO render edit page
    return f"Edit page for static path for {course_url}: {custom_static_path}"

