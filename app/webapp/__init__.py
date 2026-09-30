import os
from flask import Flask
from webapp.routes import bp


def create_app() -> Flask:
    app = Flask(__name__)
    os.makedirs(app.instance_path, exist_ok=True)
    app.config["DATABASE"] = os.path.join(app.instance_path, "matches.db")
    app.config["RESUMES_DIR"] = os.path.join(app.instance_path, "resumes")
    app.register_blueprint(bp)
    return app
