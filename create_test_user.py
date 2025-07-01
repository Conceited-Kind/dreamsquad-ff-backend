from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    email = "newtest@example.com"
    username = "newtestuser"
    password = "testpassword123"
    user = User.query.filter_by(email=email).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        print(f"Deleted user: {email}")
    new_user = User(
        username=username,
        email=email
    )
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    print(f"Created user: {email} with password: {password}, Hash: {new_user.password_hash}")