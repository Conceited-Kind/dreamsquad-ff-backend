from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import Team, Player, TeamPlayer, User
from datetime import datetime

bp = Blueprint('teams', _name_)

@bp.route('/draft', methods=['POST'])
@jwt_required()
def draft_player():
    """
    Add player to user's team
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            player_id: {type: integer}
    responses:
      201: {description: Player drafted}
      400: {description: Invalid input or budget exceeded}
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    player_id = data.get('player_id')

    team = Team.query.filter_by(user_id=user_id).first()
    player = Player.query.get_or_404(player_id)

    if not team:
        team = Team(user_id=user_id, name=f"{User.query.get(user_id).username}'s Team")
        db.session.add(team)
        db.session.commit()

    if len(team.players) >= 11:
        return jsonify({'message': 'Team is full'}), 400

    if team.budget_left < player.value:
        return jsonify({'message': 'Insufficient budget'}), 400

    team_player = TeamPlayer(team_id=team.id, player_id=player.id, selected_at=datetime.utcnow())
    team.budget_left -= player.value
    db.session.add(team_player)
    db.session.commit()

    return jsonify({'message': 'Player drafted'}), 201

@bp.route('', methods=['GET'])
@jwt_required()
def get_team():
    """
    Get user's team
    ---
    responses:
      200: {description: Team details}
    """
    user_id = get_jwt_identity()
    team = Team.query.filter_by(user_id=user_id).first()
    if not team:
        return jsonify({'message': 'No team found'}), 404
    return jsonify({
        'id': team.id,
        'name': team.name,
        'budget_left': team.budget_left,
        'players': [{'id': p.id, 'name': p.name} for p in team.players]
    }), 200

@bp.route('', methods=['PUT'])
@jwt_required()
def update_team():
    """
    Update team name
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name: {type: string}
    responses:
      200: {description: Team updated}
    """
    user_id = get_jwt_identity()
    team = Team.query.filter_by(user_id=user_id).first_or_404()
    data = request.get_json()
    team.name = data.get('name', team.name)
    db.session.commit()
    return jsonify({'message': 'Team updated'}), 200

@bp.route('', methods=['DELETE'])
@jwt_required()
def delete_team():
    """
    Delete user's team
    ---
    responses:
      200: {description: Team deleted}
    """
    user_id = get_jwt_identity()
    team = Team.query.filter_by(user_id=user_id).first_or_404()
    db.session.delete(team)
    db.session.commit()
    return jsonify({'message': 'Team deleted'}), 200