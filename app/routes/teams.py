from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import Team, Player

bp = Blueprint('teams', __name__, url_prefix='/team')

@bp.route('', methods=['GET'])
@jwt_required()
def get_team():
    """
    Get the current user's team details and player list.
    ---
    tags: [Team]
    responses:
      200:
        description: The user's team details.
      404:
        description: Team not found for this user.
    """
    user_id = get_jwt_identity()
    team = Team.query.filter_by(user_id=user_id).first_or_404()
    
    return jsonify({
        'id': team.id,
        'name': team.name,
        'budget_left': team.budget_left,
        'total_points': team.total_points,
        'players': [{
            'id': p.id, 
            'name': p.name,
            'team': p.team_name,
            'position': p.position,
            'value': p.value,
            'points': p.points,
            'photo': p.photo_url
        } for p in team.players]
    }), 200

@bp.route('/draft', methods=['POST'])
@jwt_required()
def draft_player():
    """
    Draft a player to the user's team.
    ---
    tags: [Team]
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            player_id: {type: integer}
    responses:
      201:
        description: Player drafted successfully.
      400:
        description: Invalid request (e.g., team full, insufficient budget).
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    player_id = data.get('player_id')

    if not player_id:
        return jsonify({'message': 'Player ID is required'}), 400

    team = Team.query.filter_by(user_id=user_id).first_or_404()
    player = Player.query.get_or_404(player_id)

    if len(team.players) >= 11:
        return jsonify({'message': 'Your team is full (11 players).'}), 400
    
    if player in team.players:
        return jsonify({'message': 'This player is already in your team.'}), 400

    if team.budget_left < player.value:
        return jsonify({'message': 'Insufficient budget to draft this player.'}), 400

    team.players.append(player)
    team.budget_left -= player.value
    db.session.commit()

    return jsonify({'message': f'{player.name} has been drafted to your team.'}), 201

@bp.route('/remove_player', methods=['POST'])
@jwt_required()
def remove_player():
    """
    Remove a player from the user's team.
    ---
    tags: [Team]
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            player_id: {type: integer}
    responses:
      200:
        description: Player removed successfully.
      400:
        description: Player not in team.
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    player_id = data.get('player_id')

    if not player_id:
        return jsonify({'message': 'Player ID is required'}), 400
        
    team = Team.query.filter_by(user_id=user_id).first_or_404()
    player = Player.query.get_or_404(player_id)

    if player not in team.players:
        return jsonify({'message': 'This player is not in your team.'}), 400

    team.players.remove(player)
    team.budget_left += player.value
    db.session.commit()

    return jsonify({'message': f'{player.name} has been removed from your team.'}), 200
