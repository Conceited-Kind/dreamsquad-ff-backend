from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import User

bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@bp.route('', methods=['GET'])
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
    user = User.query.get_or_404(user_id)
    team = user.team

    if not team:
        return jsonify({'message': 'No team found for this user.'}), 404

    # --- Data Enhancements ---
    
    # 1. Get League Standings Snippet
    league_standings_snippet = []
    rank = 'N/A'
    if team.league:
        all_teams_in_league = sorted(team.league.teams, key=lambda t: t.total_points, reverse=True)
        try:
            user_rank_index = all_teams_in_league.index(team)
            rank = user_rank_index + 1
            
            # Get top 2 teams
            top_two = all_teams_in_league[:2]
            
            # Add top teams to snippet
            for i, t in enumerate(top_two):
                league_standings_snippet.append({
                    'rank': i + 1,
                    'team_name': t.name,
                    'owner_name': t.user.username,
                    'points': t.total_points
                })
            
            # Add user's team to snippet if they are not in the top 2
            if user_rank_index > 1:
                league_standings_snippet.append({
                    'rank': rank,
                    'team_name': team.name,
                    'owner_name': user.username,
                    'points': team.total_points
                })

        except ValueError:
            rank = 'N/A'

    # 2. Get Top 3 Performing Players
    top_performers = sorted(team.players, key=lambda p: p.points, reverse=True)[:3]
    
    # 3. Simulate Upcoming Match Data
    upcoming_match = {
        'opponent_name': "Rival FC",
        'opponent_points': 1150 # Simulated data
    }

    # --- Final Dashboard Payload ---
    dashboard_data = {
        'username': user.username,
        'team_name': team.name,
        'total_points': team.total_points,
        'league_rank': rank,
        'team_budget': team.budget_left,
        'squad_size': len(team.players),
        'top_performers': [
            {'name': p.name, 'points': p.points, 'position': p.position, 'photo': p.photo_url} 
            for p in top_performers
        ],
        'league_standings_snippet': league_standings_snippet,
        'upcoming_match': upcoming_match
    }

    return jsonify(dashboard_data), 200
