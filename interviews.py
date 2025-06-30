from flask import Blueprint, request, jsonify
from src.models.user import db, User, UserRole
from src.models.candidate import Candidate
from src.models.application import Application
from src.models.interview import Interview, InterviewType, InterviewStatus
from src.models.activity import Activity, ActivityType
from src.routes.auth import token_required, role_required
from datetime import datetime, timedelta

interviews_bp = Blueprint('interviews', __name__)

@interviews_bp.route('/', methods=['GET'])
@token_required
def get_interviews(current_user):
    # Get query parameters for filtering
    status = request.args.get('status')
    candidate_id = request.args.get('candidate_id', type=int)
    application_id = request.args.get('application_id', type=int)
    interviewer_id = request.args.get('interviewer_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Base query
    query = Interview.query
    
    # Apply filters
    if status:
        try:
            status_enum = InterviewStatus(status)
            query = query.filter_by(status=status_enum)
        except ValueError:
            return jsonify({'message': 'Invalid status value'}), 400
    
    if candidate_id:
        query = query.filter_by(candidate_id=candidate_id)
    
    if application_id:
        query = query.filter_by(application_id=application_id)
    
    if interviewer_id:
        query = query.filter((Interview.interviewer_id == interviewer_id) | 
                            (Interview.client_interviewer_id == interviewer_id))
    
    # Date range filtering
    if date_from:
        try:
            from_date = datetime.fromisoformat(date_from)
            query = query.filter(Interview.scheduled_at >= from_date)
        except ValueError:
            return jsonify({'message': 'Invalid date format for date_from!'}), 400
    
    if date_to:
        try:
            to_date = datetime.fromisoformat(date_to)
            query = query.filter(Interview.scheduled_at <= to_date)
        except ValueError:
            return jsonify({'message': 'Invalid date format for date_to!'}), 400
    
    # Pagination
    interviews_pagination = query.order_by(Interview.scheduled_at).paginate(page=page, per_page=per_page)
    
    # Format response
    interviews_list = []
    for interview in interviews_pagination.items:
        interviews_list.append({
            'id': interview.id,
            'application_id': interview.application_id,
            'candidate_id': interview.candidate_id,
            'candidate_name': interview.candidate.full_name,
            'job_title': interview.application.job_position.title,
            'interview_type': interview.interview_type.value,
            'status': interview.status.value,
            'scheduled_at': interview.scheduled_at.isoformat(),
            'duration_minutes': interview.duration_minutes,
            'location': interview.location,
            'meeting_link': interview.meeting_link,
            'interviewer_id': interview.interviewer_id,
            'interviewer_name': interview.interviewer.full_name if interview.interviewer else None,
            'client_interviewer_id': interview.client_interviewer_id,
            'client_interviewer_name': interview.client_interviewer.full_name if interview.client_interviewer else None,
            'overall_score': interview.overall_score,
            'completed_at': interview.completed_at.isoformat() if interview.completed_at else None
        })
    
    return jsonify({
        'interviews': interviews_list,
        'total': interviews_pagination.total,
        'pages': interviews_pagination.pages,
        'current_page': interviews_pagination.page
    })

@interviews_bp.route('/<int:interview_id>', methods=['GET'])
@token_required
def get_interview(current_user, interview_id):
    interview = Interview.query.get_or_404(interview_id)
    
    # Format response with all details
    interview_data = {
        'id': interview.id,
        'application_id': interview.application_id,
        'candidate_id': interview.candidate_id,
        'candidate_name': interview.candidate.full_name,
        'job_title': interview.application.job_position.title,
        'interview_type': interview.interview_type.value,
        'status': interview.status.value,
        'scheduled_at': interview.scheduled_at.isoformat(),
        'duration_minutes': interview.duration_minutes,
        'location': interview.location,
        'meeting_link': interview.meeting_link,
        'interviewer_id': interview.interviewer_id,
        'interviewer_name': interview.interviewer.full_name if interview.interviewer else None,
        'client_interviewer_id': interview.client_interviewer_id,
        'client_interviewer_name': interview.client_interviewer.full_name if interview.client_interviewer else None,
        'technical_score': interview.technical_score,
        'communication_score': interview.communication_score,
        'culture_fit_score': interview.culture_fit_score,
        'overall_score': interview.overall_score,
        'strengths': interview.strengths,
        'weaknesses': interview.weaknesses,
        'notes': interview.notes,
        'recommendation': interview.recommendation,
        'created_at': interview.created_at.isoformat(),
        'updated_at': interview.updated_at.isoformat(),
        'completed_at': interview.completed_at.isoformat() if interview.completed_at else None
    }
    
    return jsonify({'interview': interview_data})

@interviews_bp.route('/', methods=['POST'])
@token_required
@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER])
def create_interview(current_user):
    data = request.get_json()
    
    # Validate required fields
    if not data.get('application_id') or not data.get('scheduled_at'):
        return jsonify({'message': 'Application ID and scheduled date/time are required!'}), 400
    
    # Verify application exists
    application = Application.query.get(data['application_id'])
    if not application:
        return jsonify({'message': 'Application not found!'}), 404
    
    # Process date fields
    try:
        scheduled_at = datetime.fromisoformat(data['scheduled_at'])
    except ValueError:
        return jsonify({'message': 'Invalid date format for scheduled_at!'}), 400
    
    # Process enums
    interview_type = InterviewType.PHONE
    if data.get('interview_type'):
        try:
            interview_type = InterviewType(data['interview_type'])
        except ValueError:
            return jsonify({'message': 'Invalid interview type value!'}), 400
    
    # Create new interview
    new_interview = Interview(
        application_id=data['application_id'],
        candidate_id=application.candidate_id,
        interview_type=interview_type,
        status=InterviewStatus.SCHEDULED,
        scheduled_at=scheduled_at,
        duration_minutes=data.get('duration_minutes', 60),
        location=data.get('location'),
        meeting_link=data.get('meeting_link'),
        interviewer_id=data.get('interviewer_id', current_user.id),
        client_interviewer_id=data.get('client_interviewer_id')
    )
    
    db.session.add(new_interview)
    
    # Update application status if needed
    if application.status.value in ['new', 'screening']:
        application.status = ApplicationStatus.INTERVIEW
        application.interviewed_at = datetime.utcnow()
        application.update_candidate_status()
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        candidate_id=application.candidate_id,
        application_id=application.id,
        job_position_id=application.job_position_id,
        activity_type=ActivityType.INTERVIEW_SCHEDULED,
        description=f"Interview scheduled for {application.candidate.full_name} on {scheduled_at.strftime('%Y-%m-%d %H:%M')}",
        details={
            "interview_type": interview_type.value,
            "scheduled_at": scheduled_at.isoformat(),
            "duration_minutes": data.get('duration_minutes', 60)
        }
    )
    db.session.add(activity)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Interview scheduled successfully!',
        'interview_id': new_interview.id
    }), 201

@interviews_bp.route('/<int:interview_id>', methods=['PUT'])
@token_required
def update_interview(current_user, interview_id):
    interview = Interview.query.get_or_404(interview_id)
    data = request.get_json()
    
    # Process date fields
    if 'scheduled_at' in data:
        try:
            interview.scheduled_at = datetime.fromisoformat(data['scheduled_at'])
        except ValueError:
            return jsonify({'message': 'Invalid date format for scheduled_at!'}), 400
    
    # Process enums
    if 'interview_type' in data:
        try:
            interview.interview_type = InterviewType(data['interview_type'])
        except ValueError:
            return jsonify({'message': 'Invalid interview type value!'}), 400
    
    if 'status' in data:
        old_status = interview.status
        try:
            new_status = InterviewStatus(data['status'])
            interview.status = new_status
            
            # If interview is completed, update timestamp and application status
            if new_status == InterviewStatus.COMPLETED and not interview.completed_at:
                interview.completed_at = datetime.utcnow()
                
                # Log activity for interview completion
                activity = Activity(
                    user_id=current_user.id,
                    candidate_id=interview.candidate_id,
                    application_id=interview.application_id,
                    activity_type=ActivityType.INTERVIEW_COMPLETED,
                    description=f"Interview completed for {interview.candidate.full_name}",
                    details={
                        "interview_type": interview.interview_type.value,
                        "overall_score": interview.overall_score
                    }
                )
                db.session.add(activity)
            
            # Log status change
            if old_status != new_status:
                activity = Activity(
                    user_id=current_user.id,
                    candidate_id=interview.candidate_id,
                    application_id=interview.application_id,
                    activity_type=ActivityType.STATUS_CHANGE,
                    description=f"Interview status changed from {old_status.value} to {new_status.value}",
                    details={"old_status": old_status.value, "new_status": new_status.value}
                )
                db.session.add(activity)
        except ValueError:
            return jsonify({'message': 'Invalid status value!'}), 400
    
    # Update other fields
    for field in [
        'duration_minutes', 'location', 'meeting_link', 'interviewer_id', 
        'client_interviewer_id', 'technical_score', 'communication_score', 
        'culture_fit_score', 'overall_score', 'strengths', 'weaknesses', 
        'notes', 'recommendation'
    ]:
        if field in data:
            setattr(interview, field, data[field])
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        candidate_id=interview.candidate_id,
        application_id=interview.application_id,
        activity_type=ActivityType.SYSTEM_ACTION,
        description=f"Interview updated for {interview.candidate.full_name}"
    )
    db.session.add(activity)
    
    db.session.commit()
    
    return jsonify({'message': 'Interview updated successfully!'})

@interviews_bp.route('/<int:interview_id>', methods=['DELETE'])
@token_required
@role_required([UserRole.ADMIN, UserRole.MANAGER])
def delete_interview(current_user, interview_id):
    interview = Interview.query.get_or_404(interview_id)
    
    # Log activity before deletion
    activity = Activity(
        user_id=current_user.id,
        candidate_id=interview.candidate_id,
        application_id=interview.application_id,
        activity_type=ActivityType.SYSTEM_ACTION,
        description=f"Interview deleted for {interview.candidate.full_name} scheduled on {interview.scheduled_at.strftime('%Y-%m-%d %H:%M')}"
    )
    db.session.add(activity)
    
    db.session.delete(interview)
    db.session.commit()
    
    return jsonify({'message': 'Interview deleted successfully!'})

@interviews_bp.route('/calendar', methods=['GET'])
@token_required
def get_interview_calendar(current_user):
    # Get query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Default to current week if not specified
    if not start_date:
        today = datetime.utcnow().date()
        start_date = (today - timedelta(days=today.weekday())).isoformat()  # Monday
    
    if not end_date:
        start = datetime.fromisoformat(start_date).date()
        end_date = (start + timedelta(days=6)).isoformat()  # Sunday
    
    # Parse dates
    try:
        from_date = datetime.fromisoformat(start_date)
        to_date = datetime.fromisoformat(end_date)
        to_date = datetime.combine(to_date.date(), datetime.max.time())  # End of day
    except ValueError:
        return jsonify({'message': 'Invalid date format!'}), 400
    
    # Get interviews in date range
    interviews = Interview.query.filter(
        Interview.scheduled_at >= from_date,
        Interview.scheduled_at <= to_date
    ).order_by(Interview.scheduled_at).all()
    
    # Format response
    calendar_events = []
    for interview in interviews:
        end_time = interview.scheduled_at + timedelta(minutes=interview.duration_minutes)
        calendar_events.append({
            'id': interview.id,
            'title': f"{interview.candidate.full_name} - {interview.interview_type.value.capitalize()}",
            'start': interview.scheduled_at.isoformat(),
            'end': end_time.isoformat(),
            'candidate_id': interview.candidate_id,
            'candidate_name': interview.candidate.full_name,
            'job_title': interview.application.job_position.title,
            'status': interview.status.value,
            'location': interview.location,
            'meeting_link': interview.meeting_link,
            'interviewer_id': interview.interviewer_id,
            'interviewer_name': interview.interviewer.full_name if interview.interviewer else None
        })
    
    return jsonify({'events': calendar_events})

@interviews_bp.route('/statistics', methods=['GET'])
@token_required
def get_interview_statistics(current_user):
    # Count interviews by status
    status_counts = {}
    for status in InterviewStatus:
        count = Interview.query.filter_by(status=status).count()
        status_counts[status.value] = count
    
    # Count interviews by type
    type_counts = {}
    for interview_type in InterviewType:
        count = Interview.query.filter_by(interview_type=interview_type).count()
        type_counts[interview_type.value] = count
    
    # Calculate average scores
    avg_technical = db.session.query(db.func.avg(Interview.technical_score)).scalar() or 0
    avg_communication = db.session.query(db.func.avg(Interview.communication_score)).scalar() or 0
    avg_culture_fit = db.session.query(db.func.avg(Interview.culture_fit_score)).scalar() or 0
    avg_overall = db.session.query(db.func.avg(Interview.overall_score)).scalar() or 0
    
    # Calculate no-show rate
    total_interviews = Interview.query.count()
    no_show_count = Interview.query.filter_by(status=InterviewStatus.NO_SHOW).count()
    no_show_rate = (no_show_count / total_interviews) * 100 if total_interviews > 0 else 0
    
    # Upcoming interviews
    upcoming_interviews = Interview.query.filter(
        Interview.scheduled_at > datetime.utcnow(),
        Interview.status == InterviewStatus.SCHEDULED
    ).order_by(Interview.scheduled_at).limit(5).all()
    
    upcoming_data = [{
        'id': i.id,
        'candidate_name': i.candidate.full_name,
        'job_title': i.application.job_position.title,
        'interview_type': i.interview_type.value,
        'scheduled_at': i.scheduled_at.isoformat()
    } for i in upcoming_interviews]
    
    return jsonify({
        'total_interviews': total_interviews,
        'completed_interviews': Interview.query.filter_by(status=InterviewStatus.COMPLETED).count(),
        'status_distribution': status_counts,
        'type_distribution': type_counts,
        'average_scores': {
            'technical': round(avg_technical, 1),
            'communication': round(avg_communication, 1),
            'culture_fit': round(avg_culture_fit, 1),
            'overall': round(avg_overall, 1)
        },
        'no_show_rate': round(no_show_rate, 1),
        'upcoming_interviews': upcoming_data
    })
