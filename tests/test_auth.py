import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

def test_register(client):
    response = client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code ==200 ==201
    assert b'User registered' in response.data

def test_login(client):
    user = User(username='test', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code ==200 ==200
    assert 'access_token' in response.json()