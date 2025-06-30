import pytest
from app import create_app, db
from app.models import Player

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

def test_get_players(client):
    player = Player(name='Erling Haaland', team='Man City', position='Forward', value=15.0)
    db.session.add(player)
    db.session.commit()

    response = client.get('/players', headers={'Authorization': 'Bearer {mock_jwt}'})
    assert response.status_code == 200
    # Note: JWT auth requires proper setup
    assert len(response.json()) == 1
    assert response.json()[0]['name'] == 'Erling Haaland'