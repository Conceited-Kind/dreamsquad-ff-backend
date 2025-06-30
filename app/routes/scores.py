from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from .. import db
from ..models import Player
import random

bp = Blueprint('scores', __name__, url_prefix='/scoreboard')

@bp.route('/update', methods=['POST'])
@jwt_required()
def update_scores():
    """
    Simulates a gameweek by updating all player scores with a random value.
    ---
    tags: [Scoreboard]
    responses:
      200:
        description: Player scores updated successfully.
      500:
        description: Failed to update scores.
    """
    try:
        players = Player.query.all()
        for player in players:
            player.points += random.randint(-2, 15)
            if player.points < 0:
                player.points = 0
        
        db.session.commit()
        return jsonify({'message': f'Successfully updated scores for {len(players)} players.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to update scores', 'error': str(e)}), 500
