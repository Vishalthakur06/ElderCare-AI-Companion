from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_required,current_user
from app import db
from app.models import HealthRecord
bp=Blueprint("health",__name__,url_prefix="/health")
@bp.route("/",methods=["GET","POST"])
@login_required
def index():
    if request.method=="POST":
        kind=request.form.get("kind",""); value=request.form.get("value","").strip()
        if kind and value:
            db.session.add(HealthRecord(user_id=current_user.id,kind=kind,value=value,notes=request.form.get("notes",""))); db.session.commit(); flash("Health entry saved.")
        else: flash("Choose a measurement and enter a value.","error")
        return redirect(url_for("health.index"))
    return render_template("health.html",items=HealthRecord.query.filter_by(user_id=current_user.id).order_by(HealthRecord.recorded_at.desc()).all())
@bp.post("/<int:item_id>/delete")
@login_required
def delete(item_id):
    x=HealthRecord.query.filter_by(id=item_id,user_id=current_user.id).first_or_404(); db.session.delete(x); db.session.commit(); return redirect(url_for("health.index"))
