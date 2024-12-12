from flask import Blueprint, render_template

admin_bp = Blueprint('admin', __name__, url_prefix='')

@admin_bp.route('/')
def admin_options():
    return render_template("admin_options.html")