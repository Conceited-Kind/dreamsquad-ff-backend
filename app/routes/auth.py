from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from .. import db
from ..models import User
import requests
import os

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user with email and password
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username: {type: string}
            email: {type: string}
            password: {type: string}
    responses:
      201: {description: User registered}
      400: {description: Invalid input or user exists}
    """
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not all([username, email, password]):
        return jsonify({'message': 'Missing fields'}), 400

    if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered'}), 201

@bp.route('/login', methods=['POST'])
def login():
    """
    Login with email and password
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            email: {type: string}
            password: {type: string}
    responses:
      200: {description: JWT token returned}
      401: {description: Invalid credentials}
    """
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401

@bp.route('/google', methods=['POST'])
def google_login():
    """
    Login with Google OAuth
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            token: {type: string}
    responses:
      200: {description: JWT token returned}
      400: {description: Invalid token}
    """
    token = request.get_json().get('token')
    if not token:
        return jsonify({'message': 'Missing token'}), 400


    try:
        response = requests.get(
            'https://www.googleapis.com/oauth2/v3/tokeninfo',
            params={'id_token': token}
        )
        data = response.json()
        if 'sub' not in data:
            return jsonify({'message': 'Invalid token'}), 400

        google_id = data['sub']
        email = data['email']
        username = data.get('name', email.split('@')[0])

        user = User.query.filter_by(google_id=google_id).first()
        if not user:
            user = User(username=username, email=email, google_id=google_id)
            db.session.add(user)
            db.session.commit()

        access_token = create_access_token(identity=user.id)
        return jsonify({'access_token': access_token}), 200
    except Exception:
        return jsonify({'message': 'Token verification failed'}), 400