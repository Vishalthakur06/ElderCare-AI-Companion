from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import HealthRecord, Medicine, Appointment
from app.services.ai_service import (
    analyze_health, check_interactions, chat_response,
    compute_health_score, analyze_trends,
    check_refill_alerts, predict_appointment_priority
)

bp = Blueprint("ai", __name__, url_prefix="/ai")


@bp.route("/")
@login_required
def index():
    records      = HealthRecord.query.filter_by(user_id=current_user.id).order_by(HealthRecord.recorded_at.desc()).all()
    medicines    = Medicine.query.filter_by(user_id=current_user.id).all()
    appointments = Appointment.query.filter_by(user_id=current_user.id).all()

    # Latest record per kind for risk analysis
    analyses, seen = [], set()
    for r in records:
        if r.kind not in seen:
            seen.add(r.kind)
            result = analyze_health(r.kind, r.value)
            analyses.append({"kind": r.kind, "value": r.value,
                             "date": r.recorded_at.strftime("%d %b %Y"), **result})

    health_score  = compute_health_score(records)
    trends        = analyze_trends(records)
    interactions  = check_interactions([m.name for m in medicines])
    refill_alerts = check_refill_alerts(medicines)
    appt_priority = predict_appointment_priority(appointments)

    # Build chart data per vital kind
    chart_data = {}
    for kind, t in trends.items():
        chart_data[kind] = {"labels": t["labels"], "data": t["data_points"], "trend": t["trend"]}

    return render_template("ai.html",
        analyses      = analyses,
        health_score  = health_score,
        trends        = trends,
        chart_data    = chart_data,
        interactions  = interactions,
        refill_alerts = refill_alerts,
        appt_priority = appt_priority,
        medicines     = medicines,
    )


@bp.post("/chat")
@login_required
def chat():
    data = request.get_json(silent=True) or {}
    msg  = data.get("message", "").strip()
    if not msg:
        return jsonify({"response": "Please type a message."}), 400
    return jsonify({"response": chat_response(msg)})


@bp.get("/analyze")
@login_required
def analyze():
    kind  = request.args.get("kind", "")
    value = request.args.get("value", "")
    if not kind or not value:
        return jsonify({"error": "kind and value required"}), 400
    return jsonify(analyze_health(kind, value))
