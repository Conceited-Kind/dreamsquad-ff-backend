from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import Team, Player

bp = Blueprint('teams', __name__, url_prefix='/teams')

@bp.route('/my-team', methods=['GET', 'OPTIONS'])
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
    print(f"Request method: {request.method}, Headers: {request.headers}")
    if request.method == 'OPTIONS':
        return '', 200
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

@bp.route('/draft', methods=['POST', 'OPTIONS'])
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
    print(f"Request method: {request.method}, Headers: {request.headers}")
    if request.method == 'OPTIONS':
        return '', 200
    user_id = get_jwt_identity()
    data = request.get_json()
    player_id = data.get('player_id')

    if not player_id:
        print(f"Draft failed: No player_id provided")
        return jsonify({'message': 'Player ID is required'}), 400

    team = Team.query.filter_by(user_id=user_id).first_or_404()
    player = Player.query.get_or_404(player_id)

    if len(team.players) >= 11:
        print(f"Draft failed: Team full for user {user_id}")
        return jsonify({'message': 'Your team is full (11 players).'}), 400
    
    if player in team.players:
        print(f"Draft failed: Player {player_id} already in team")
        return jsonify({'message': 'This player is already in your team.'}), 400

    if team.budget_left < player.value:
        print(f"Draft failed: Insufficient budget for player {player_id}")
        return jsonify({'message': 'Insufficient budget to draft this player.'}), 400

    team.players.append(player)
    team.budget_left -= player.value
    try:
        db.session.commit()
        print(f"Draft success: Player {player_id} added to team {team.id}")
        return jsonify({'message': f'{player.name} has been drafted to your team.'}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Draft error: {str(e)}")
        return jsonify({'message': 'Error drafting player.'}), 500

@bp.route('/remove_player', methods=['POST', 'OPTIONS'])
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
      500:
        description: Database error.
    """
    print(f"Request method: {request.method}, Headers: {request.headers}")
    if request.method == 'OPTIONS':
        return '', 200
    user_id = get_jwt_identity()
    data = request.get_json()
    player_id = data.get('player_id')

    if not player_id:
        print(f"Remove failed: No player_id provided")
        return jsonify({'message': 'Player ID is required'}), 400
        
    team = Team.query.filter_by(user_id=user_id).first_or_404()
    player = Player.query.get_or_404(player_id)

    if player not in team.players:
        print(f"Remove failed: Player {player_id} not in team {team.id}")
        return jsonify({'message': 'This player is not in your team.'}), 400

    team.players.remove(player)
    team.budget_left += player.value
    try:
        db.session.commit()
        print(f"Remove success: Player {player_id} removed from team {team.id}")
        return jsonify({'message': f'{player.name} has been removed from your team.'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Remove error: {str(e)}")
        return jsonify({'message': 'Error removing player.'}), 500