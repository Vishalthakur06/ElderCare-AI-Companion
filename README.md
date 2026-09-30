# ElderCare – AI Companion

Accessible Flask starter application for senior-care coordination: accounts, medicine lists, health logs, appointments, emergency contacts, caregiver sharing preferences and a responsive dashboard.

## Requirements
Python 3.10+ and a modern browser. Voice recognition is browser-dependent. External weather/news and SMS/email providers are not configured by default.

## Windows setup
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```
Open http://127.0.0.1:5000 and register an account. The SQLite database is created automatically in the instance folder.

## Tests
```powershell
pytest
```

## Notes and limitations
- Change `SECRET_KEY` before deployment. Set `FLASK_DEBUG=0` in production and use HTTPS, secure cookies, a production WSGI server and a managed database.
- This starter uses `db.create_all()` for convenient local setup; use Flask-Migrate for schema changes in an evolving deployment.
- Browser notifications and speech APIs depend on browser permissions/support and may not work when the app is closed.
- SOS currently provides saved contacts and `tel:` links. It does not send SMS, email or call emergency services automatically.
- Weather/news integrations, scheduled background reminders, consent invitation workflow, entertainment media, and richer analytics require provider configuration and further implementation before production use.
- Health values are self-reported, not clinically verified. This is not a medical device and does not diagnose or prescribe.
- Do not enter real patient data into a development instance. Review privacy, security and applicable legal requirements before deployment.
