from functools import wraps

from flask import g, redirect, render_template

from flask_helpers import get_user_from_session
from flask_repository_getters import get_course_repository


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

def requires_course(routing_argument_key: str):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if routing_argument_key not in kwargs:
                raise ValueError(f"key {routing_argument_key} must be provided as Flask routing argument")

            course_repo = get_course_repository()
            course = course_repo.get_course_by_starting_url_if_exists("/" + kwargs[routing_argument_key])
            if not course:
                return render_template("404.html"), 404

            g.course = course
            return f(*args, **kwargs)
        return decorated_function
    return decorator


