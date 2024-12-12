from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='')

@admin_bp.route('/')
def admin_options():
    return 'Hello admin!'