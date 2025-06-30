from flask import Blueprint, request, jsonify
from src.models.user import db, User, UserRole
from src.models.candidate import Candidate, CandidateStatus
from src.models.job_position import JobPosition
from src.models.application import Application, ApplicationStatus
from src.models.activity import Activity, ActivityType
from src.routes.auth import token_required, role_required
from datetime import datetime

applications_bp = Blueprint('applications', __name__)

@applications_bp.route('/', methods=['GET'])
@token_required
def get_applications(current_user):
    # Get query parameters for filtering
    status = request.args.get('status')
    candidate_id = request.args.get('candidate_id', type=int)
    job_id = request.args.get('job_id', type=int)
    recruiter_id = request.args.get('recruiter_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Base query
    query = Application.query
    
    # Apply filters
    if status:
        try:
            status_enum = ApplicationStatus(status)
            query = query.filter_by(status=status_enum)
        except ValueError:
            return jsonify({'message': 'Invalid status value'}), 400
    
    if candidate_id:
        query = query.filter_by(candidate_id=candidate_id)
    
    if job_id:
        query = query.filter_by(job_position_id=job_id)
    
    if recruiter_id:
        query = query.filter_by(recruiter_id=recruiter_id)
    
    # Pagination
    applications_pagination = query.order_by(Application.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # Format response
    applications_list = []
    for application in applications_pagination.items:
        applications_list.append({
            'id': application.id,
            'candidate_id': application.candidate_id,
            'candidate_name': application.candidate.full_name,
            'job_position_id': application.job_position_id,
            'job_title': application.job_position.title,
            'status': application.status.value,
            'current_stage': application.current_stage,
            'recruiter_id': application.recruiter_id,
            'recruiter_name': application.recruiter.full_name if application.recruiter else None,
            'candidate_score': application.candidate_score,
            'applied_at': application.applied_at.isoformat(),
            'updated_at': application.updated_at.isoformat()
        })
    
    return jsonify({
        'applications': applications_list,
        'total': applications_pagination.total,
        'pages': applications_pagination.pages,
        'current_page': applications_pagination.page
    })

@applications_bp.route('/<int:application_id>', methods=['GET'])
@token_required
def get_application(current_user, application_id):
    application = Application.query.get_or_404(application_id)
    
    # Format response with all details
    application_data = {
        'id': application.id,
        'candidate_id': application.candidate_id,
        'candidate_name': application.candidate.full_name,
        'job_position_id': application.job_position_id,
        'job_title': application.job_position.title,
        'status': application.status.value,
        'cover_letter': application.cover_letter,
        'expected_salary': application.expected_salary,
        'availability_date': application.availability_date.isoformat() if application.availability_date else None,
        'recruiter_id': application.recruiter_id,
        'recruiter_name': application.recruiter.full_name if application.recruiter else None,
        'recruiter_notes': application.recruiter_notes,
        'candidate_score': application.candidate_score,
        'current_stage': application.current_stage,
        'is_active': application.is_active,
        'applied_at': application.applied_at.isoformat(),
        'screened_at': application.screened_at.isoformat() if application.screened_at else None,
        'interviewed_at': application.interviewed_at.isoformat() if application.interviewed_at else None,
        'shortlisted_at': application.shortlisted_at.isoformat() if application.shortlisted_at else None,
        'client_reviewed_at': application.client_reviewed_at.isoformat() if application.client_reviewed_at else None,
        'hired_at': application.hired_at.isoformat() if application.hired_at else None,
        'rejected_at': application.rejected_at.isoformat() if application.rejected_at else None,
        'withdrawn_at': application.withdrawn_at.isoformat() if application.withdrawn_at else None,
        'time_to_screen': application.time_to_screen,
        'time_to_interview': application.time_to_interview,
        'time_to_decision': application.time_to_decision,
        'created_at': application.created_at.isoformat(),
        'updated_at': application.updated_at.isoformat()
    }
    
    return jsonify({'application': application_data})

@applications_bp.route('/', methods=['POST'])
@token_required
def create_application(current_user):
    data = request.get_json()
    
    # Validate required fields
    if not data.get('candidate_id') or not data.get('job_position_id'):
        return jsonify({'message': 'Candidate ID and Job Position ID are required!'}), 400
    
    # Verify candidate and job position exist
    candidate = Candidate.query.get(data['candidate_id'])
    if not candidate:
        return jsonify({'message': 'Candidate not found!'}), 404
    
    job_position = JobPosition.query.get(data['job_position_id'])
    if not job_position:
        return jsonify({'message': 'Job position not found!'}), 404
    
    # Check if application already exists
    existing_application = Application.query.filter_by(
        candidate_id=data['candidate_id'],
        job_position_id=data['job_position_id']
    ).first()
    
    if existing_application:
        return jsonify({'message': 'Application already exists!'}), 409
    
    # Process date fields
    availability_date = None
    if data.get('availability_date'):
        try:
            availability_date = datetime.fromisoformat(data['availability_date'])
        except ValueError:
            return jsonify({'message': 'Invalid date format for availability_date!'}), 400
    
    # Create new application
    new_application = Application(
        candidate_id=data['candidate_id'],
        job_position_id=data['job_position_id'],
        status=ApplicationStatus.NEW,
        cover_letter=data.get('cover_letter'),
        expected_salary=data.get('expected_salary'),
        availability_date=availability_date,
        recruiter_id=current_user.id if current_user.role in [UserRole.RECRUITER, UserRole.MANAGER, UserRole.ADMIN] else None,
        recruiter_notes=data.get('recruiter_notes'),
        candidate_score=data.get('candidate_score'),
        current_stage="Applied"
    )
    
    db.session.add(new_application)
    
    # Update job position applications count
    job_position.applications_count += 1
    
    # Update candidate status
    candidate.status = CandidateStatus.NEW
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        candidate_id=data['candidate_id'],
        job_position_id=data['job_position_id'],
        application_id=new_application.id,
        activity_type=ActivityType.SYSTEM_ACTION,
        description=f"Application created for {candidate.full_name} to {job_position.title}"
    )
    db.session.add(activity)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Application created successfully!',
        'application_id': new_application.id
    }), 201

@applications_bp.route('/<int:application_id>', methods=['PUT'])
@token_required
def update_application(current_user, application_id):
    application = Application.query.get_or_404(application_id)
    data = request.get_json()
    
    # Update basic fields
    if 'cover_letter' in data:
        application.cover_letter = data['cover_letter']
    
    if 'expected_salary' in data:
        application.expected_salary = data['expected_salary']
    
    if 'recruiter_notes' in data:
        application.recruiter_notes = data['recruiter_notes']
    
    if 'candidate_score' in data:
        application.candidate_score = data['candidate_score']
    
    if 'current_stage' in data:
        application.current_stage = data['current_stage']
    
    if 'is_active' in data:
        application.is_active = data['is_active']
    
    # Process date fields
    if 'availability_date' in data:
        try:
            application.availability_date = datetime.fromisoformat(data['availability_date']) if data['availability_date'] else None
        except ValueError:
            return jsonify({'message': 'Invalid date format for availability_date!'}), 400
    
    # Handle status change
    if 'status' in data:
        old_status = application.status
        try:
            new_status = ApplicationStatus(data['status'])
            
            # Update status-specific timestamps
            if new_status == ApplicationStatus.SCREENING and not application.screened_at:
                application.screened_at = datetime.utcnow()
                if application.applied_at:
                    time_diff = application.screened_at - application.applied_at
                    application.time_to_screen = int(time_diff.total_seconds() / 3600)  # Hours
            
            elif new_status == ApplicationStatus.INTERVIEW and not application.interviewed_at:
                application.interviewed_at = datetime.utcnow()
                if application.screened_at:
                    time_diff = application.interviewed_at - application.screened_at
                    application.time_to_interview = int(time_diff.total_seconds() / 3600)  # Hours
            
            elif new_status == ApplicationStatus.SHORTLISTED and not application.shortlisted_at:
                application.shortlisted_at = datetime.utcnow()
            
            elif new_status == ApplicationStatus.CLIENT_REVIEW and not application.client_reviewed_at:
                application.client_reviewed_at = datetime.utcnow()
            
            elif new_status == ApplicationStatus.HIRED and not application.hired_at:
                application.hired_at = datetime.utcnow()
                if application.interviewed_at:
                    time_diff = application.hired_at - application.interviewed_at
                    application.time_to_decision = int(time_diff.total_seconds() / 3600)  # Hours
            
            elif new_status == ApplicationStatus.REJECTED and not application.rejected_at:
                application.rejected_at = datetime.utcnow()
                if application.interviewed_at:
                    time_diff = application.rejected_at - application.interviewed_at
                    application.time_to_decision = int(time_diff.total_seconds() / 3600)  # Hours
            
            elif new_status == ApplicationStatus.WITHDRAWN and not application.withdrawn_at:
                application.withdrawn_at = datetime.utcnow()
            
            application.status = new_status
            
            # Update candidate status
            application.update_candidate_status()
            
            # Log status change
            if old_status != new_status:
                activity = Activity(
                    user_id=current_user.id,
                    candidate_id=application.candidate_id,
                    job_position_id=application.job_position_id,
                    application_id=application.id,
                    activity_type=ActivityType.STATUS_CHANGE,
                    description=f"Application status changed from {old_status.value} to {new_status.value}",
                    details={"old_status": old_status.value, "new_status": new_status.value}
                )
                db.session.add(activity)
        except ValueError:
            return jsonify({'message': 'Invalid status value!'}), 400
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        candidate_id=application.candidate_id,
        job_position_id=application.job_position_id,
        application_id=application.id,
        activity_type=ActivityType.SYSTEM_ACTION,
        description=f"Application updated for {application.candidate.full_name}"
    )
    db.session.add(activity)
    
    db.session.commit()
    
    return jsonify({'message': 'Application updated successfully!'})

@applications_bp.route('/<int:application_id>', methods=['DELETE'])
@token_required
@role_required([UserRole.ADMIN, UserRole.MANAGER])
def delete_application(current_user, application_id):
    application = Application.query.get_or_404(application_id)
    
    # Log activity before deletion
    activity = Activity(
        user_id=current_user.id,
        candidate_id=application.candidate_id,
        job_position_id=application.job_position_id,
        activity_type=ActivityType.SYSTEM_ACTION,
        description=f"Application deleted for {application.candidate.full_name} to {application.job_position.title}"
    )
    db.session.add(activity)
    
    # Update job position applications count
    job_position = application.job_position
    if job_position.applications_count > 0:
        job_position.applications_count -= 1
    
    db.session.delete(application)
    db.session.commit()
    
    return jsonify({'message': 'Application deleted successfully!'})

@applications_bp.route('/statistics', methods=['GET'])
@token_required
def get_application_statistics(current_user):
    # Count applications by status
    status_counts = {}
    for status in ApplicationStatus:
        count = Application.query.filter_by(status=status).count()
        status_counts[status.value] = count
    
    # Calculate average times
    avg_time_to_screen = db.session.query(db.func.avg(Application.time_to_screen)).scalar() or 0
    avg_time_to_interview = db.session.query(db.func.avg(Application.time_to_interview)).scalar() or 0
    avg_time_to_decision = db.session.query(db.func.avg(Application.time_to_decision)).scalar() or 0
    
    # Calculate conversion rates
    total_applications = Application.query.count()
    screened_count = Application.query.filter(Application.screened_at.isnot(None)).count()
    interviewed_count = Application.query.filter(Application.interviewed_at.isnot(None)).count()
    hired_count = Application.query.filter(Application.hired_at.isnot(None)).count()
    
    screen_rate = (screened_count / total_applications) * 100 if total_applications > 0 else 0
    interview_rate = (interviewed_count / screened_count) * 100 if screened_count > 0 else 0
    hire_rate = (hired_count / interviewed_count) * 100 if interviewed_count > 0 else 0
    
    # Recent applications
    recent_applications = Application.query.order_by(Application.created_at.desc()).limit(5).all()
    recent_data = [{
        'id': a.id,
        'candidate_name': a.candidate.full_name,
        'job_title': a.job_position.title,
        'status': a.status.value,
        'applied_at': a.applied_at.isoformat()
    } for a in recent_applications]
    
    return jsonify({
        'total_applications': total_applications,
        'status_distribution': status_counts,
        'time_metrics': {
            'avg_time_to_screen': round(avg_time_to_screen, 1),  # Hours
            'avg_time_to_interview': round(avg_time_to_interview, 1),  # Hours
            'avg_time_to_decision': round(avg_time_to_decision, 1)  # Hours
        },
        'conversion_rates': {
            'screen_rate': round(screen_rate, 1),  # Percentage
            'interview_rate': round(interview_rate, 1),  # Percentage
            'hire_rate': round(hire_rate, 1)  # Percentage
        },
        'recent_applications': recent_data
    })
