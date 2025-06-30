from flask import Blueprint, request, jsonify
from src.models.user import db, User, UserRole
from src.models.candidate import Candidate, CandidateStatus, Gender, EducationLevel
from src.models.activity import Activity, ActivityType
from src.routes.auth import token_required, role_required
from datetime import datetime
import os

candidates_bp = Blueprint('candidates', __name__)

@candidates_bp.route('/', methods=['GET'])
@token_required
def get_candidates(current_user):
    # Get query parameters for filtering
    status = request.args.get('status')
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Base query
    query = Candidate.query
    
    # Apply filters
    if status:
        try:
            status_enum = CandidateStatus(status)
            query = query.filter_by(status=status_enum)
        except ValueError:
            return jsonify({'message': 'Invalid status value'}), 400
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Candidate.full_name.ilike(search_term)) | 
            (Candidate.email.ilike(search_term)) |
            (Candidate.phone.ilike(search_term)) |
            (Candidate.skills.ilike(search_term))
        )
    
    # Pagination
    candidates_pagination = query.order_by(Candidate.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # Format response
    candidates_list = []
    for candidate in candidates_pagination.items:
        candidates_list.append({
            'id': candidate.id,
            'full_name': candidate.full_name,
            'email': candidate.email,
            'phone': candidate.phone,
            'status': candidate.status.value,
            'years_of_experience': candidate.years_of_experience,
            'skills': candidate.skills,
            'current_position': candidate.current_position,
            'created_at': candidate.created_at.isoformat()
        })
    
    return jsonify({
        'candidates': candidates_list,
        'total': candidates_pagination.total,
        'pages': candidates_pagination.pages,
        'current_page': candidates_pagination.page
    })

@candidates_bp.route('/<int:candidate_id>', methods=['GET'])
@token_required
def get_candidate(current_user, candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    
    # Format response with all details
    candidate_data = {
        'id': candidate.id,
        'full_name': candidate.full_name,
        'email': candidate.email,
        'phone': candidate.phone,
        'date_of_birth': candidate.date_of_birth.isoformat() if candidate.date_of_birth else None,
        'gender': candidate.gender.value if candidate.gender else None,
        'address': candidate.address,
        'city': candidate.city,
        'province': candidate.province,
        'country': candidate.country,
        'education_level': candidate.education_level.value if candidate.education_level else None,
        'major': candidate.major,
        'university': candidate.university,
        'skills': candidate.skills,
        'languages': candidate.languages,
        'years_of_experience': candidate.years_of_experience,
        'resume_url': candidate.resume_url,
        'portfolio_url': candidate.portfolio_url,
        'current_employer': candidate.current_employer,
        'current_position': candidate.current_position,
        'current_salary': candidate.current_salary,
        'expected_salary': candidate.expected_salary,
        'status': candidate.status.value,
        'source': candidate.source,
        'notes': candidate.notes,
        'quality_score': candidate.quality_score,
        'last_contact_date': candidate.last_contact_date.isoformat() if candidate.last_contact_date else None,
        'created_at': candidate.created_at.isoformat(),
        'updated_at': candidate.updated_at.isoformat()
    }
    
    return jsonify({'candidate': candidate_data})

@candidates_bp.route('/', methods=['POST'])
@token_required
def create_candidate(current_user):
    data = request.get_json()
    
    # Validate required fields
    if not data.get('full_name') or not data.get('email'):
        return jsonify({'message': 'Full name and email are required!'}), 400
    
    # Check if candidate already exists
    if Candidate.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Candidate with this email already exists!'}), 409
    
    # Process enums
    gender = None
    if data.get('gender'):
        try:
            gender = Gender(data['gender'])
        except ValueError:
            return jsonify({'message': 'Invalid gender value!'}), 400
    
    education_level = None
    if data.get('education_level'):
        try:
            education_level = EducationLevel(data['education_level'])
        except ValueError:
            return jsonify({'message': 'Invalid education level value!'}), 400
    
    status = CandidateStatus.NEW
    if data.get('status'):
        try:
            status = CandidateStatus(data['status'])
        except ValueError:
            return jsonify({'message': 'Invalid status value!'}), 400
    
    # Process date fields
    date_of_birth = None
    if data.get('date_of_birth'):
        try:
            date_of_birth = datetime.fromisoformat(data['date_of_birth'])
        except ValueError:
            return jsonify({'message': 'Invalid date format for date_of_birth!'}), 400
    
    # Create new candidate
    new_candidate = Candidate(
        full_name=data['full_name'],
        email=data['email'],
        phone=data.get('phone'),
        date_of_birth=date_of_birth,
        gender=gender,
        address=data.get('address'),
        city=data.get('city'),
        province=data.get('province'),
        country=data.get('country', 'Vietnam'),
        education_level=education_level,
        major=data.get('major'),
        university=data.get('university'),
        skills=data.get('skills'),
        languages=data.get('languages'),
        years_of_experience=data.get('years_of_experience'),
        resume_url=data.get('resume_url'),
        portfolio_url=data.get('portfolio_url'),
        current_employer=data.get('current_employer'),
        current_position=data.get('current_position'),
        current_salary=data.get('current_salary'),
        expected_salary=data.get('expected_salary'),
        status=status,
        source=data.get('source'),
        notes=data.get('notes')
    )
    
    db.session.add(new_candidate)
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        candidate_id=new_candidate.id,
        activity_type=ActivityType.SYSTEM_ACTION,
        description=f"Candidate {data['full_name']} created"
    )
    db.session.add(activity)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Candidate created successfully!',
        'candidate_id': new_candidate.id
    }), 201

@candidates_bp.route('/<int:candidate_id>', methods=['PUT'])
@token_required
def update_candidate(current_user, candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    data = request.get_json()
    
    # Update basic fields
    if 'full_name' in data:
        candidate.full_name = data['full_name']
    
    if 'email' in data:
        candidate.email = data['email']
    
    if 'phone' in data:
        candidate.phone = data['phone']
    
    # Process enums
    if 'gender' in data:
        try:
            candidate.gender = Gender(data['gender']) if data['gender'] else None
        except ValueError:
            return jsonify({'message': 'Invalid gender value!'}), 400
    
    if 'education_level' in data:
        try:
            candidate.education_level = EducationLevel(data['education_level']) if data['education_level'] else None
        except ValueError:
            return jsonify({'message': 'Invalid education level value!'}), 400
    
    if 'status' in data:
        old_status = candidate.status
        try:
            new_status = CandidateStatus(data['status'])
            candidate.status = new_status
            
            # Log status change
            if old_status != new_status:
                activity = Activity(
                    user_id=current_user.id,
                    candidate_id=candidate.id,
                    activity_type=ActivityType.STATUS_CHANGE,
                    description=f"Candidate status changed from {old_status.value} to {new_status.value}",
                    details={"old_status": old_status.value, "new_status": new_status.value}
                )
                db.session.add(activity)
        except ValueError:
            return jsonify({'message': 'Invalid status value!'}), 400
    
    # Process date fields
    if 'date_of_birth' in data:
        try:
            candidate.date_of_birth = datetime.fromisoformat(data['date_of_birth']) if data['date_of_birth'] else None
        except ValueError:
            return jsonify({'message': 'Invalid date format for date_of_birth!'}), 400
    
    # Update other fields
    for field in [
        'address', 'city', 'province', 'country', 'major', 'university', 
        'skills', 'languages', 'years_of_experience', 'resume_url', 
        'portfolio_url', 'current_employer', 'current_position', 
        'current_salary', 'expected_salary', 'source', 'notes'
    ]:
        if field in data:
            setattr(candidate, field, data[field])
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        candidate_id=candidate.id,
        activity_type=ActivityType.SYSTEM_ACTION,
        description=f"Candidate {candidate.full_name} updated"
    )
    db.session.add(activity)
    
    db.session.commit()
    
    return jsonify({'message': 'Candidate updated successfully!'})

@candidates_bp.route('/<int:candidate_id>', methods=['DELETE'])
@token_required
@role_required([UserRole.ADMIN, UserRole.MANAGER])
def delete_candidate(current_user, candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    
    # Log activity before deletion
    activity = Activity(
        user_id=current_user.id,
        activity_type=ActivityType.SYSTEM_ACTION,
        description=f"Candidate {candidate.full_name} deleted"
    )
    db.session.add(activity)
    
    db.session.delete(candidate)
    db.session.commit()
    
    return jsonify({'message': 'Candidate deleted successfully!'})

@candidates_bp.route('/<int:candidate_id>/notes', methods=['POST'])
@token_required
def add_candidate_note(current_user, candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    data = request.get_json()
    
    if not data.get('note'):
        return jsonify({'message': 'Note content is required!'}), 400
    
    # Update candidate notes
    if candidate.notes:
        candidate.notes += f"\n\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')} by {current_user.full_name}]\n{data['note']}"
    else:
        candidate.notes = f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')} by {current_user.full_name}]\n{data['note']}"
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        candidate_id=candidate.id,
        activity_type=ActivityType.NOTE_ADDED,
        description=f"Note added to candidate {candidate.full_name}",
        details={"note": data['note']}
    )
    db.session.add(activity)
    
    db.session.commit()
    
    return jsonify({'message': 'Note added successfully!'})

@candidates_bp.route('/statistics', methods=['GET'])
@token_required
def get_candidate_statistics(current_user):
    # Count candidates by status
    status_counts = {}
    for status in CandidateStatus:
        count = Candidate.query.filter_by(status=status).count()
        status_counts[status.value] = count
    
    # Count candidates by source
    source_counts = db.session.query(
        Candidate.source, db.func.count(Candidate.id)
    ).group_by(Candidate.source).all()
    
    source_data = {source: count for source, count in source_counts if source}
    
    # Count candidates by education level
    education_counts = {}
    for level in EducationLevel:
        count = Candidate.query.filter_by(education_level=level).count()
        education_counts[level.value] = count
    
    # Recent activity
    recent_candidates = Candidate.query.order_by(Candidate.created_at.desc()).limit(5).all()
    recent_data = [{
        'id': c.id,
        'full_name': c.full_name,
        'email': c.email,
        'status': c.status.value,
        'created_at': c.created_at.isoformat()
    } for c in recent_candidates]
    
    return jsonify({
        'total_candidates': Candidate.query.count(),
        'status_distribution': status_counts,
        'source_distribution': source_data,
        'education_distribution': education_counts,
        'recent_candidates': recent_data
    })
