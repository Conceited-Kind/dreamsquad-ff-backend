from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import User, Team

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('', methods=['GET'])  # Matches /dashboard/
@jwt_required()
def get_dashboard_data():
    """
    Get all aggregated data for the logged-in user's dashboard.
    ---
    tags: [Dashboard]
    responses:
      200:
        description: Aggregated dashboard data.
      404:
        description: User or team not found.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)  # Avoid get_or_404 to handle gracefully

    if not user:
        return jsonify({'message': 'User not found'}), 404

    team = getattr(user, 'team', None)  # Safely get team, handle None

    if not team:
        return jsonify({'message': 'No team found for this user'}), 404

    # 1. Get League Standings Snippet
    league_standings_snippet = []
    rank = 'N/A'
    league = getattr(team, 'league', None)
    if league and league.teams:
        all_teams_in_league = sorted(league.teams, key=lambda t: getattr(t, 'total_points', 0), reverse=True)
        try:
            user_rank_index = all_teams_in_league.index(team)
            rank = user_rank_index + 1
            
            # Get top 2 teams
            top_two = all_teams_in_league[:2]
            
            # Add top teams to snippet
            for i, t in enumerate(top_two):
                league_standings_snippet.append({
                    'rank': i + 1,
                    'team_name': getattr(t, 'name', 'Unknown Team'),
                    'owner_name': getattr(t.user, 'username', 'Unknown Owner'),
                    'points': getattr(t, 'total_points', 0)
                })
            
            # Add user's team to snippet if they are not in the top 2
            if user_rank_index > 1:
                league_standings_snippet.append({
                    'rank': rank,
                    'team_name': team.name,
                    'owner_name': user.username,
                    'points': getattr(team, 'total_points', 0)
                })

        except ValueError:
            rank = 'N/A'

    # 2. Get Top 3 Performing Players
    players = getattr(team, 'players', [])
    top_performers = [
        {
            'name': getattr(p, 'name', 'Unknown Player'),
            'points': getattr(p, 'points', 0),
            'position': getattr(p, 'position', 'Unknown'),
            'photo': getattr(p, 'photo_url', 'https://via.placeholder.com/40')
        }
        for p in sorted(players, key=lambda p: getattr(p, 'points', 0), reverse=True)[:3]
    ]

    # 3. Simulate Upcoming Match Data
    upcoming_match = {
        'opponent_name': "Rival FC",
        'opponent_points': 1150  # Simulated data
    }

    # --- Final Dashboard Payload ---
    dashboard_data = {
        'team_name': getattr(team, 'name', 'No Team'),
        'total_points': getattr(team, 'total_points', 0),
        'league_rank': rank,
        'team_budget': getattr(team, 'budget_left', 100.0),
        'squad_size': len(players),
        'top_performers': top_performers,
        'league_standings_snippet': league_standings_snippet,
        'upcoming_match': upcoming_match
    }

    return jsonify(dashboard_data), 200