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

    # --- Flasgger Configuration for JWT ---
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
    
    # --- FINAL CORS CONFIGURATION ---
    # This more detailed configuration allows the necessary headers and methods
    # from your frontend's origin, which will fix the error.
    CORS(
        app, 
        resources={r"/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}}, 
        supports_credentials=True
    )
    # --- END CORS CONFIGURATION ---

    # Register blueprints
    from .routes import auth, players, teams, leagues, dashboard, scores
    app.register_blueprint(auth.bp)
    app.register_blueprint(players.bp)
    app.register_blueprint(teams.bp)
    app.register_blueprint(leagues.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(scores.bp)

    # Health check route
    @app.route('/')
    def index():
        return {"message": "Welcome to the DreamSquad API!", "status": "ok"}

    return app
