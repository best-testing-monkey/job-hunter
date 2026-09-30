from flask import Blueprint, jsonify, render_template

bp = Blueprint("main", __name__)


@bp.route("/health", methods=["GET"])
def health() -> dict:
    return jsonify({"status": "ok"})


@bp.route("/theme-preview", methods=["GET"])
def theme_preview():
    return render_template("theme_preview.html")
