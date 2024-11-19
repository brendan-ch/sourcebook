from flask import Blueprint, render_template

index_bp = Blueprint("index", __name__)

@index_bp.route("/")
def all_classes_page():
    # return render_template("all_classes.html")
    return "All classes page"

@index_bp.route("/sign-in")
def sign_in_page():
    # return render_template("sign_in.html")
    return "Sign in page"
