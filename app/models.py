from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Association table for the many-to-many relationship between Users and Leagues
league_member_table = db.Table('league_member',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('league_id', db.Integer, db.ForeignKey('league.id'), primary_key=True)
)

# Association table for the many-to-many relationship between Teams and Players
team_player_table = db.Table('team_player',
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True),
    db.Column('player_id', db.Integer, db.ForeignKey('player.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=True)
    google_id = db.Column(db.String(120), unique=True, nullable=True)
    
    team = db.relationship('Team', back_populates='user', uselist=False, cascade='all, delete-orphan')
    leagues = db.relationship('League', secondary=league_member_table, back_populates='users')
    owned_leagues = db.relationship('League', back_populates='owner')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # --- FINAL FIX ---
        # First, check if a password hash exists at all.
        # If it doesn't, this user can't log in with a password.
        if not self.password_hash:
            return False
        # If it does exist, then check it.
        return check_password_hash(self.password_hash, password)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    league_id = db.Column(db.Integer, db.ForeignKey('league.id'), nullable=True)
    budget_left = db.Column(db.Float, default=100.0)
    
    user = db.relationship('User', back_populates='team')
    league = db.relationship('League', back_populates='teams')
    players = db.relationship('Player', secondary=team_player_table, back_populates='teams')
    
    @property
    def total_points(self):
        return sum(player.points for player in self.players)

class Player(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_player_id = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    team_name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    photo_url = db.Column(db.String(200), nullable=True)
    value = db.Column(db.Float, nullable=False, default=5.0)
    points = db.Column(db.Integer, default=0)
    
    teams = db.relationship('Team', secondary=team_player_table, back_populates='players')

class League(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    code = db.Column(db.String(8), unique=True, nullable=True, index=True)
    is_private = db.Column(db.Boolean, default=True)
    max_members = db.Column(db.Integer, default=12)
    
    owner = db.relationship('User', back_populates='owned_leagues')
    users = db.relationship('User', secondary=league_member_table, back_populates='leagues')
    teams = db.relationship('Team', back_populates='league')
