import pytest
from app import create_app, db
from app.models import League

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

def test_create_league(client):
    response = client.post('/leagues/league', json={'name': 'Test League', 'is_private': False}, headers={'Authorization': 'Bearer {mock_jwt}'})
    assert response.status_code == 201
    assert 'id' in response.json()