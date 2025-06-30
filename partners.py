from flask import Blueprint, request, jsonify
from src.models.user import db, User, UserRole
from src.models.partner import Partner, PartnerType, PartnerStatus
from src.models.activity import Activity, ActivityType
from src.routes.auth import token_required, role_required

partners_bp = Blueprint('partners', __name__)

@partners_bp.route('/', methods=['GET'])
@token_required
def get_partners(current_user):
    # Get query parameters for filtering
    status = request.args.get('status')
    partner_type = request.args.get('partner_type')
    search = request.args.get('search')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Base query
    query = Partner.query
    
    # Apply filters
    if status:
        try:
            status_enum = PartnerStatus(status)
            query = query.filter_by(status=status_enum)
        except ValueError:
            return jsonify({'message': 'Invalid status value'}), 400
    
    if partner_type:
        try:
            partner_type_enum = PartnerType(partner_type)
            query = query.filter_by(partner_type=partner_type_enum)
        except ValueError:
            return jsonify({'message': 'Invalid partner type value'}), 400
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Partner.name.ilike(search_term)) | 
            (Partner.primary_contact_name.ilike(search_term)) |
            (Partner.primary_contact_email.ilike(search_term))
        )
    
    # Pagination
    partners_pagination = query.order_by(Partner.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # Format response
    partners_list = []
    for partner in partners_pagination.items:
        partners_list.append({
            'id': partner.id,
            'name': partner.name,
            'partner_type': partner.partner_type.value,
            'status': partner.status.value,
            'primary_contact_name': partner.primary_contact_name,
            'primary_contact_email': partner.primary_contact_email,
            'primary_contact_phone': partner.primary_contact_phone,
            'quality_rating': partner.quality_rating,
            'success_rate': partner.success_rate,
            'created_at': partner.created_at.isoformat()
        })
    
    return jsonify({
        'partners': partners_list,
        'total': partners_pagination.total,
        'pages': partners_pagination.pages,
        'current_page': partners_pagination.page
    })

@partners_bp.route('/<int:partner_id>', methods=['GET'])
@token_required
def get_partner(current_user, partner_id):
    partner = Partner.query.get_or_404(partner_id)
    
    # Format response with all details
    partner_data = {
        'id': partner.id,
        'name': partner.name,
        'partner_type': partner.partner_type.value,
        'status': partner.status.value,
        'address': partner.address,
        'city': partner.city,
        'province': partner.province,
        'country': partner.country,
        'website': partner.website,
        'primary_contact_name': partner.primary_contact_name,
        'primary_contact_email': partner.primary_contact_email,
        'primary_contact_phone': partner.primary_contact_phone,
        'description': partner.description,
        'specialization': partner.specialization,
        'agreement_details': partner.agreement_details,
        'commission_rate': partner.commission_rate,
        'quality_rating': partner.quality_rating,
        'candidates_provided_count': partner.candidates_provided_count,
        'successful_placements_count': partner.successful_placements_count,
        'success_rate': partner.success_rate,
        'created_at': partner.created_at.isoformat(),
        'updated_at': partner.updated_at.isoformat()
    }
    
    return jsonify({'partner': partner_data})

@partners_bp.route('/', methods=['POST'])
@token_required
@role_required([UserRole.ADMIN, UserRole.MANAGER])
def create_partner(current_user):
    data = request.get_json()
    
    # Validate required fields
    if not data.get('name') or not data.get('partner_type'):
        return jsonify({'message': 'Partner name and type are required!'}), 400
    
    # Process enums
    try:
        partner_type = PartnerType(data['partner_type'])
    except ValueError:
        return jsonify({'message': 'Invalid partner type value!'}), 400
    
    status = PartnerStatus.ACTIVE
    if data.get('status'):
        try:
            status = PartnerStatus(data['status'])
        except ValueError:
            return jsonify({'message': 'Invalid status value!'}), 400
    
    # Create new partner
    new_partner = Partner(
        name=data['name'],
        partner_type=partner_type,
        status=status,
        address=data.get('address'),
        city=data.get('city'),
        province=data.get('province'),
        country=data.get('country', 'Vietnam'),
        website=data.get('website'),
        primary_contact_name=data.get('primary_contact_name'),
        primary_contact_email=data.get('primary_contact_email'),
        primary_contact_phone=data.get('primary_contact_phone'),
        description=data.get('description'),
        specialization=data.get('specialization'),
        agreement_details=data.get('agreement_details'),
        commission_rate=data.get('commission_rate'),
        quality_rating=data.get('quality_rating', 0.0),
        candidates_provided_count=data.get('candidates_provided_count', 0),
        successful_placements_count=data.get('successful_placements_count', 0),
        success_rate=data.get('success_rate', 0.0)
    )
    
    # Associate with user if provided
    if data.get('user_id'):
        user = User.query.get(data['user_id'])
        if user and user.role == UserRole.PARTNER:
            new_partner.user_id = user.id
    
    db.session.add(new_partner)
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        activity_type=ActivityType.SYSTEM_ACTION,
        description=f"Partner {data['name']} created"
    )
    db.session.add(activity)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Partner created successfully!',
        'partner_id': new_partner.id
    }), 201

@partners_bp.route('/<int:partner_id>', methods=['PUT'])
@token_required
@role_required([UserRole.ADMIN, UserRole.MANAGER])
def update_partner(current_user, partner_id):
    partner = Partner.query.get_or_404(partner_id)
    data = request.get_json()
    
    # Update basic fields
    if 'name' in data:
        partner.name = data['name']
    
    # Process enums
    if 'partner_type' in data:
        try:
            partner.partner_type = PartnerType(data['partner_type'])
        except ValueError:
            return jsonify({'message': 'Invalid partner type value!'}), 400
    
    if 'status' in data:
        try:
            partner.status = PartnerStatus(data['status'])
        except ValueError:
            return jsonify({'message': 'Invalid status value!'}), 400
    
    # Update other fields
    for field in [
        'address', 'city', 'province', 'country', 'website', 
        'primary_contact_name', 'primary_contact_email', 'primary_contact_phone',
        'description', 'specialization', 'agreement_details', 'commission_rate',
        'quality_rating', 'candidates_provided_count', 'successful_placements_count',
        'success_rate'
    ]:
        if field in data:
            setattr(partner, field, data[field])
    
    # Update user association if provided
    if 'user_id' in data:
        if data['user_id']:
            user = User.query.get(data['user_id'])
            if user and user.role == UserRole.PARTNER:
                partner.user_id = user.id
        else:
            partner.user_id = None
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        activity_type=ActivityType.SYSTEM_ACTION,
        description=f"Partner {partner.name} updated"
    )
    db.session.add(activity)
    
    db.session.commit()
    
    return jsonify({'message': 'Partner updated successfully!'})

@partners_bp.route('/<int:partner_id>', methods=['DELETE'])
@token_required
@role_required([UserRole.ADMIN])
def delete_partner(current_user, partner_id):
    partner = Partner.query.get_or_404(partner_id)
    
    # Log activity before deletion
    activity = Activity(
        user_id=current_user.id,
        activity_type=ActivityType.SYSTEM_ACTION,
        description=f"Partner {partner.name} deleted"
    )
    db.session.add(activity)
    
    db.session.delete(partner)
    db.session.commit()
    
    return jsonify({'message': 'Partner deleted successfully!'})

@partners_bp.route('/statistics', methods=['GET'])
@token_required
def get_partner_statistics(current_user):
    # Count partners by type
    type_counts = {}
    for partner_type in PartnerType:
        count = Partner.query.filter_by(partner_type=partner_type).count()
        type_counts[partner_type.value] = count
    
    # Count partners by status
    status_counts = {}
    for status in PartnerStatus:
        count = Partner.query.filter_by(status=status).count()
        status_counts[status.value] = count
    
    # Calculate average metrics
    avg_quality_rating = db.session.query(db.func.avg(Partner.quality_rating)).scalar() or 0
    avg_success_rate = db.session.query(db.func.avg(Partner.success_rate)).scalar() or 0
    
    # Top performing partners
    top_partners = Partner.query.order_by(Partner.success_rate.desc()).limit(5).all()
    top_data = [{
        'id': p.id,
        'name': p.name,
        'partner_type': p.partner_type.value,
        'quality_rating': p.quality_rating,
        'success_rate': p.success_rate,
        'successful_placements_count': p.successful_placements_count
    } for p in top_partners]
    
    return jsonify({
        'total_partners': Partner.query.count(),
        'active_partners': Partner.query.filter_by(status=PartnerStatus.ACTIVE).count(),
        'type_distribution': type_counts,
        'status_distribution': status_counts,
        'average_metrics': {
            'quality_rating': round(avg_quality_rating, 1),
            'success_rate': round(avg_success_rate, 1)
        },
        'top_performing_partners': top_data
    })
