from flask import Blueprint, request, jsonify
from src.models.user import db, User, UserRole
from src.models.job_position import JobPosition, JobType, JobLevel, JobStatus
from src.models.client import Client
from src.models.activity import Activity, ActivityType
from src.routes.auth import token_required, role_required
from datetime import datetime

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/', methods=['GET'])
@token_required
def get_jobs(current_user):
    # Get query parameters for filtering
    status = request.args.get('status')
    search = request.args.get('search')
    client_id = request.args.get('client_id', type=int)
    job_type = request.args.get('job_type')
    job_level = request.args.get('job_level')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Base query
    query = JobPosition.query
    
    # Apply filters
    if status:
        try:
            status_enum = JobStatus(status)
            query = query.filter_by(status=status_enum)
        except ValueError:
            return jsonify({'message': 'Invalid status value'}), 400
    
    if job_type:
        try:
            job_type_enum = JobType(job_type)
            query = query.filter_by(job_type=job_type_enum)
        except ValueError:
            return jsonify({'message': 'Invalid job type value'}), 400
    
    if job_level:
        try:
            job_level_enum = JobLevel(job_level)
            query = query.filter_by(job_level=job_level_enum)
        except ValueError:
            return jsonify({'message': 'Invalid job level value'}), 400
    
    if client_id:
        query = query.filter_by(client_id=client_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (JobPosition.title.ilike(search_term)) | 
            (JobPosition.description.ilike(search_term)) |
            (JobPosition.location.ilike(search_term))
        )
    
    # Pagination
    jobs_pagination = query.order_by(JobPosition.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # Format response
    jobs_list = []
    for job in jobs_pagination.items:
        jobs_list.append({
            'id': job.id,
            'title': job.title,
            'client_id': job.client_id,
            'client_name': job.client.company_name,
            'job_type': job.job_type.value,
            'job_level': job.job_level.value if job.job_level else None,
            'location': job.location,
            'remote_option': job.remote_option,
            'status': job.status.value,
            'vacancies': job.vacancies,
            'applications_count': job.applications_count,
            'created_at': job.created_at.isoformat()
        })
    
    return jsonify({
        'jobs': jobs_list,
        'total': jobs_pagination.total,
        'pages': jobs_pagination.pages,
        'current_page': jobs_pagination.page
    })

@jobs_bp.route('/<int:job_id>', methods=['GET'])
@token_required
def get_job(current_user, job_id):
    job = JobPosition.query.get_or_404(job_id)
    
    # Format response with all details
    job_data = {
        'id': job.id,
        'client_id': job.client_id,
        'client_name': job.client.company_name,
        'title': job.title,
        'description': job.description,
        'requirements': job.requirements,
        'responsibilities': job.responsibilities,
        'benefits': job.benefits,
        'job_type': job.job_type.value,
        'job_level': job.job_level.value if job.job_level else None,
        'location': job.location,
        'remote_option': job.remote_option,
        'department': job.department,
        'salary_min': job.salary_min,
        'salary_max': job.salary_max,
        'salary_currency': job.salary_currency,
        'salary_is_public': job.salary_is_public,
        'vacancies': job.vacancies,
        'status': job.status.value,
        'start_date': job.start_date.isoformat() if job.start_date else None,
        'end_date': job.end_date.isoformat() if job.end_date else None,
        'priority': job.priority,
        'views_count': job.views_count,
        'applications_count': job.applications_count,
        'time_to_fill': job.time_to_fill,
        'created_at': job.created_at.isoformat(),
        'updated_at': job.updated_at.isoformat()
    }
    
    return jsonify({'job': job_data})

@jobs_bp.route('/', methods=['POST'])
@token_required
@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER])
def create_job(current_user):
    data = request.get_json()
    
    # Validate required fields
    if not data.get('title') or not data.get('client_id'):
        return jsonify({'message': 'Job title and client ID are required!'}), 400
    
    # Verify client exists
    client = Client.query.get(data['client_id'])
    if not client:
        return jsonify({'message': 'Client not found!'}), 404
    
    # Process enums
    job_type = JobType.FULL_TIME
    if data.get('job_type'):
        try:
            job_type = JobType(data['job_type'])
        except ValueError:
            return jsonify({'message': 'Invalid job type value!'}), 400
    
    job_level = None
    if data.get('job_level'):
        try:
            job_level = JobLevel(data['job_level'])
        except ValueError:
            return jsonify({'message': 'Invalid job level value!'}), 400
    
    status = JobStatus.DRAFT
    if data.get('status'):
        try:
            status = JobStatus(data['status'])
        except ValueError:
            return jsonify({'message': 'Invalid status value!'}), 400
    
    # Process date fields
    start_date = None
    if data.get('start_date'):
        try:
            start_date = datetime.fromisoformat(data['start_date'])
        except ValueError:
            return jsonify({'message': 'Invalid date format for start_date!'}), 400
    
    end_date = None
    if data.get('end_date'):
        try:
            end_date = datetime.fromisoformat(data['end_date'])
        except ValueError:
            return jsonify({'message': 'Invalid date format for end_date!'}), 400
    
    # Create new job position
    new_job = JobPosition(
        client_id=data['client_id'],
        title=data['title'],
        description=data.get('description', ''),
        requirements=data.get('requirements'),
        responsibilities=data.get('responsibilities'),
        benefits=data.get('benefits'),
        job_type=job_type,
        job_level=job_level,
        location=data.get('location'),
        remote_option=data.get('remote_option', False),
        department=data.get('department'),
        salary_min=data.get('salary_min'),
        salary_max=data.get('salary_max'),
        salary_currency=data.get('salary_currency', 'VND'),
        salary_is_public=data.get('salary_is_public', False),
        vacancies=data.get('vacancies', 1),
        status=status,
        start_date=start_date,
        end_date=end_date,
        priority=data.get('priority', 1)
    )
    
    db.session.add(new_job)
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        job_position_id=new_job.id,
        activity_type=ActivityType.SYSTEM_ACTION,
        description=f"Job position '{data['title']}' created"
    )
    db.session.add(activity)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Job position created successfully!',
        'job_id': new_job.id
    }), 201

@jobs_bp.route('/<int:job_id>', methods=['PUT'])
@token_required
@role_required([UserRole.ADMIN, UserRole.MANAGER, UserRole.RECRUITER])
def update_job(current_user, job_id):
    job = JobPosition.query.get_or_404(job_id)
    data = request.get_json()
    
    # Update basic fields
    if 'title' in data:
        job.title = data['title']
    
    if 'description' in data:
        job.description = data['description']
    
    # Process enums
    if 'job_type' in data:
        try:
            job.job_type = JobType(data['job_type'])
        except ValueError:
            return jsonify({'message': 'Invalid job type value!'}), 400
    
    if 'job_level' in data:
        try:
            job.job_level = JobLevel(data['job_level']) if data['job_level'] else None
        except ValueError:
            return jsonify({'message': 'Invalid job level value!'}), 400
    
    if 'status' in data:
        old_status = job.status
        try:
            new_status = JobStatus(data['status'])
            job.status = new_status
            
            # Log status change
            if old_status != new_status:
                activity = Activity(
                    user_id=current_user.id,
                    job_position_id=job.id,
                    activity_type=ActivityType.STATUS_CHANGE,
                    description=f"Job status changed from {old_status.value} to {new_status.value}",
                    details={"old_status": old_status.value, "new_status": new_status.value}
                )
                db.session.add(activity)
        except ValueError:
            return jsonify({'message': 'Invalid status value!'}), 400
    
    # Process date fields
    if 'start_date' in data:
        try:
            job.start_date = datetime.fromisoformat(data['start_date']) if data['start_date'] else None
        except ValueError:
            return jsonify({'message': 'Invalid date format for start_date!'}), 400
    
    if 'end_date' in data:
        try:
            job.end_date = datetime.fromisoformat(data['end_date']) if data['end_date'] else None
        except ValueError:
            return jsonify({'message': 'Invalid date format for end_date!'}), 400
    
    # Update other fields
    for field in [
        'requirements', 'responsibilities', 'benefits', 'location', 
        'remote_option', 'department', 'salary_min', 'salary_max', 
        'salary_currency', 'salary_is_public', 'vacancies', 'priority'
    ]:
        if field in data:
            setattr(job, field, data[field])
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        job_position_id=job.id,
        activity_type=ActivityType.SYSTEM_ACTION,
        description=f"Job position '{job.title}' updated"
    )
    db.session.add(activity)
    
    db.session.commit()
    
    return jsonify({'message': 'Job position updated successfully!'})

@jobs_bp.route('/<int:job_id>', methods=['DELETE'])
@token_required
@role_required([UserRole.ADMIN, UserRole.MANAGER])
def delete_job(current_user, job_id):
    job = JobPosition.query.get_or_404(job_id)
    
    # Log activity before deletion
    activity = Activity(
        user_id=current_user.id,
        activity_type=ActivityType.SYSTEM_ACTION,
        description=f"Job position '{job.title}' deleted"
    )
    db.session.add(activity)
    
    db.session.delete(job)
    db.session.commit()
    
    return jsonify({'message': 'Job position deleted successfully!'})

@jobs_bp.route('/statistics', methods=['GET'])
@token_required
def get_job_statistics(current_user):
    # Count jobs by status
    status_counts = {}
    for status in JobStatus:
        count = JobPosition.query.filter_by(status=status).count()
        status_counts[status.value] = count
    
    # Count jobs by type
    type_counts = {}
    for job_type in JobType:
        count = JobPosition.query.filter_by(job_type=job_type).count()
        type_counts[job_type.value] = count
    
    # Count jobs by level
    level_counts = {}
    for level in JobLevel:
        count = JobPosition.query.filter_by(job_level=level).count()
        level_counts[level.value] = count
    
    # Top locations
    location_counts = db.session.query(
        JobPosition.location, db.func.count(JobPosition.id)
    ).group_by(JobPosition.location).order_by(db.func.count(JobPosition.id).desc()).limit(5).all()
    
    location_data = {location: count for location, count in location_counts if location}
    
    # Recent jobs
    recent_jobs = JobPosition.query.order_by(JobPosition.created_at.desc()).limit(5).all()
    recent_data = [{
        'id': j.id,
        'title': j.title,
        'client_name': j.client.company_name,
        'status': j.status.value,
        'created_at': j.created_at.isoformat()
    } for j in recent_jobs]
    
    return jsonify({
        'total_jobs': JobPosition.query.count(),
        'open_jobs': JobPosition.query.filter_by(status=JobStatus.OPEN).count(),
        'status_distribution': status_counts,
        'type_distribution': type_counts,
        'level_distribution': level_counts,
        'top_locations': location_data,
        'recent_jobs': recent_data
    })
