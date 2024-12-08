from functools import wraps

from flask import g, redirect, render_template

from flask_helpers import get_user_from_session

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
