from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
class User(UserMixin, db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100), nullable=False)
    email=db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash=db.Column(db.String(256), nullable=False)
    role=db.Column(db.String(20), default="elder", nullable=False)
    language=db.Column(db.String(10), default="en")
    caregiver_id=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    share_health=db.Column(db.Boolean, default=False)
    share_medicines=db.Column(db.Boolean, default=False)
    def set_password(self,p): self.password_hash=generate_password_hash(p)
    def check_password(self,p): return check_password_hash(self.password_hash,p)
class Medicine(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False,index=True)
    name=db.Column(db.String(120),nullable=False); dosage=db.Column(db.String(80),default="")
    times=db.Column(db.String(200),default="09:00"); instructions=db.Column(db.String(300),default="")
    start_date=db.Column(db.String(10),default=""); end_date=db.Column(db.String(10),default="")
    created_at=db.Column(db.DateTime,default=datetime.utcnow)
class HealthRecord(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False,index=True)
    kind=db.Column(db.String(30),nullable=False); value=db.Column(db.String(100),nullable=False)
    notes=db.Column(db.String(500),default=""); recorded_at=db.Column(db.DateTime,default=datetime.utcnow)
class Appointment(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False,index=True)
    doctor=db.Column(db.String(120),nullable=False); clinic=db.Column(db.String(160),default="")
    when=db.Column(db.String(30),nullable=False); purpose=db.Column(db.String(300),default="")
    notes=db.Column(db.String(500),default="")
class EmergencyContact(db.Model):
    id=db.Column(db.Integer,primary_key=True); user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False,index=True)
    name=db.Column(db.String(100),nullable=False); phone=db.Column(db.String(30),nullable=False); relation=db.Column(db.String(60),default="")
