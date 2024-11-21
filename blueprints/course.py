from flask import Blueprint, render_template

course_bp = Blueprint("course", __name__)

@course_bp.route("/<string:course_url>/", methods=["GET"])
def course_home_page(course_url: str):
    return render_template("course_static_page.html")

@course_bp.route("/<string:course_url>/<path:custom_static_path>/", methods=["GET"])
def course_custom_static_url_page(course_url: str, custom_static_path: str):
    # TODO render static page
    return f"Custom static path for {course_url}: {custom_static_path}"

@course_bp.route("/<string:course_url>/<path:custom_static_path>/edit/", methods=["GET", "POST"])
def course_custom_static_url_edit_page(course_url: str, custom_static_path: str):
    # TODO render edit page
    return f"Edit page for static path for {course_url}: {custom_static_path}"

