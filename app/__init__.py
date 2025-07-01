from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    # Enhanced Swagger Configuration
    app.config['SWAGGER'] = {
        'title': 'DreamSquad FF API',
        'uiversion': 3,
        "specs_route": "/apidocs/",
        'securityDefinitions': {
            'Bearer': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'Enter your bearer token in the format **Bearer &lt;token&gt;**'
            }
        },
        'security': [{'Bearer': []}]
    }
    swagger = Swagger(app)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Comprehensive CORS Configuration
    CORS(
        app, 
        resources={
            r"/*": {
                "origins": [
                    "http://localhost:5173", 
                    "http://127.0.0.1:5173",
                    "https://your-production-domain.com"
                    "https://jade-griffin-db7ea0.netlify.app"
                    "https://dreamsquad-ff-backend-2.onrender.com"
                ],
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": [
                    "Content-Type", 
                    "Authorization",
                    "X-Requested-With",
                    "Access-Control-Allow-Origin"
                ],
                "supports_credentials": True,
                "expose_headers": [
                    "Content-Type", 
                    "Authorization",
                    "Access-Control-Allow-Origin"
                ],
                "max_age": 600
            }
        }
    )

    # Register blueprints
    from .routes import auth, players, teams, leagues, dashboard, scores
    app.register_blueprint(auth.bp)
    app.register_blueprint(players.bp)
    app.register_blueprint(teams.bp)
    app.register_blueprint(leagues.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(scores.bp)

    @app.route('/')
    def index():
        return {"message": "Welcome to the DreamSquad API!", "status": "ok"}

    return app

