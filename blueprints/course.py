import re
import urllib.parse
from dataclasses import asdict
from typing import Optional

import markdown2
from bs4 import BeautifulSoup
from flask import Blueprint, render_template, session, abort, request, redirect, current_app, flash, g

from custom_exceptions import AlreadyExistsException, NotFoundException, InvalidPathException
from flask_decorators import requires_login, requires_course_enrollment, requires_course_page
from flask_repository_getters import get_content_repository, get_attendance_repository
from models import course
from models.attendance_record import AttendanceRecord
from models.course import Course
from models.course_enrollment import Role
from models.page import Page

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

@course_bp.route("/<string:course_url>/new/", methods=["GET", "POST"])
@requires_login(should_redirect=False)
@requires_course_enrollment(course_url_routing_arg_key="course_url", required_role=Role.ASSISTANT)
def course_create_new_page(course_url: str):
    user = g.user
    course = g.course
    role = g.role
    nav_links = g.nav_links

    def render_new_page_template_with_optional_error(error: Optional[str] = None):
        return render_template(
            "course_edit_page.html",
            user=user,
            role=role,
            course=course,
            discard_navigates_to=f"{course.starting_url_path}",
            page_navigation_links=nav_links,
            error=error
        )

    if request.method == "GET":
        return render_new_page_template_with_optional_error()
    else:
        page_dictionary = dict(request.form)

        try:
            page_to_insert = Page(**page_dictionary)
            content_repo = get_content_repository()
            page_to_insert.page_id = content_repo.add_new_page_and_get_id(page_to_insert)

            return redirect(course.starting_url_path + page_to_insert.url_path_after_course_path)

        # TODO create test cases for each error type
        # TODO PLEASE give better error messages, these are super vague right now
        except InvalidPathException as e:
            current_app.logger.exception(e)
            return render_new_page_template_with_optional_error(
                error="Not a valid path, please try again."
            ), 400
        except ValueError as e:
            current_app.logger.exception(e)
            return render_new_page_template_with_optional_error(
                error="Couldn't convert one of the attributes into the correct type, please try again."
            ), 400
        except AlreadyExistsException as e:
            current_app.logger.exception(e)
            return render_new_page_template_with_optional_error(
                error="There is already a page with that path in this course. Please try again with a different path."
            ), 400

        except TypeError as e:
            current_app.logger.exception(e)
            return render_new_page_template_with_optional_error(
                error="There was an issue parsing your response. Please try again later."
            ), 400

@course_bp.route("/<string:course_url>/", methods=["GET"])
@course_bp.route("/<string:course_url>/<path:custom_static_path>/", methods=["GET"])
@requires_login(should_redirect=False)
@requires_course_enrollment(course_url_routing_arg_key="course_url", required_role=Role.STUDENT)
@requires_course_page(custom_path_routing_arg_key="custom_static_path", custom_path_is_required=False)
def course_custom_static_url_page(course_url: str, custom_static_path: Optional[str] = None):
    user = g.user
    course = g.course
    role = g.role
    page = g.page
    page_navigation_links = g.nav_links

    page_html_content = generate_html_from_markdown(page, course)

    return render_template(
        "course_static_page.html",
        role=role,
        course=course,
        page=page,
        user=user,
        page_navigation_links=page_navigation_links,
        page_html_content=page_html_content
    )

@course_bp.route("/<string:course_url>/delete/", methods=["POST"])
@course_bp.route("/<string:course_url>/<path:custom_static_path>/delete/", methods=["POST"])
@requires_login(should_redirect=False)
@requires_course_enrollment(course_url_routing_arg_key="course_url", required_role=Role.ASSISTANT)
@requires_course_page(custom_path_routing_arg_key="custom_static_path", custom_path_is_required=False)
def course_delete_page(course_url: str, custom_static_path: Optional[str] = None):
    user = g.user
    course = g.course
    role = g.role
    page = g.page

    content_repository = get_content_repository()

    if not page:
        return render_template("404.html"), 404

    try:
        content_repository.delete_page_by_id(page.page_id)
        flash(f"Page at {page.url_path_after_course_path} was deleted.")
        return redirect(course.starting_url_path)
    except NotFoundException:
        flash(f"Page was not found. Someone else may have deleted it already.")

        page_html_content = generate_html_from_markdown(page, course)
        return render_template(
            "course_static_page.html",
            course=course,
            page=page,
            user=user,
            role=role,
            page_html_content=page_html_content,
        ), 404

@course_bp.route("/<string:course_url>/edit/", methods=["GET", "POST"])
@course_bp.route("/<string:course_url>/<path:custom_static_path>/edit/", methods=["GET", "POST"])
@requires_login(should_redirect=False)
@requires_course_enrollment(course_url_routing_arg_key="course_url", required_role=Role.ASSISTANT)
@requires_course_page(custom_path_routing_arg_key="custom_static_path", custom_path_is_required=False)
def course_custom_static_url_edit_page(course_url: str, custom_static_path: Optional[str] = None):
    user = g.user
    course = g.course
    page = g.page
    role = g.role
    nav_links = g.nav_links

    def render_edit_template_with_optional_error(error: Optional[str] = None):
        return render_template(
            "course_edit_page.html",
            submit_path=course.starting_url_path + page.url_path_after_course_path + "/edit",
            user=user,
            role=role,
            course=course,
            error=error,
            discard_navigates_to=f"{course.starting_url_path}{page.url_path_after_course_path}",
            page_navigation_links=nav_links,
            **asdict(page)
        )

    if request.method == "GET":
        return render_edit_template_with_optional_error(), 200
    elif request.method == "POST":
        page_dictionary = dict(request.form)

        try:
            page_to_update = Page(**page_dictionary)
            if not page_to_update.page_id:
                return render_edit_template_with_optional_error(
                    error="Page ID not provided.",
                ), 400

            content_repo = get_content_repository()
            content_repo.update_page_by_id(page_to_update)

            return redirect(course.starting_url_path + page_to_update.url_path_after_course_path)

        # TODO create test cases for each error type
        # TODO PLEASE give better error messages, these are super vague right now
        except InvalidPathException as e:
            current_app.logger.exception(e)
            return render_edit_template_with_optional_error(
                error="Not a valid path, please try again"
            ), 400
        except NotFoundException as e:
            current_app.logger.exception(e)
            return render_edit_template_with_optional_error(
                "Couldn't find the page. It may have been moved or deleted by another user."
            ), 404
        except ValueError as e:
            current_app.logger.exception(e)
            return render_edit_template_with_optional_error(
                error="Couldn't convert one of the attributes into the correct type."
            ), 400
        except AlreadyExistsException as e:
            current_app.logger.exception(e)
            return render_edit_template_with_optional_error(
                error="There is already a page with that URL in this course. Please try again with a different URL."
            ), 400
        except TypeError as e:
            current_app.logger.exception(e)
            return render_edit_template_with_optional_error(
                error="There was an issue parsing your response. Please try again later."
            ), 400

@course_bp.route("/<string:course_url>/attendance/", methods=["GET"])
@requires_login(should_redirect=False)
@requires_course_enrollment(course_url_routing_arg_key="course_url", required_role=Role.ASSISTANT)
def course_attendance_session_list_page(course_url: str):
    user = g.user
    course = g.course
    role = g.role
    nav_links = g.nav_links

    attendance_repo = get_attendance_repository()

    active_sessions = attendance_repo.get_active_attendance_sessions_from_course_id(course.course_id)
    closed_sessions = attendance_repo.get_closed_attendance_sessions_from_course_id(course.course_id)

    return render_template(
        "course_attendance_sessions_list.html",
        course=course,
        user=user,
        role=role,
        page_navigation_links=nav_links,
        active_sessions=active_sessions,
        closed_sessions=closed_sessions,
    )

# TODO return a form where user can fill out optional title and options
@course_bp.route("/<string:course_url>/attendance/new/", methods=["POST"])
@requires_login(should_redirect=False)
@requires_course_enrollment(course_url_routing_arg_key="course_url", required_role=Role.ASSISTANT)
def course_attendance_session_new_session(course_url: str):
    user = g.user
    course = g.course
    role = g.role

    attendance_repo = get_attendance_repository()
    try:
        session_id = attendance_repo.start_new_attendance_session_and_get_id(course.course_id)
        return redirect(f"{course.starting_url_path}/attendance/{session_id}")
    except Exception as e:
        current_app.logger.exception(e)
        flash("An unknown error occurred. Please try again later.")
        return redirect(f"{course.starting_url_path}/attendance")

@course_bp.route("/<string:course_url>/attendance/<int:attendance_session_id>/", methods=["GET"])
@requires_login(should_redirect=False)
@requires_course_enrollment(course_url_routing_arg_key="course_url", required_role=Role.ASSISTANT)
def course_attendance_student_list(course_url: str, attendance_session_id: int):
    # TODO later, show a static page without editing capabilities
    course = g.course
    return redirect(f"{course.starting_url_path}/attendance/{attendance_session_id}/edit")

@course_bp.route("/<string:course_url>/attendance/<int:attendance_session_id>/edit/", methods=["GET", "POST"])
@requires_login(should_redirect=False)
@requires_course_enrollment(course_url_routing_arg_key="course_url", required_role=Role.ASSISTANT)
def course_attendance_student_list_edit(course_url: str, attendance_session_id: int):
    user = g.user
    course = g.course
    role = g.role
    nav_links = g.nav_links

    attendance_repo = get_attendance_repository()
    attendance_records = attendance_repo.get_student_attendance_records_with_names_from_session_id(attendance_session_id)

    def render_attendance_student_list():
        return render_template(
            "course_attendance_students_list.html",
            course=course,
            user=user,
            role=role,
            attendance_records=attendance_records,
            attendance_session_id=attendance_session_id,
            page_navigation_links=nav_links,
        )

    if request.method == "GET":
        return render_attendance_student_list()
    elif request.method == "POST":
        attendance_record_dictionary = dict(request.form)
        try:
            for key in attendance_record_dictionary:
                # noinspection PyTypeChecker
                constructed_attendance_record = AttendanceRecord(
                    user_id=key,
                    attendance_session_id=attendance_session_id,
                    attendance_status=attendance_record_dictionary[key],
                )

                attendance_repo.update_status_by_attendance_session_and_user_id(
                    constructed_attendance_record,
                )

            flash("Changes have been saved.")
            return redirect(f"{course.starting_url_path}/attendance/{attendance_session_id}")
        except ValueError as e:
            current_app.logger.exception(e)
            flash("Couldn't convert one of the attributes to the correct value, please try again.")
            return render_attendance_student_list(), 400
        except NotFoundException as e:
            current_app.logger.exception(e)
            flash("One or more records you submitted no longer exist. Please try again.")
            return render_attendance_student_list(), 404
        except Exception as e:
            current_app.logger.exception(e)
            flash("An unknown error occurred. Please try again later.")
            return render_attendance_student_list(), 500

