import re
import urllib.parse

import markdown2
from bs4 import BeautifulSoup
from flask import Blueprint, render_template, session, abort, request, redirect, current_app

from custom_exceptions import AlreadyExistsException
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

@course_bp.route("/<string:course_url>/new/", methods=["GET", "POST"])
def course_create_new_page(course_url: str):
    user = get_user_from_session()
    course_repo = get_course_repository()

    course = course_repo.get_course_by_starting_url_if_exists("/" + course_url)
    if not course:
        return render_template("404.html"), 404

    role = None
    if user:
        role = course_repo.get_user_role_in_class_if_exists(user.user_id, course.course_id)

    if not role or role == Role.STUDENT:
        return render_template(
            "401.html",
            custom_error_message="You need to be an editor to use this endpoint."
        ), 401

    if request.method == "GET":
        return render_template(
            "course_edit_page.html",
            user=user,
            role=role,
            course=course,
        )
    else:
        page_dictionary = dict(request.form)

        try:
            page_to_insert = Page(**page_dictionary)
            content_repo = get_content_repository()
            page_to_insert.page_id = content_repo.add_new_page_and_get_id(page_to_insert)

            return redirect(course.starting_url_path + page_to_insert.url_path_after_course_path)

        # TODO create test cases for each error type
        # TODO PLEASE give better error messages, these are super vague right now
        except ValueError as e:
            current_app.logger.exception(e)
            return render_template(
                "course_edit_page.html",
                user=user,
                role=role,
                course=course,
                error="Couldn't convert one of the attributes into the correct type."
            ), 400
        except AlreadyExistsException as e:
            current_app.logger.exception(e)
            return render_template(
                "course_edit_page.html",
                user=user,
                role=role,
                course=course,
                error="There is already a page with that URL in this course. Please try again with a different URL."
            ), 400
        except TypeError as e:
            # Something happened when constructing the Page object
            current_app.logger.exception(e)
            return render_template(
                "course_edit_page.html",
                user=user,
                role=role,
                course=course,
                error="There was an issue parsing your response. Please try again later."
            ), 400

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
    user = get_user_from_session()
    course_repo = get_course_repository()

    course = course_repo.get_course_by_starting_url_if_exists("/" + course_url)
    if not course:
        return render_template("404.html"), 404

    role = None
    if user:
        role = course_repo.get_user_role_in_class_if_exists(user.user_id, course.course_id)

    if not role or role == Role.STUDENT:
        return render_template(
            "401.html",
            custom_error_message="You need to be an editor to use this endpoint."
        ), 401

    if request.method == "GET":
        return render_template(
            "course_edit_page.html",
            user=user,
            role=role,
            course=course,
        )

