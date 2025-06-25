import pytest
from app import create_app, db
from app.models import User, Team

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

def test_draft_player(client):
    user = User(username='test', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()

    response = client.post('/team/draft', json={'player_id': 1}, headers={'Authorization': 'Bearer {mock_jwt}'})
    assert response.status_code == 201
    # Note: Requires player and JWT setup
    assert b'Player drafted' in response.data