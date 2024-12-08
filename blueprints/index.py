from flask import Blueprint, render_template, request, session, redirect, flash, g

from flask_decorators import requires_login
from flask_helpers import get_user_from_session
from flask_repository_getters import get_user_repository, get_course_repository

index_bp = Blueprint("index", __name__)

@index_bp.route("/")
@requires_login(should_redirect=True)
def your_classes_page():
    course_repository = get_course_repository()
    course_terms_with_courses = course_repository.get_course_terms_with_courses_for_user_id(g.user.user_id)

    return render_template(
        "your_classes.html",
        course_terms_with_courses=course_terms_with_courses,
        current_user=g.user,
    )

@index_bp.route("/sign-in", methods=["GET", "POST"])
def sign_in_page():
    if request.method == "GET":
        user = get_user_from_session()
        if user:
            return redirect("/")

        return render_template("sign_in.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            return render_template(
                "sign_in.html",
                error="Please fill out all missing fields."
            ), 400

        user_repository = get_user_repository()
        user_id = user_repository.get_user_id_if_credentials_match(email, password)

        if not user_id:
            return render_template(
                "sign_in.html",
                error="Incorrect email or password, please try again."
            ), 401

        user = user_repository.get_user_from_id_if_exists(user_id)

        session["user_uuid"] = user.user_uuid
        return redirect("/")

@index_bp.route("/sign-out", methods=["GET"])
def sign_out_page():
    if "user_uuid" in session:
        session.pop("user_uuid")

    return redirect("/")
