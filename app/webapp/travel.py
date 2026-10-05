"""Travel-time annotation/filtering of match rows, backed by resume-matcher/geo.py."""
import sys
from pathlib import Path

_RESUME_MATCHER_DIR = Path(__file__).resolve().parents[2] / "resume-matcher"
if str(_RESUME_MATCHER_DIR) not in sys.path:
    sys.path.insert(0, str(_RESUME_MATCHER_DIR))
import geo  # noqa: E402


def apply_travel(resume, matches, enabled: bool = True):
    """Return (rows, hidden_count, warning).

    rows: list of (match, info) where info has travel_minutes, travel_status,
    travel_flag (display text or None). Filtering is active only when the
    resume has home_city and max_travel_minutes and `enabled` is True.
    """
    home = (resume["home_city"] or "").strip()
    max_min = resume["max_travel_minutes"]
    mode = resume["travel_mode"] or "car"
    configured = bool(home) and max_min is not None
    warning = None
    if not home:
        return [(m, None) for m in matches], 0, None
    if mode not in ("car", "transit"):
        mode = "car"
    try:
        home_ok = geo.resolve_location(home) is not None
    except Exception:
        home_ok = False
    if not home_ok:
        warning = f"Home city '{home}' could not be resolved; travel filtering is off."
        return [(m, None) for m in matches], 0, warning

    rows, hidden = [], 0
    for m in matches:
        try:
            res = geo.travel_time(home, m["location"], m["workplace"], mode)
        except ValueError:
            rows.append((m, None))
            continue
        if configured and enabled and not geo.within_limit(res, max_min):
            hidden += 1
            continue
        if res.status == "ok":
            label = f"{res.minutes} min"
        elif res.status == "remote":
            label = "Remote"
        elif res.status == "unknown":
            label = "Unknown location"
        else:
            label = "Too far"
        rows.append((m, {"minutes": res.minutes, "status": res.status, "label": label}))
    return rows, hidden, warning
