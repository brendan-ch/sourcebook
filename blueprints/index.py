from flask import Blueprint, render_template

index_bp = Blueprint("index", __name__)

@index_bp.route("/")
def all_classes_page():
    # return render_template("all-classes.html")
    return "All classes page"
