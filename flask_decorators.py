from functools import wraps

from flask import g, redirect, render_template

from flask_helpers import get_user_from_session
from flask_repository_getters import get_course_repository
from models.course_enrollment import Role


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
            return f(*args, **kwargs)
        return decorated_function
    return decorator

