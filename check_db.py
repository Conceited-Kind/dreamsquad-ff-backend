from app import create_app, db
from app.models import User, Team, Player

app = create_app()
with app.app_context():
    users = User.query.all()
    print(f"Total users in database: {len(users)}")
    for u in users:
        print(f"ID: {u.id}, Username: {u.username}, Email: {u.email}")

    teams = Team.query.all()
    print(f"\nTotal teams in database: {len(teams)}")
    for t in teams:
        print(f"ID: {t.id}, Name: {t.name}, User ID: {t.user_id}, Budget Left: {t.budget_left}")

    players = Player.query.all()
    print(f"\nTotal players in database: {len(players)}")
    print("First 5 players:")
    for p in players[:5]:
        print(f"ID: {p.id}, API Player ID: {p.api_player_id}, Name: {p.name}, Team: {p.team_name}, Position: {p.position}, Value: {p.value}, Photo: {p.photo_url}")