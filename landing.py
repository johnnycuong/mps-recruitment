from flask import Blueprint, render_template, send_from_directory, request, jsonify
import os

landing_bp = Blueprint('landing', __name__)

@landing_bp.route('/', methods=['GET'])
def index():
    """Render the landing page"""
    return render_template('index.html')

@landing_bp.route('/admin', methods=['GET'])
def admin():
    """Render the admin dashboard"""
    return render_template('admin.html')

@landing_bp.route('/assets/<path:filename>')
def serve_assets(filename):
    """Serve static assets"""
    return send_from_directory(os.path.join('static', 'assets'), filename)

@landing_bp.route('/candidate-form', methods=['GET'])
def candidate_form():
    """Render the candidate application form"""
    job_id = request.args.get('job_id')
    return render_template('candidate_form.html', job_id=job_id)

@landing_bp.route('/jobs', methods=['GET'])
def jobs_listing():
    """Render the public jobs listing page"""
    return render_template('jobs.html')

@landing_bp.route('/job/<int:job_id>', methods=['GET'])
def job_details(job_id):
    """Render the public job details page"""
    return render_template('job_details.html', job_id=job_id)

@landing_bp.route('/application-success', methods=['GET'])
def application_success():
    """Render the application success page"""
    return render_template('application_success.html')

@landing_bp.route('/contact', methods=['GET'])
def contact():
    """Render the contact page"""
    return render_template('contact.html')

@landing_bp.route('/about', methods=['GET'])
def about():
    """Render the about page"""
    return render_template('about.html')

@landing_bp.route('/services', methods=['GET'])
def services():
    """Render the services page"""
    return render_template('services.html')

@landing_bp.route('/contact-submit', methods=['POST'])
def contact_submit():
    """Handle contact form submission"""
    data = request.get_json()
    
    # In a real implementation, this would send an email or save to database
    # For now, just return success
    return jsonify({
        'success': True,
        'message': 'Thank you for your message. We will get back to you soon.'
    })
