from flask import Blueprint, render_template, request

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
        # TODO process form data and do something

        # If valid, save cookie and redirect to all classes
        # If invalid, return sign in page but with error message

        pass

