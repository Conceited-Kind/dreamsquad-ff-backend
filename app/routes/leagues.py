from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import League, LeagueMember, User
import uuid

bp = Blueprint('leagues', __name__)

@bp.route('', methods=['POST'])
@jwt_required()
def create_league():
    """
    Create a new league
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name: {type: string}
            is_private: {type: boolean}
    responses:
      201: {description: League created}
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get('name')
    is_private = data.get('is_private', False)
    code = str(uuid.uuid4())[:6] if is_private else None

    league = League(name=name, is_private=is_private, code=code)
    db.session.add(league)
    db.session.commit()

    league_member = LeagueMember(user_id=user_id, league_id=league.id)
    db.session.add(league_member)
    db.session.commit()

    return jsonify({'id': league.id, 'name': name, 'code': code}), 201

@bp.route('', methods=['GET'])
@jwt_required()
def get_leagues():
    """
    Get list of available leagues
    ---
    responses:
      200: {description: List of leagues}
    """
    leagues = League.query.filter(League.is_private == False).all()
    return jsonify([{
        'id': league.id,
        'name': league.name,
        'is_private': league.is_private
    } for league in leagues]), 200

@bp.route('/join', methods=['POST'])
@jwt_required()
def join_league():
    """
    Join a league by code
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            code: {type: string}
    responses:
      200: {description: Joined league}
      400: {description: Invalid code}
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    code = request.get('code')

    league = League.query.filter_by(code=code).first()
    if not league:
        return jsonify({'message': 'Invalid league code'}), 400

    if LeagueMember.query.get((user_id, league.id)):
        return jsonify({'message': 'Already joined'}), 400

    league_member =  LeagueMember(user_id=user_id, league_id=league.id)
    db.session.add(league_member)
    db.session.commit()
    return jsonify({'message': 'Joined league'}), 200