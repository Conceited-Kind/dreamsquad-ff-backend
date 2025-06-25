import pytest
from app import create_app, db
from app.models import Score, Team, User

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client

def test_get_scores(client):
    user = User(username='test', email='test@example.com')
    db.session.add(user)
    team = Team(user_id=user.id, name='Test Team')
    db.session.add(team)
    score = Score(team_id=team.id, matchday=1, points=50)
    db.session.add(score)
    db.session.commit()

    response = client.get('/scoreboard?league_id=1', headers={'Authorization': 'Bearer {mock_jwt}'})
    assert response.status_code == 200
    assert len(response.json()) == 1