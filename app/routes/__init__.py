def register_blueprints(app):
    from .auth import bp as auth
    from .dashboard import bp as dashboard
    from .medicine import bp as medicine
    from .health import bp as health
    from .appointments import bp as appointments
    from .emergency import bp as emergency
    from .caregiver import bp as caregiver
    from .settings import bp as settings
    for b in (auth,dashboard,medicine,health,appointments,emergency,caregiver,settings): app.register_blueprint(b)
