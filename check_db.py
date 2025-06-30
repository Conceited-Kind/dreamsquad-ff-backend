from app import create_app, db
from app.models import Player

app = create_app()
with app.app_context():
    # Query all players
    players = Player.query.all()
    print(f"Total players in database: {len(players)}")
    print("First 5 players:")
    for p in players[:5]:
        print(f"ID: {p.id}, API Player ID: {p.api_player_id}, Name: {p.name}, Team: {p.team}, Position: {p.position}, Value: {p.value}, Photo: {p.photo}")

    # Optional: Check for players from a specific league/season
    premier_league_players = Player.query.filter_by(team="Arsenal").all()  # Example filter
    print(f"\nPlayers from Arsenal: {len(premier_league_players)}")
    for p in premier_league_players[:5]:
        print(f"Name: {p.name}, Team: {p.team}, Position: {p.position}")