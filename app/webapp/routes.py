from flask import Blueprint, jsonify, render_template, g, current_app, request, redirect, url_for, abort
from webapp import db

bp = Blueprint("main", __name__)


def get_db():
    if "db" not in g:
        g.db = db.get_connection(current_app.config["DATABASE"])
        db.init_db(g.db)
    return g.db


@bp.teardown_app_request
def close_db(error):
    db_conn = g.pop("db", None)
    if db_conn is not None:
        db_conn.close()


@bp.route("/health", methods=["GET"])
def health() -> dict:
    return jsonify({"status": "ok"})


@bp.route("/theme-preview", methods=["GET"])
def theme_preview():
    return render_template("theme_preview.html")


@bp.route("/", methods=["GET"])
def resume_list():
    conn = get_db()
    resumes = db.list_resumes(conn)
    return render_template("resumes.html", resumes=resumes)


@bp.route("/resumes/<int:resume_id>", methods=["GET"])
def resume_detail(resume_id):
    conn = get_db()
    resume = db.get_resume(conn, resume_id)
    if resume is None:
        abort(404)
    matches = db.get_matches(conn, resume_id)
    return render_template("resume_detail.html", resume=resume, matches=matches)


@bp.route("/resumes", methods=["POST"])
def register_resume_route():
    name = request.form["name"]
    file_path = request.form["file_path"]
    conn = get_db()
    db.register_resume(conn, name, file_path)
    return redirect(url_for("main.resume_list"))
