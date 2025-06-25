from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flasgger import Swagger
from .config import Config
from .routes import auth, players, teams, leagues, scores

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    Swagger(app, template_file='swagger.yml')

    # Register blueprints
    app.register_blueprint(auth.bp, url_prefix='/auth')
    app.register_blueprint(players.bp, url_prefix='/players')
    app.register_blueprint(teams.bp, url_prefix='/team')
    app.register_blueprint(leagues.bp, url_prefix='/leagues')
    app.register_blueprint(scores.bp, url_prefix='/scoreboard')

    with app.app_context():
        db.create_all()

    return app