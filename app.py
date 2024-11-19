from flask import Flask

from blueprints.index import index_bp
from config import FLASK_APP_SECRET_KEY


def create_app():
    app = Flask(__name__)
    app.secret_key = FLASK_APP_SECRET_KEY
    app.register_blueprint(index_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run()
