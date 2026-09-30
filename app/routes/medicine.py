from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_required,current_user
from app import db
from app.models import Medicine
bp=Blueprint("medicine",__name__,url_prefix="/medicines")
@bp.route("/",methods=["GET","POST"])
@login_required
def index():
    if request.method=="POST":
        name=request.form.get("name","").strip()
        if name:
            db.session.add(Medicine(user_id=current_user.id,name=name,dosage=request.form.get("dosage",""),times=request.form.get("times","09:00"),instructions=request.form.get("instructions",""),start_date=request.form.get("start_date",""),end_date=request.form.get("end_date",""))); db.session.commit(); flash("Medicine saved.")
        else: flash("Medicine name is required.","error")
        return redirect(url_for("medicine.index"))
    return render_template("medicines.html",items=Medicine.query.filter_by(user_id=current_user.id).all())
@bp.post("/<int:item_id>/delete")
@login_required
def delete(item_id):
    x=Medicine.query.filter_by(id=item_id,user_id=current_user.id).first_or_404(); db.session.delete(x); db.session.commit(); flash("Medicine removed."); return redirect(url_for("medicine.index"))
