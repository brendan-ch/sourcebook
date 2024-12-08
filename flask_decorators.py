from functools import wraps

from flask import g, redirect, render_template

from flask_helpers import get_user_from_session
from flask_repository_getters import get_course_repository, get_content_repository
from models.course_enrollment import Role
from models.page import VisibilitySetting


def requires_login(should_redirect: bool):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user" not in g or g.user is None:
                user = get_user_from_session()
                if user is None and should_redirect:
                    return redirect("/sign-in")
                elif user is None:
                    return render_template("401.html"), 401

                g.user = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def requires_course_enrollment(course_url_routing_arg_key: str, required_role: Role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if course_url_routing_arg_key not in kwargs:
                raise ValueError(f"key {course_url_routing_arg_key} must be provided as Flask routing argument")

            course_repo = get_course_repository()
            course = course_repo.get_course_by_starting_url_if_exists("/" + kwargs[course_url_routing_arg_key])
            if not course:
                return render_template("404.html"), 404

            role = course_repo.get_user_role_in_class_if_exists(g.user.user_id, course.course_id)
            if not role:
                return render_template(
                    "401.html",
                    custom_error_message="You need to be enrolled in this class to see it."
                ), 401
            elif role.value < required_role.value:
                return render_template(
                    "401.html",
                    custom_error_message="You need a higher role to use this endpoint."
                ), 401

            g.course = course
            g.role = role

            content_repository = get_content_repository()
            g.nav_links = content_repository.generate_listed_page_navigation_link_tree_for_course_id(g.course.course_id)

            return f(*args, **kwargs)
        return decorated_function
    return decorator

def requires_course_page(custom_path_routing_arg_key: str, custom_path_is_required = False):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if custom_path_routing_arg_key not in kwargs and custom_path_is_required:
                raise ValueError(f"key {custom_path_routing_arg_key} must be provided as Flask routing argument")
            elif custom_path_routing_arg_key not in kwargs:
                url_path = "/"
            else:
                url_path = "/" + kwargs[custom_path_routing_arg_key]

            content_repo = get_content_repository()

            page = content_repo.get_page_by_url_and_course_id_if_exists(course_id=g.course.course_id, url_path=url_path)
            if not page:
                return render_template(
                    "course_static_page.html",
                    course=g.course,
                    user=g.user,
                    role=g.role,
                    page_navigation_links=g.nav_links,
                    page_html_content="<p>This page does not exist within the course.</p>"
                ), 404
            elif page.page_visibility_setting == VisibilitySetting.HIDDEN \
                and g.role == Role.STUDENT:
                return render_template(
                    "course_static_page.html",
                    course=g.course,
                    user=g.user,
                    role=g.role,
                    page_navigation_links=g.nav_links,
                    page_html_content="<p>This page is hidden.</p>"
                ), 401

            g.page = page
            return f(*args, **kwargs)
        return decorated_function
    return decorator

