from dotenv import load_dotenv
load_dotenv()

from app import create_app
app = create_app()

with app.app_context():
    from app.models import User
    if User.query.count() == 0:
        from seed import seed
        seed()

if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False))
