from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from .. import db
from ..models import Player
import requests
import os
import random

bp = Blueprint('players', __name__, url_prefix='/players')

@bp.route('', methods=['GET'])
@jwt_required()
def get_players():
    """
    Get a list of all available players for drafting.
    ---
    tags: [Players]
    responses:
      200:
        description: A list of players.
    """
    players = Player.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'team': p.team_name,
        'position': p.position,
        'value': p.value,
        'points': p.points,
        'photo': p.photo_url
    } for p in players]), 200

@bp.route('/sync', methods=['POST'])
@jwt_required()
def sync_players():
    """
    Syncs the player database with the external API-Football, fetching all pages.
    ---
    tags: [Players]
    responses:
      201:
        description: Player sync complete.
      500:
        description: API key missing or request failed.
    """
    api_key = os.getenv('API_FOOTBALL_KEY')
    if not api_key:
        return jsonify({'message': 'API key for API-Football is missing'}), 500

    headers = {'x-apisports-key': api_key}
    base_params = {'league': '39', 'season': '2023'} # Premier League, 2023-2024 Season
    url = 'https://v3.football.api-sports.io/players'
    
    current_page = 1
    total_pages = 1 # Start with 1, will be updated after the first call
    players_added = 0
    
    # --- PAGINATION LOOP ---
    # Keep fetching pages as long as we haven't exceeded the total number of pages
    while current_page <= total_pages:
        try:
            params = {**base_params, 'page': current_page}
            response = requests.get(url, headers=headers, params=params, timeout=20)
            response.raise_for_status()
            
            data = response.json()
            
            # After the first request, update total_pages with the real value from the API
            if current_page == 1:
                total_pages = data.get('paging', {}).get('total', 1)

            players_data = data.get('response', [])
            if not players_data:
                break # Stop if there's no data on the current page

            for player_obj in players_data:
                player_info = player_obj.get('player', {})
                stats = player_obj.get('statistics', [{}])[0]
                api_id = player_info.get('id')

                if not api_id or not stats.get('games', {}).get('position'):
                    continue

                if not Player.query.filter_by(api_player_id=api_id).first():
                    new_player = Player(
                        api_player_id=api_id,
                        name=player_info.get('name', 'N/A'),
                        team_name=stats.get('team', {}).get('name', 'N/A'),
                        position=stats.get('games', {}).get('position', 'Unknown'),
                        photo_url=player_info.get('photo'),
                        value=round(random.uniform(4.5, 13.0), 1),
                        points=random.randint(20, 150)
                    )
                    db.session.add(new_player)
                    players_added += 1
            
            # Move to the next page for the next iteration
            current_page += 1

        except requests.RequestException as e:
            return jsonify({'message': f'API-Football request failed: {e}'}), 500
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': f'An error occurred during sync: {e}'}), 500

    db.session.commit()
    return jsonify({'message': f'Player sync complete. Added {players_added} new players.'}), 201
