from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import Medicine, HealthRecord, Appointment, EmergencyContact
from app.services.weather_service import get_weather, get_news
from datetime import date

bp = Blueprint("dashboard", __name__)

@bp.route("/")
@login_required
def home():
    return render_template(
        "dashboard.html",
        medicines=Medicine.query.filter_by(user_id=current_user.id).order_by(Medicine.name).all(),
        records=HealthRecord.query.filter_by(user_id=current_user.id).order_by(HealthRecord.recorded_at.desc()).limit(4).all(),
        appointments=Appointment.query.filter_by(user_id=current_user.id).all(),
        contacts=EmergencyContact.query.filter_by(user_id=current_user.id).all(),
        today=date.today().isoformat()
    )

@bp.get("/api/daily")
@login_required
def daily_api():
    lat = request.args.get("lat", type=float)
    lon = request.args.get("lon", type=float)
    if lat is None or lon is None:
        return jsonify({"error": "lat/lon required"}), 400
    return jsonify({
        "weather": get_weather(lat, lon),
        "news":    get_news()
    })
