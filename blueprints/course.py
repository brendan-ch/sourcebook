import re
import urllib.parse

import markdown2
from bs4 import BeautifulSoup
from flask import Blueprint, render_template, session, abort

from flask_helpers import get_user_from_session
from flask_repository_getters import get_course_repository, get_user_repository, get_content_repository
from models.course import Course
from models.course_enrollment import Role
from models.page import VisibilitySetting, Page
from models.user import User

course_bp = Blueprint("course", __name__)

def generate_html_from_markdown(page: Page, course: Course):
    page_html_content = markdown2.markdown(page.page_content)

    soup = BeautifulSoup(page_html_content, "html.parser")
    all_relative_links = soup.find_all("a", href=re.compile("^/"))
    for relative_link in all_relative_links:
        replacement = soup.new_tag("a", **relative_link.attrs)
        replacement.string = relative_link.string
        url_without_beginning_slash = relative_link.attrs["href"][1:]
        replacement.attrs["href"] = urllib.parse.urljoin(course.starting_url_path + "/", url_without_beginning_slash)
        relative_link.replace_with(replacement)

    page_html_content = soup.prettify()
    return page_html_content

def render_static_page_template_based_on_role(course: Course, user: User, page: Page, role: Role):
    if not page:
        return render_template(
            "course_static_page.html",
            course=course,
            user=user,
            role=role,
            page_html_content="<p>This page does not exist within the course.</p>",
        ), 404
    elif page.page_visibility_setting == VisibilitySetting.HIDDEN \
            and role == Role.STUDENT:
        return render_template(
            "course_static_page.html",
            course=course,
            user=user,
            role=role,
            page_html_content="<p>This page is hidden.</p>"
        ), 401

    page_html_content = generate_html_from_markdown(page, course)

    return render_template(
        "course_static_page.html",
        course=course,
        user=user,
        role=role,
        page_html_content=page_html_content,
    )

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

    if not role:
        return render_template(
            "401.html",
            custom_error_message="You need to be enrolled in this course to see it."
        ), 401

    content_repository = get_content_repository()
    page = content_repository.get_page_by_url_and_course_id_if_exists(
        course_id=course.course_id,
        url_path="/"
    )

    return render_static_page_template_based_on_role(
        course=course,
        user=user,
        role=role,
        page=page,
    )

@course_bp.route("/<string:course_url>/<path:custom_static_path>/", methods=["GET"])
def course_custom_static_url_page(course_url: str, custom_static_path: str):
    user = get_user_from_session()
    course_repo = get_course_repository()

    course = course_repo.get_course_by_starting_url_if_exists("/" + course_url)
    if not course:
        return render_template("404.html"), 404

    role = None
    if user:
        role = course_repo.get_user_role_in_class_if_exists(user.user_id, course.course_id)

    if not role:
        return render_template(
            "401.html",
            custom_error_message="You need to be enrolled in this course to see it."
        ), 401

    content_repository = get_content_repository()
    page = content_repository.get_page_by_url_and_course_id_if_exists(
        course_id=course.course_id,
        url_path="/" + custom_static_path
    )

    return render_static_page_template_based_on_role(
        role=role,
        course=course,
        page=page,
        user=user,
    )

@course_bp.route("/<string:course_url>/<path:custom_static_path>/edit/", methods=["GET", "POST"])
def course_custom_static_url_edit_page(course_url: str, custom_static_path: str):
    # TODO render edit page
    return f"Edit page for static path for {course_url}: {custom_static_path}"

