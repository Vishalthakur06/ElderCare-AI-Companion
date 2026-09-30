import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = "auth.login"

    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from app.routes import register_blueprints
    register_blueprints(app)

    from app.translations import get_t
    @app.context_processor
    def inject_translations():
        lang = "en"
        if current_user.is_authenticated:
            lang = getattr(current_user, "language", "en") or "en"
        return {"t": get_t(lang), "lang": lang}

    @app.errorhandler(404)
    def not_found(e): return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e): return render_template("errors/500.html"), 500

    with app.app_context():
        db.create_all()

    return app
