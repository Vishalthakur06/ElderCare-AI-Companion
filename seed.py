from dotenv import load_dotenv
load_dotenv()

from app import create_app, db
from app.models import User, Medicine, HealthRecord, Appointment, EmergencyContact
from datetime import datetime, timedelta

app = create_app()

def seed():
    with app.app_context():
        # Clear existing demo data
        for email in ["demo@eldercare.com", "caregiver@eldercare.com"]:
            u = User.query.filter_by(email=email).first()
            if u:
                Medicine.query.filter_by(user_id=u.id).delete()
                HealthRecord.query.filter_by(user_id=u.id).delete()
                Appointment.query.filter_by(user_id=u.id).delete()
                EmergencyContact.query.filter_by(user_id=u.id).delete()
                db.session.delete(u)
        db.session.commit()

        # --- Users ---
        elder = User(name="Ramesh Sharma", email="demo@eldercare.com", role="elder", language="en")
        elder.set_password("demo1234")

        caregiver = User(name="Priya Sharma", email="caregiver@eldercare.com", role="caregiver", language="en")
        caregiver.set_password("care1234")

        db.session.add_all([elder, caregiver])
        db.session.flush()  # get IDs before commit

        # Link elder to caregiver
        elder.caregiver_id = caregiver.id
        elder.share_health = True
        elder.share_medicines = True

        # --- Medicines ---
        today = datetime.today()
        medicines = [
            Medicine(user_id=elder.id, name="Metformin", dosage="500mg",
                     times="08:00,20:00", instructions="Take with meals",
                     start_date=(today - timedelta(days=60)).strftime("%Y-%m-%d"),
                     end_date=(today + timedelta(days=30)).strftime("%Y-%m-%d")),
            Medicine(user_id=elder.id, name="Amlodipine", dosage="5mg",
                     times="09:00", instructions="Take with water",
                     start_date=(today - timedelta(days=90)).strftime("%Y-%m-%d"),
                     end_date=(today + timedelta(days=5)).strftime("%Y-%m-%d")),  # near expiry
            Medicine(user_id=elder.id, name="Atorvastatin", dosage="10mg",
                     times="21:00", instructions="Take at night",
                     start_date=(today - timedelta(days=30)).strftime("%Y-%m-%d"),
                     end_date=(today + timedelta(days=60)).strftime("%Y-%m-%d")),
            Medicine(user_id=elder.id, name="Aspirin", dosage="75mg",
                     times="08:00", instructions="Take after breakfast",
                     start_date=(today - timedelta(days=120)).strftime("%Y-%m-%d"),
                     end_date=(today - timedelta(days=2)).strftime("%Y-%m-%d")),  # expired
            Medicine(user_id=elder.id, name="Vitamin D3", dosage="1000 IU",
                     times="10:00", instructions="Take with milk",
                     start_date=(today - timedelta(days=15)).strftime("%Y-%m-%d"),
                     end_date=(today + timedelta(days=75)).strftime("%Y-%m-%d")),
        ]
        db.session.add_all(medicines)

        # --- Health Records (last 14 days) ---
        records = []
        bp_values = [
            "128/82", "132/85", "125/80", "130/84", "127/81",
            "135/88", "122/78", "129/83", "131/86", "126/80",
            "133/87", "124/79", "128/82", "130/85"
        ]
        sugar_values = [108, 115, 102, 120, 110, 118, 105, 112, 122, 108, 116, 103, 111, 119]
        pulse_values = [72, 75, 70, 78, 74, 76, 71, 73, 77, 72, 75, 69, 74, 76]
        weight_values = [74.5, 74.3, 74.6, 74.4, 74.2, 74.5, 74.3, 74.1, 74.4, 74.2, 74.0, 74.3, 74.1, 74.2]

        for i in range(14):
            day = today - timedelta(days=13 - i)
            records += [
                HealthRecord(user_id=elder.id, kind="bp", value=bp_values[i],
                             notes="Morning reading", recorded_at=day.replace(hour=8, minute=0)),
                HealthRecord(user_id=elder.id, kind="sugar", value=str(sugar_values[i]),
                             notes="Fasting", recorded_at=day.replace(hour=7, minute=30)),
                HealthRecord(user_id=elder.id, kind="pulse", value=str(pulse_values[i]),
                             notes="", recorded_at=day.replace(hour=8, minute=5)),
                HealthRecord(user_id=elder.id, kind="weight", value=str(weight_values[i]),
                             notes="", recorded_at=day.replace(hour=9, minute=0)),
            ]
        db.session.add_all(records)

        # --- Appointments ---
        appointments = [
            Appointment(user_id=elder.id, doctor="Dr. Anil Mehta",
                        clinic="City Heart Clinic, Pune",
                        when=(today + timedelta(days=3)).strftime("%Y-%m-%dT10:30"),
                        purpose="chest pain follow-up",
                        notes="Bring ECG reports"),
            Appointment(user_id=elder.id, doctor="Dr. Sunita Rao",
                        clinic="Diabetes Care Centre, Pune",
                        when=(today + timedelta(days=12)).strftime("%Y-%m-%dT11:00"),
                        purpose="routine diabetes checkup",
                        notes="Fasting blood test required"),
            Appointment(user_id=elder.id, doctor="Dr. Vikram Joshi",
                        clinic="Orthopedic Plus, Pune",
                        when=(today + timedelta(days=25)).strftime("%Y-%m-%dT15:00"),
                        purpose="knee pain review",
                        notes="X-ray done last month"),
            Appointment(user_id=elder.id, doctor="Dr. Meena Kulkarni",
                        clinic="Eye Care Hospital, Pune",
                        when=(today + timedelta(days=40)).strftime("%Y-%m-%dT09:30"),
                        purpose="annual eye checkup",
                        notes=""),
        ]
        db.session.add_all(appointments)

        # --- Emergency Contacts ---
        contacts = [
            EmergencyContact(user_id=elder.id, name="Priya Sharma",
                             phone="+91-98765-43210", relation="Daughter"),
            EmergencyContact(user_id=elder.id, name="Rahul Sharma",
                             phone="+91-87654-32109", relation="Son"),
            EmergencyContact(user_id=elder.id, name="Dr. Anil Mehta",
                             phone="+91-76543-21098", relation="Family Doctor"),
        ]
        db.session.add_all(contacts)

        db.session.commit()
        print("[OK] Seed complete!")
        print("   Elder login    -> demo@eldercare.com / demo1234")
        print("   Caregiver login -> caregiver@eldercare.com / care1234")

if __name__ == "__main__":
    seed()
