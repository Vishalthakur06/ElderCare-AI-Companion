def register_blueprints(app):
    from .auth import bp as auth
    from .dashboard import bp as dashboard
    from .medicine import bp as medicine
    from .health import bp as health
    from .appointments import bp as appointments
    from .emergency import bp as emergency
    from .caregiver import bp as caregiver
    from .settings import bp as settings
    from .ai import bp as ai
    for b in (auth,dashboard,medicine,health,appointments,emergency,caregiver,settings,ai): app.register_blueprint(b)
