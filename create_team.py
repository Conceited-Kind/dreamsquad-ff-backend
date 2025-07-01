from app import create_app, db
from app.models import User, Team

app = create_app()
with app.app_context():
    user = User.query.get(8)
    if user:
        if not Team.query.filter_by(user_id=user.id).first():
            team = Team(
                name="Test Team",
                user_id=user.id,
                budget_left=100.0
            )
            db.session.add(team)
            db.session.commit()
            print(f"Created team for user: {user.email}")
        else:
            print(f"Team already exists for user: {user.email}")
    else:
        print("User ID 8 not found")