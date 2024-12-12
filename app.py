import sys
from typing import Optional

from flask import Flask

from blueprints.course import course_bp
from blueprints.index import index_bp
from config import FLASK_APP_SECRET_KEY, DATABASE_HOST, DATABASE_SCHEMA_NAME, DATABASE_USER, DATABASE_PASSWORD, \
    DATABASE_PORT
from db_connection_details import DBConnectionDetails


def create_app(is_admin_app = False, custom_db_config: Optional[DBConnectionDetails] = None):
    app = Flask(__name__)
    app.secret_key = FLASK_APP_SECRET_KEY

    if not custom_db_config:
        custom_db_config = DBConnectionDetails(
            host=DATABASE_HOST,
            database=DATABASE_SCHEMA_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            port=DATABASE_PORT
        )

    # TODO register a different set of blueprints for admins
    app.register_blueprint(index_bp)
    app.register_blueprint(course_bp)

    app.config["DB_CONFIG_OBJECT"] = custom_db_config

    return app

if __name__ == "__main__":
    if sys.argv[-1] == "--admin":
        print("admin")

    app = create_app()
    app.run()
