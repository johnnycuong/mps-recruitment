from flask import Blueprint, request, jsonify
from src.models.user import db, User, UserRole
from src.models.client import Client, ClientType, ClientStatus
from src.models.activity import Activity, ActivityType
from src.routes.auth import token_required, role_required

clients_bp = Blueprint('clients', __name__)

@clients_bp.route('/', methods=['GET'])
@token_required
def get_clients(current_user):
    # Get query parameters for filtering
    status = request.args.get('status')
    search = request.args.get('search')
    client_type = request.args.get('client_type')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Base query
    query = Client.query
    
    # Apply filters
    if status:
        try:
            status_enum = ClientStatus(status)
            query = query.filter_by(status=status_enum)
        except ValueError:
            return jsonify({'message': 'Invalid status value'}), 400
    
    if client_type:
        try:
            client_type_enum = ClientType(client_type)
            query = query.filter_by(client_type=client_type_enum)
        except ValueError:
            return jsonify({'message': 'Invalid client type value'}), 400
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Client.company_name.ilike(search_term)) | 
            (Client.primary_contact_name.ilike(search_term)) |
            (Client.primary_contact_email.ilike(search_term))
        )
    
    # Pagination
    clients_pagination = query.order_by(Client.created_at.desc()).paginate(page=page, per_page=per_page)
    
    # Format response
    clients_list = []
    for client in clients_pagination.items:
        clients_list.append({
            'id': client.id,
            'company_name': client.company_name,
            'industry': client.industry,
            'client_type': client.client_type.value,
            'status': client.status.value,
            'primary_contact_name': client.primary_contact_name,
            'primary_contact_email': client.primary_contact_email,
            'primary_contact_phone': client.primary_contact_phone,
            'quality_rating': client.quality_rating,
            'created_at': client.created_at.isoformat()
        })
    
    return jsonify({
        'clients': clients_list,
        'total': clients_pagination.total,
        'pages': clients_pagination.pages,
        'current_page': clients_pagination.page
    })

@clients_bp.route('/<int:client_id>', methods=['GET'])
@token_required
def get_client(current_user, client_id):
    client = Client.query.get_or_404(client_id)
    
    # Format response with all details
    client_data = {
        'id': client.id,
        'company_name': client.company_name,
        'industry': client.industry,
        'client_type': client.client_type.value,
        'status': client.status.value,
        'address': client.address,
        'city': client.city,
        'country': client.country,
        'website': client.website,
        'description': client.description,
        'employee_count': client.employee_count,
        'primary_contact_name': client.primary_contact_name,
        'primary_contact_email': client.primary_contact_email,
        'primary_contact_phone': client.primary_contact_phone,
        'quality_rating': client.quality_rating,
        'response_time_avg': client.response_time_avg,
        'hire_success_rate': client.hire_success_rate,
        'created_at': client.created_at.isoformat(),
        'updated_at': client.updated_at.isoformat()
    }
    
    return jsonify({'client': client_data})

@clients_bp.route('/', methods=['POST'])
@token_required
@role_required([UserRole.ADMIN, UserRole.MANAGER])
def create_client(current_user):
    data = request.get_json()
    
    # Validate required fields
    if not data.get('company_name'):
        return jsonify({'message': 'Company name is required!'}), 400
    
    # Process enums
    client_type = ClientType.FDI
    if data.get('client_type'):
        try:
            client_type = ClientType(data['client_type'])
        except ValueError:
            return jsonify({'message': 'Invalid client type value!'}), 400
    
    status = ClientStatus.ACTIVE
    if data.get('status'):
        try:
            status = ClientStatus(data['status'])
        except ValueError:
            return jsonify({'message': 'Invalid status value!'}), 400
    
    # Create new client
    new_client = Client(
        company_name=data['company_name'],
        industry=data.get('industry'),
        client_type=client_type,
        status=status,
        address=data.get('address'),
        city=data.get('city'),
        country=data.get('country'),
        website=data.get('website'),
        description=data.get('description'),
        employee_count=data.get('employee_count'),
        primary_contact_name=data.get('primary_contact_name'),
        primary_contact_email=data.get('primary_contact_email'),
        primary_contact_phone=data.get('primary_contact_phone'),
        quality_rating=data.get('quality_rating', 0.0),
        response_time_avg=data.get('response_time_avg'),
        hire_success_rate=data.get('hire_success_rate')
    )
    
    # Associate with user if provided
    if data.get('user_id'):
        user = User.query.get(data['user_id'])
        if user and user.role == UserRole.CLIENT:
            new_client.user_id = user.id
    
    db.session.add(new_client)
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        activity_type=ActivityType.SYSTEM_ACTION,
        description=f"Client {data['company_name']} created"
    )
    db.session.add(activity)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Client created successfully!',
        'client_id': new_client.id
    }), 201

@clients_bp.route('/<int:client_id>', methods=['PUT'])
@token_required
@role_required([UserRole.ADMIN, UserRole.MANAGER])
def update_client(current_user, client_id):
    client = Client.query.get_or_404(client_id)
    data = request.get_json()
    
    # Update basic fields
    if 'company_name' in data:
        client.company_name = data['company_name']
    
    if 'industry' in data:
        client.industry = data['industry']
    
    # Process enums
    if 'client_type' in data:
        try:
            client.client_type = ClientType(data['client_type'])
        except ValueError:
            return jsonify({'message': 'Invalid client type value!'}), 400
    
    if 'status' in data:
        try:
            client.status = ClientStatus(data['status'])
        except ValueError:
            return jsonify({'message': 'Invalid status value!'}), 400
    
    # Update other fields
    for field in [
        'address', 'city', 'country', 'website', 'description', 
        'employee_count', 'primary_contact_name', 'primary_contact_email', 
        'primary_contact_phone', 'quality_rating', 'response_time_avg', 
        'hire_success_rate'
    ]:
        if field in data:
            setattr(client, field, data[field])
    
    # Update user association if provided
    if 'user_id' in data:
        if data['user_id']:
            user = User.query.get(data['user_id'])
            if user and user.role == UserRole.CLIENT:
                client.user_id = user.id
        else:
            client.user_id = None
    
    # Log activity
    activity = Activity(
        user_id=current_user.id,
        activity_type=ActivityType.SYSTEM_ACTION,
        description=f"Client {client.company_name} updated"
    )
    db.session.add(activity)
    
    db.session.commit()
    
    return jsonify({'message': 'Client updated successfully!'})

@clients_bp.route('/<int:client_id>', methods=['DELETE'])
@token_required
@role_required([UserRole.ADMIN])
def delete_client(current_user, client_id):
    client = Client.query.get_or_404(client_id)
    
    # Log activity before deletion
    activity = Activity(
        user_id=current_user.id,
        activity_type=ActivityType.SYSTEM_ACTION,
        description=f"Client {client.company_name} deleted"
    )
    db.session.add(activity)
    
    db.session.delete(client)
    db.session.commit()
    
    return jsonify({'message': 'Client deleted successfully!'})

@clients_bp.route('/statistics', methods=['GET'])
@token_required
def get_client_statistics(current_user):
    # Count clients by type
    type_counts = {}
    for client_type in ClientType:
        count = Client.query.filter_by(client_type=client_type).count()
        type_counts[client_type.value] = count
    
    # Count clients by status
    status_counts = {}
    for status in ClientStatus:
        count = Client.query.filter_by(status=status).count()
        status_counts[status.value] = count
    
    # Count clients by industry
    industry_counts = db.session.query(
        Client.industry, db.func.count(Client.id)
    ).group_by(Client.industry).all()
    
    industry_data = {industry: count for industry, count in industry_counts if industry}
    
    # Recent clients
    recent_clients = Client.query.order_by(Client.created_at.desc()).limit(5).all()
    recent_data = [{
        'id': c.id,
        'company_name': c.company_name,
        'client_type': c.client_type.value,
        'status': c.status.value,
        'created_at': c.created_at.isoformat()
    } for c in recent_clients]
    
    return jsonify({
        'total_clients': Client.query.count(),
        'type_distribution': type_counts,
        'status_distribution': status_counts,
        'industry_distribution': industry_data,
        'recent_clients': recent_data
    })
