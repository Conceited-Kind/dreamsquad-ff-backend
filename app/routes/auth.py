from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from google.oauth2 import id_token
from google.auth.transport import requests
from .. import db
from ..models import User, Team
from flask_cors import cross_origin, CORS

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Apply global CORS configuration
CORS(bp, resources={r"/auth/*": {"origins": [
    "http://localhost:5173",
    "https://jade-griffin-db7ea0.netlify.app"
], "supports_credentials": True}})

@bp.route('/register', methods=['POST'])
@cross_origin(origins=['http://localhost:5173', 'https://jade-griffin-db7ea0.netlify.app'], supports_credentials=True)
def register():
    """
    Register a new user and create their default team.
    ---
    tags: [Authentication]
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [username, email, password]
          properties:
            username: {type: string}
            email: {type: string}
            password: {type: string}
    responses:
      201:
        description: User registered successfully.
      400:
        description: Invalid input or user already exists.
    """
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({'message': 'Username, email, and password are required'}), 400

    if User.query.filter((User.email == email) | (User.username == username)).first():
        return jsonify({'message': 'User with that email or username already exists'}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    default_team = Team(name=f"{username}'s Team", user_id=user.id)
    db.session.add(default_team)
    
    db.session.commit()

    return jsonify({'message': f'User {username} registered successfully'}), 201

@bp.route('/login', methods=['POST'])
@cross_origin(origins=['http://localhost:5173', 'https://jade-griffin-db7ea0.netlify.app'], supports_credentials=True)
def login():
    """
    Log in a user and return a JWT access token.
    ---
    tags: [Authentication]
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required: [email, password]
          properties:
            email: {type: string}
            password: {type: string}
    responses:
      200:
        description: Login successful.
      401:
        description: Invalid credentials.
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token, username=user.username), 200

    return jsonify({'message': 'Invalid credentials'}), 401

@bp.route('/google', methods=['POST', 'OPTIONS'])
@cross_origin(origins=['http://localhost:5173', 'https://jade-griffin-db7ea0.netlify.app'], supports_credentials=True)
def google_login():
    """
    Login or Register with a Google ID Token.
    ---
    tags: [Authentication]
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            id_token: {type: string}
    responses:
      200:
        description: JWT token returned.
      400:
        description: Invalid Google token or duplicate email.
      500:
        description: Internal server error.
    """
    if request.method == 'OPTIONS':
        return jsonify({'message': 'CORS preflight successful'}), 200

    token = request.get_json().get('id_token')
    if not token:
        return jsonify({'message': 'Missing Google ID token'}), 400

    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            '390480519666-5d2b8en0e3slv374hhm696mrtq0l4l0e.apps.googleusercontent.com'
        )
        google_id = idinfo['sub']
        email = idinfo['email']
        base_username = idinfo.get('name', email.split('@')[0]).replace(" ", "_")

        # Handle duplicate username
        username = base_username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            if User.query.filter_by(email=email).first():
                return jsonify({'message': f'An account with the email {email} already exists. Please log in with your existing credentials or use a different email.'}), 400
            user = User(username=username, email=email, google_id=google_id)
            db.session.add(user)
            db.session.flush()

            default_team = Team(name=f"{username}'s Team", user_id=user.id)
            db.session.add(default_team)
            db.session.commit()
        else:
            if user.username != username:
                user.username = username
                db.session.commit()

        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token, 'username': user.username}), 200

    except ValueError as e:
        return jsonify({'message': f'Token verification failed: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'An internal error occurred: {str(e)}'}), 500