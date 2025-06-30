from flask import Blueprint, request, jsonify
from src.models.user import db, User, UserRole
from src.models.activity import Activity, ActivityType
from src.routes.auth import token_required, role_required
from datetime import datetime, timedelta

activities_bp = Blueprint('activities', __name__)

@activities_bp.route('/', methods=['GET'])
@token_required
def get_activities(current_user):
    # Get query parameters for filtering
    activity_type = request.args.get('activity_type')
    user_id = request.args.get('user_id', type=int)
    candidate_id = request.args.get('candidate_id', type=int)
    application_id = request.args.get('application_id', type=int)
    job_position_id = request.args.get('job_position_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # Base query
    query = Activity.query
    
    # Apply filters
    if activity_type:
        try:
            activity_type_enum = ActivityType(activity_type)
            query = query.filter_by(activity_type=activity_type_enum)
        except ValueError:
            return jsonify({'message': 'Invalid activity type value'}), 400
    
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    if candidate_id:
        query = query.filter_by(candidate_id=candidate_id)
    
    if application_id:
        query = query.filter_by(application_id=application_id)
    
    if job_position_id:
        query = query.filter_by(job_position_id=job_position_id)
    
    # Date range filtering
    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from)
            query = query.filter(Activity.created_at >= from_date)
        except ValueError:
            return jsonify({'message': 'Invalid date format for date_from!'}), 400
    
    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to)
            query = query.filter(Activity.created_at <= to_date)
        except ValueError:
            return jsonify({'message': 'Invalid date format for date_to!'}), 400
    
    # Pagination
    activities_pagination = query.order_by(Activity.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # Format response
    activities_list = []
    for activity in activities_pagination.items:
        activity_data = {
            'id': activity.id,
            'activity_type': activity.activity_type.value,
            'description': activity.description,
            'details': activity.details,
            'created_at': activity.created_at.isoformat(),
            'user_id': activity.user_id,
            'user_name': activity.user.full_name if activity.user else None
        }
        
        # Add related entity IDs if they exist
        if activity.candidate_id:
            activity_data['candidate_id'] = activity.candidate_id
        
        if activity.application_id:
            activity_data['application_id'] = activity.application_id
        
        if activity.job_position_id:
            activity_data['job_position_id'] = activity.job_position_id
        
        activities_list.append(activity_data)
    
    return jsonify({
        'activities': activities_list,
        'total': activities_pagination.total,
        'pages': activities_pagination.pages,
        'current_page': activities_pagination.page
    })

@activities_bp.route('/recent', methods=['GET'])
@token_required
def get_recent_activities(current_user):
    # Get query parameters
    days = request.args.get('days', 7, type=int)
    limit = request.args.get('limit', 20, type=int)
    
    # Calculate date range
    from_date = datetime.utcnow() - timedelta(days=days)
    
    # Get recent activities
    activities = Activity.query.filter(
        Activity.created_at >= from_date
    ).order_by(Activity.created_at.desc()).limit(limit).all()
    
    # Format response
    activities_list = []
    for activity in activities:
        activity_data = {
            'id': activity.id,
            'activity_type': activity.activity_type.value,
            'description': activity.description,
            'created_at': activity.created_at.isoformat(),
            'user_id': activity.user_id,
            'user_name': activity.user.full_name if activity.user else None
        }
        
        # Add related entity IDs if they exist
        if activity.candidate_id:
            activity_data['candidate_id'] = activity.candidate_id
        
        if activity.application_id:
            activity_data['application_id'] = activity.application_id
        
        if activity.job_position_id:
            activity_data['job_position_id'] = activity.job_position_id
        
        activities_list.append(activity_data)
    
    return jsonify({'activities': activities_list})

@activities_bp.route('/', methods=['POST'])
@token_required
def create_activity(current_user):
    data = request.get_json()
    
    # Validate required fields
    if not data.get('activity_type') or not data.get('description'):
        return jsonify({'message': 'Activity type and description are required!'}), 400
    
    # Process enum
    try:
        activity_type = ActivityType(data['activity_type'])
    except ValueError:
        return jsonify({'message': 'Invalid activity type value!'}), 400
    
    # Create new activity
    new_activity = Activity(
        user_id=current_user.id,
        activity_type=activity_type,
        description=data['description'],
        details=data.get('details'),
        candidate_id=data.get('candidate_id'),
        application_id=data.get('application_id'),
        job_position_id=data.get('job_position_id')
    )
    
    db.session.add(new_activity)
    db.session.commit()
    
    return jsonify({
        'message': 'Activity logged successfully!',
        'activity_id': new_activity.id
    }), 201

@activities_bp.route('/statistics', methods=['GET'])
@token_required
@role_required([UserRole.ADMIN, UserRole.MANAGER])
def get_activity_statistics(current_user):
    # Get query parameters
    days = request.args.get('days', 30, type=int)
    
    # Calculate date range
    from_date = datetime.utcnow() - timedelta(days=days)
    
    # Count activities by type
    type_counts = {}
    for activity_type in ActivityType:
        count = Activity.query.filter(
            Activity.activity_type == activity_type,
            Activity.created_at >= from_date
        ).count()
        type_counts[activity_type.value] = count
    
    # Count activities by user (top 5)
    user_counts = db.session.query(
        Activity.user_id, User.full_name, db.func.count(Activity.id)
    ).join(User).filter(
        Activity.created_at >= from_date
    ).group_by(Activity.user_id, User.full_name).order_by(
        db.func.count(Activity.id).desc()
    ).limit(5).all()
    
    user_data = [{
        'user_id': user_id,
        'user_name': user_name,
        'activity_count': count
    } for user_id, user_name, count in user_counts]
    
    # Activity trend by day
    today = datetime.utcnow().date()
    daily_counts = []
    
    for i in range(days):
        day = today - timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        
        count = Activity.query.filter(
            Activity.created_at >= day_start,
            Activity.created_at <= day_end
        ).count()
        
        daily_counts.append({
            'date': day.isoformat(),
            'count': count
        })
    
    # Reverse to get chronological order
    daily_counts.reverse()
    
    return jsonify({
        'total_activities': Activity.query.filter(Activity.created_at >= from_date).count(),
        'type_distribution': type_counts,
        'top_active_users': user_data,
        'daily_trend': daily_counts
    })
