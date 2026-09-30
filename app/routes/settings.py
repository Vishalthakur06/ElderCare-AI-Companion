from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_required,current_user
from app import db
bp=Blueprint("settings",__name__)
@bp.route("/settings",methods=["GET","POST"])
@login_required
def index():
    if request.method=="POST":
        current_user.language=request.form.get("language","en")
        current_user.share_health=bool(request.form.get("share_health"))
        current_user.share_medicines=bool(request.form.get("share_medicines"))
        db.session.commit(); flash("Settings updated."); return redirect(url_for("settings.index"))
    return render_template("settings.html")
