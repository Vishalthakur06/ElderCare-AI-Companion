from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_required,current_user
from app import db
from app.models import EmergencyContact
bp=Blueprint("emergency",__name__,url_prefix="/emergency")
@bp.route("/",methods=["GET","POST"])
@login_required
def index():
    if request.method=="POST":
        name=request.form.get("name","").strip(); phone=request.form.get("phone","").strip()
        if name and phone: db.session.add(EmergencyContact(user_id=current_user.id,name=name,phone=phone,relation=request.form.get("relation",""))); db.session.commit(); flash("Contact saved.")
        else: flash("Name and phone are required.","error")
        return redirect(url_for("emergency.index"))
    return render_template("emergency.html",items=EmergencyContact.query.filter_by(user_id=current_user.id).all())
@bp.post("/<int:item_id>/delete")
@login_required
def delete(item_id):
    x=EmergencyContact.query.filter_by(id=item_id,user_id=current_user.id).first_or_404(); db.session.delete(x); db.session.commit(); return redirect(url_for("emergency.index"))
