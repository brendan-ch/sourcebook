from flask import Flask

from blueprints.index import index_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(index_bp)

    return app

app = create_app()

if __name__ == "__main__":
    app.run()
