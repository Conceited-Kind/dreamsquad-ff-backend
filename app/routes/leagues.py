from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import League, User, Team
import uuid
from sqlalchemy.orm import joinedload

bp = Blueprint('leagues', __name__, url_prefix='/leagues')

def generate_league_code():
    return str(uuid.uuid4()).upper()[:8]

@bp.route('/my-leagues', methods=['GET'])
@jwt_required()
def get_my_leagues():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    leagues_data = []
    for league in user.leagues:
        all_teams_in_league = sorted(league.teams, key=lambda t: t.total_points, reverse=True)
        user_team = next((t for t in all_teams_in_league if t.user_id == user_id), None)
        rank = (all_teams_in_league.index(user_team) + 1) if user_team else 'N/A'

        leagues_data.append({
            'id': league.id,
            'name': league.name,
            'members': len(league.users),
            'maxMembers': league.max_members,
            'code': league.code,
            'rank': rank,
            'points': user_team.total_points if user_team else 0,
            'isOwner': league.owner_id == user_id
        })
        
    return jsonify(leagues_data), 200

@bp.route('/public', methods=['GET'])
@jwt_required()
def get_public_leagues():
    leagues = League.query.filter_by(is_private=False).all()
    return jsonify([{
        'id': league.id,
        'name': league.name,
        'members': f"{len(league.users)}/{league.max_members}",
        'prize': 'Bragging Rights'
    } for league in leagues]), 200

@bp.route('/<int:league_id>', methods=['GET'])
@jwt_required()
def get_league_details(league_id):
    league = League.query.options(joinedload(League.teams).joinedload(Team.user)).get_or_404(league_id)
    standings_data = sorted(league.teams, key=lambda t: t.total_points, reverse=True)
    standings_response = [{
        'rank': i + 1,
        'team_name': team.name,
        'owner_name': team.user.username,
        'points': team.total_points
    } for i, team in enumerate(standings_data)]
    
    return jsonify({
        'id': league.id,
        'name': league.name,
        'code': league.code,
        'standings': standings_response
    }), 200

@bp.route('/create', methods=['POST'])
@jwt_required()
def create_league():
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get('name')
    if not name:
        return jsonify({'message': 'League name is required'}), 400

    new_league = League(name=name, owner_id=user_id, code=generate_league_code())
    user = User.query.get(user_id)
    user.leagues.append(new_league)
    
    team = Team.query.filter_by(user_id=user_id).first()
    if team:
        team.league_id = new_league.id

    db.session.add(new_league)
    db.session.commit()
    
    return jsonify({
        'message': f"League '{name}' created successfully.",
        'league_id': new_league.id,  # Added this line
        'league_code': new_league.code
    }), 201

@bp.route('/join', methods=['POST'])
@jwt_required()
def join_league():
    user_id = get_jwt_identity()
    data = request.get_json()
    code = data.get('code')
    if not code:
        return jsonify({'message': 'League code is required'}), 400

    league = League.query.filter_by(code=code).first()
    if not league:
        return jsonify({'message': 'Invalid league code'}), 404

    user = User.query.get(user_id)
    if league in user.leagues:
        return jsonify({'message': 'You are already in this league'}), 400

    if len(league.users) >= league.max_members:
        return jsonify({'message': 'This league is full'}), 400

    user.leagues.append(league)
    
    team = Team.query.filter_by(user_id=user_id).first()
    if team:
        team.league_id = league.id
        
    db.session.commit()
    return jsonify({'message': f'Successfully joined {league.name}'}), 200

@bp.route('/<int:league_id>/leave', methods=['POST'])
@jwt_required()
def leave_league(league_id):
    user_id = get_jwt_identity()
    league = League.query.get_or_404(league_id)
    user = User.query.get(user_id)

    if league.owner_id == user_id:
        return jsonify({'message': 'Owners cannot leave a league. You must delete it instead.'}), 403

    if league not in user.leagues:
        return jsonify({'message': 'You are not a member of this league.'}), 400

    user.leagues.remove(league)
    
    team = Team.query.filter_by(user_id=user_id).first()
    if team and team.league_id == league_id:
        team.league_id = None

    db.session.commit()
    return jsonify({'message': f'You have successfully left {league.name}.'}), 200

@bp.route('/<int:league_id>', methods=['DELETE'])
@jwt_required()
def delete_league(league_id):
    user_id = get_jwt_identity()
    league = League.query.get_or_404(league_id)

    if league.owner_id != user_id:
        return jsonify({'message': 'Only the league owner can delete this league.'}), 403

    for team in league.teams:
        team.league_id = None
    
    db.session.delete(league)
    db.session.commit()
    return jsonify({'message': f'League "{league.name}" has been deleted.'}), 200