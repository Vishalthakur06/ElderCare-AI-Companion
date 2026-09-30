from flask import Blueprint,render_template,request,redirect,url_for,flash
from flask_login import login_user,logout_user,current_user
from app import db
from app.models import User
bp=Blueprint("auth",__name__)
@bp.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        name=request.form.get("name","").strip(); email=request.form.get("email","").strip().lower(); password=request.form.get("password","")
        if not name or "@" not in email or len(password)<8: flash("Enter a name, valid email and password (8+ characters).","error")
        elif User.query.filter_by(email=email).first(): flash("That email is already registered.","error")
        else:
            u=User(name=name,email=email,role=request.form.get("role","elder")); u.set_password(password); db.session.add(u); db.session.commit(); login_user(u); return redirect(url_for("dashboard.home"))
    return render_template("register.html")
@bp.route("/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=User.query.filter_by(email=request.form.get("email","").lower().strip()).first()
        if u and u.check_password(request.form.get("password","")): login_user(u); return redirect(url_for("dashboard.home"))
        flash("Email or password was not recognized.","error")
    return render_template("login.html")
@bp.route("/logout",methods=["POST"])
def logout(): logout_user(); return redirect(url_for("auth.login"))
