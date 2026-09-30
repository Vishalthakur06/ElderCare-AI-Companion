from app import create_app,db
import pytest
@pytest.fixture
def client(tmp_path):
    app=create_app(); app.config.update(TESTING=True,SQLALCHEMY_DATABASE_URI="sqlite:///"+str(tmp_path/"test.db"),WTF_CSRF_ENABLED=False)
    with app.app_context(): db.drop_all(); db.create_all()
    return app.test_client()
def test_register_and_login(client):
    r=client.post("/register",data={"name":"Demo","email":"demo@example.com","password":"securepass123","role":"elder"},follow_redirects=True)
    assert r.status_code==200
    r=client.post("/logout",follow_redirects=True)
    assert r.status_code==200
    r=client.post("/login",data={"email":"demo@example.com","password":"securepass123"},follow_redirects=True)
    assert r.status_code==200
