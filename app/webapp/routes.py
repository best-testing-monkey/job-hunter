from flask import Blueprint, jsonify

bp = Blueprint("main", __name__)


@bp.route("/health", methods=["GET"])
def health() -> dict:
    return jsonify({"status": "ok"})
