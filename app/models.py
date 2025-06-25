from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=True)  # Null for Google OAuth users
    google_id = db.Column(db.String(120), unique=True, nullable=True)
    team = db.relationship('Team', backref='user', uselist=False, cascade='all, delete-orphan')
    leagues = db.relationship('League', secondary='league_member', backref='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    budget_left = db.Column(db.Float, default=100.0)
    points = db.Column(db.Integer, default=0)
    players = db.relationship('Player', secondary='team_player', backref='teams')
    scores = db.relationship('Score', backref='team', cascade='all, delete-orphan')

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(100), nullable=False)  # e.g., Man City
    position = db.Column(db.String(50), nullable=False)
    value = db.Column(db.Float, nullable=False)
    points = db.Column(db.Integer, default=0)

class League(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_private = db.Column(db.Boolean, default=False)
    code = db.Column(db.String(10), unique=True, nullable=True)  # For private leagues

class LeagueMember(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'), primary_key=True)
    join_date = db.Column(db.DateTime, default=datetime.utcnow)  # User-submittable attribute
    user = db.relationship('User', backref='league_members')
    league = db.relationship('League', backref='league_members')

class TeamPlayer(db.Model):
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), primary_key=True)
    selected_at = db.Column(db.DateTime, default=datetime.utcnow)  # User-submittable attribute
    team = db.relationship('Team', backref='team_players')
    player = db.relationship('Player', backref='team_players')

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    matchday = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, default=0)