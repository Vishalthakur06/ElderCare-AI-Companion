from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_required,current_user
from app import db
from app.models import User,Medicine,HealthRecord,Appointment
bp=Blueprint("caregiver",__name__,url_prefix="/caregiver")
@bp.route("/",methods=["GET","POST"])
@login_required
def index():
    if current_user.role!="caregiver": flash("Caregiver account required.","error"); return redirect(url_for("dashboard.home"))
    if request.method=="POST":
        elder=User.query.filter_by(email=request.form.get("email","").strip().lower(),role="elder").first()
        if not elder: flash("No elder account found for that email.","error")
        elif elder.id==current_user.id: flash("You cannot link your own account.","error")
        else: elder.caregiver_id=current_user.id; db.session.commit(); flash("Caregiver link requested/created. Ask the elder to review sharing settings.")
        return redirect(url_for("caregiver.index"))
    elders=User.query.filter_by(caregiver_id=current_user.id).all()
    return render_template("caregiver_dashboard.html",elders=elders,Medicine=Medicine,HealthRecord=HealthRecord,Appointment=Appointment)
