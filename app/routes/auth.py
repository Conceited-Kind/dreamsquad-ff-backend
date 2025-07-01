from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from .. import db
from ..models import User, Team
import requests
import os
from flask_cors import cross_origin, CORS  # Import both for global and route-specific use

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Apply global CORS configuration for all auth routes
CORS(bp, resources={r"/auth/*": {"origins": ["https://jade-griffin-db7ea0.netlify.app"], "supports_credentials": True}})

@bp.route('/register', methods=['POST'])
@cross_origin(origin=['https://jade-griffin-db7ea0.netlify.app'], supports_credentials=True)  # Route-specific CORS
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
@cross_origin(origin=['https://jade-griffin-db7ea0.netlify.app'], supports_credentials=True)  # Route-specific CORS
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
@cross_origin(origin=['https://jade-griffin-db7ea0.netlify.app'], supports_credentials=True)  # Route-specific CORS
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
            token: {type: string}
    responses:
      200:
        description: JWT token returned.
      400:
        description: Invalid Google token or duplicate email.
      500:
        description: Internal server error.
    """
    # Handle the browser's preflight request
    if request.method == 'OPTIONS':
        return jsonify({'message': 'CORS preflight successful'}), 200

    # Handle the actual POST request
    google_token = request.get_json().get('token')
    if not google_token:
        return jsonify({'message': 'Missing Google token'}), 400

    try:
        # Verify the token with Google's servers
        response = requests.get(
            'https://www.googleapis.com/oauth2/v3/tokeninfo',
            params={'id_token': google_token}
        )
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        if 'sub' not in data or 'email' not in data:
            return jsonify({'message': 'Invalid token data from Google'}), 400

        google_id = data['sub']
        email = data['email']
        base_username = data.get('name', email.split('@')[0]).replace(" ", "_")

        # Handle duplicate username by appending a counter
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

            # Create a default team for the new Google user
            default_team = Team(name=f"{username}'s Team", user_id=user.id)
            db.session.add(default_team)
            db.session.commit()
        else:
            # Update username if it changed (e.g., due to Google profile update)
            if user.username != username:
                user.username = username
                db.session.commit()

        # Create and return our own app's access token
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token, 'username': user.username}), 200
        
    except requests.RequestException as e:
        return jsonify({'message': f'Token verification failed: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'An internal error occurred: {str(e)}'}), 500