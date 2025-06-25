from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from .. import db
from ..models import Score, Team, Player
import requests
import os

bp = Blueprint('scores', __name__)

@bp.route('', methods=['GET'])
@jwt_required()
def get_scores():
    """
    Get scores for a league
    ---
    parameters:
      - name: league_id
        in: query
        type: integer
        required: true
    responses:
      200: {description: League scores}
    """
    league_id = request.args.get('league_id')
    scores = Score.query.join(Team).filter(Team.league_id == league_id).all()
    return jsonify([{
        'id': s.id,
        'team': s.team.user.username,
        'matchday': s.matchday,
        'points': s.points
    } for s in scores]), 200

@bp.route('/update', methods=['POST']
@jwt_required():
    def update_scores():
    """
        Update scores based on API data
    ---
        responses:
          201: {description: Scores updated}
          400: {description: API error}
    """
    api_key = os.getenv('FOOTBALL_API_KEY')
    headers = {'X-Auth-Token': api_key}
    try:
        # Fetch match results (simplified)
        response = requests.get('https://api.football-data.org/v4/competitions/PL/matches', headers=headers)
        matches = response.json()['matches']
        for match in matches:
            matchday = match['matchday']
            for player in Player.query.all():
                # Placeholder scoring logic: goal = 5 pts, assist = 3 pts
                player_points = 0  # Fetch from API
                for team in Team.query.filter(Team.players.any(id=player.id)):
                    score = Score.query.filter_by(team_id=team.id, matchday=matchday).first()
                    if not score:
                        score = Score(team_id=team.id, matchday=matchday, points=player_points)
                        db.session.add(score)
                    else:
                        score.points += player_points
        db.session.commit()
        return jsonify({'message': 'Scores updated'}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400