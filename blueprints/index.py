from flask import Blueprint, render_template, request, session, redirect, flash

from flask_repository_getters import get_user_repository, get_course_repository

index_bp = Blueprint("index", __name__)

@index_bp.route("/")
def your_classes_page():
    if "user_id" not in session:
        return redirect("/sign-in")

    user_id = session["user_id"]

    user_repository = get_user_repository()
    user = user_repository.get_user_from_id_if_exists(user_id)
    if not user:
        return redirect("/sign-out")

    course_repository = get_course_repository()
    course_terms_with_courses = course_repository.get_course_terms_with_courses_for_user_id(user_id)

    return render_template(
        "your_classes.html",
        course_terms_with_courses=course_terms_with_courses,
        current_user=user,
    )

@index_bp.route("/sign-in", methods=["GET", "POST"])
def sign_in_page():
    if request.method == "GET":
        if "user_id" in session:
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

        session["user_id"] = user_id
        return redirect("/")

@index_bp.route("/sign-out", methods=["GET"])
def sign_out_page():
    if "user_id" in session:
        session.pop("user_id")

    return redirect("/")
