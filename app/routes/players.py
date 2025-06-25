from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from .. import db
from ..models import Player
import requests
import os

bp = Blueprint('players', __name__)

@bp.route('', methods=['GET'])
@jwt_required()
def get_players():
    """
    Get list of players for drafting
    ---
    responses:
      200: {description: List of players}
    """
    players = Player.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'team': p.team, 'position': p.position, 'value': p.value} for p in players]), 200

@bp.route('/sync', methods=['POST'])
@jwt_required()
def sync_players():
    """
    Sync players from Football-Data.org API (Premier League)
    ---
    responses:
      201: {description: Players synced}
      400: {description: API error}
    """
    api_key = os.getenv('FOOTBALL_API_KEY')
    headers = {'X-Auth-Token': api_key}
    try:
        response = requests.get('https://api.football-data.org/v4/competitions/PL/players', headers=headers)
        data = response.json()
        for player in data.get('players', []):
            existing = Player.query.filter_by(name=player['name']).first()
            if not existing:
                new_player = Player(
                    name=player['name'],
                    team=player.get('currentTeam', {}).get('name', 'Unknown'),
                    position=player.get('position', 'Unknown'),
                    value=10.0  # Placeholder, adjust based on API or logic
                )
                db.session.add(new_player)
        db.session.commit()
        return jsonify({'message': 'Players synced'}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400