import threading
from datetime import datetime, timezone
from flask import Blueprint, jsonify, render_template, g, current_app, request, redirect, url_for, abort
from webapp import db, matcher, jobs

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


@bp.route("/resumes/new", methods=["GET"])
def new_resume():
    return render_template("resume_new.html")


@bp.route("/resumes/<int:resume_id>", methods=["GET"])
def resume_detail(resume_id):
    conn = get_db()
    resume = db.get_resume(conn, resume_id)
    if resume is None:
        abort(404)
    matches = db.get_matches(conn, resume_id)
    return render_template("resume_detail.html", resume=resume, matches=matches)


def _run_rematch(resume_id: int, resume_file_path: str, db_path: str) -> None:
    conn = db.get_connection(db_path)
    try:
        results = matcher.run_embed_match(resume_file_path)
        for result in results:
            job_file = result["job_file"]
            score = result["score"]
            job_info = jobs.parse_job_file(job_file)
            site = jobs.site_name_for(job_file)
            computed_at = datetime.now(timezone.utc).isoformat()
            db.upsert_match(
                conn,
                resume_id=resume_id,
                job_file=job_file,
                title=job_info.get("title"),
                site=site,
                location=job_info.get("location"),
                workplace=job_info.get("workplace"),
                source_url=job_info.get("source"),
                score=score,
                computed_at=computed_at,
                job_posted=None,
            )
    finally:
        db.set_rematch_running(conn, resume_id, False)
        conn.close()


@bp.route("/resumes/<int:resume_id>/rematch", methods=["POST"])
def rematch_resume(resume_id):
    conn = get_db()
    resume = db.get_resume(conn, resume_id)
    if resume is None:
        abort(404)
    db.set_rematch_running(conn, resume_id, True)
    thread = threading.Thread(
        target=_run_rematch,
        args=(resume_id, resume["file_path"], current_app.config["DATABASE"]),
        daemon=True,
    )
    thread.start()
    return redirect(url_for("main.resume_detail", resume_id=resume_id))


@bp.route("/resumes/<int:resume_id>/rematch-status", methods=["GET"])
def rematch_status(resume_id):
    conn = get_db()
    resume = db.get_resume(conn, resume_id)
    if resume is None:
        abort(404)
    return jsonify({"running": bool(resume["rematch_running"])})


@bp.route("/resumes/<int:resume_id>/edit", methods=["GET"])
def edit_resume_get(resume_id):
    conn = get_db()
    resume = db.get_resume(conn, resume_id)
    if resume is None:
        abort(404)
    return render_template("resume_edit.html", resume=resume)


@bp.route("/resumes/<int:resume_id>/edit", methods=["POST"])
def edit_resume_post(resume_id):
    conn = get_db()
    resume = db.get_resume(conn, resume_id)
    if resume is None:
        abort(404)
    name = request.form["name"]
    content = request.form["content"]
    db.update_resume(conn, resume_id, name, content)
    return redirect(url_for("main.resume_detail", resume_id=resume_id))


@bp.route("/resumes/<int:resume_id>/delete", methods=["POST"])
def delete_resume(resume_id):
    conn = get_db()
    resume = db.get_resume(conn, resume_id)
    if resume is None:
        abort(404)
    db.delete_resume(conn, resume_id)
    return redirect(url_for("main.resume_list"))


@bp.route("/resumes", methods=["POST"])
def register_resume_route():
    name = request.form["name"]
    content = request.form["content"]
    conn = get_db()
    db.create_resume(conn, current_app.config["RESUMES_DIR"], name, content)
    return redirect(url_for("main.resume_list"))
