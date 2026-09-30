from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_required,current_user
from app import db
from app.models import Appointment
bp=Blueprint("appointments",__name__,url_prefix="/appointments")
@bp.route("/",methods=["GET","POST"])
@login_required
def index():
    if request.method=="POST":
        doctor=request.form.get("doctor","").strip(); when=request.form.get("when","")
        if doctor and when: db.session.add(Appointment(user_id=current_user.id,doctor=doctor,clinic=request.form.get("clinic",""),when=when,purpose=request.form.get("purpose",""),notes=request.form.get("notes",""))); db.session.commit(); flash("Appointment saved.")
        else: flash("Doctor and date/time are required.","error")
        return redirect(url_for("appointments.index"))
    return render_template("appointments.html",items=Appointment.query.filter_by(user_id=current_user.id).order_by(Appointment.when).all())
@bp.post("/<int:item_id>/delete")
@login_required
def delete(item_id):
    x=Appointment.query.filter_by(id=item_id,user_id=current_user.id).first_or_404(); db.session.delete(x); db.session.commit(); return redirect(url_for("appointments.index"))
