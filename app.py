from typing import Optional

from flask import Flask

from blueprints.index import index_bp
from config import FLASK_APP_SECRET_KEY
from db_connection_details import DBConnectionDetails


def create_app(custom_db_config: Optional[DBConnectionDetails] = None):
    app = Flask(__name__)
    app.secret_key = FLASK_APP_SECRET_KEY
    app.register_blueprint(index_bp)

    app.config["DB_CONFIG_OBJECT"] = custom_db_config

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
