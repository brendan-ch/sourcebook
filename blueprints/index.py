from flask import Blueprint, render_template, request, session, redirect

from flask_repository_getters import get_user_repository

index_bp = Blueprint("index", __name__)

@index_bp.route("/")
def all_classes_page():
    # return render_template("all_classes.html")
    return "All classes page"

@index_bp.route("/sign-in", methods=["GET", "POST"])
def sign_in_page():
    if request.method == "GET":
        return "Sign in page"
        # return render_template("sign_in.html")
    else:
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            # TODO flash message in rendering template
            return "Please fill out all missing fields", 400

        user_repository = get_user_repository()
        user_id = user_repository.get_user_id_if_credentials_match(email, password)

        if not user_id:
            return "Incorrect email or password, please try again", 401

        session["user_id"] = user_id
        return redirect("/")
