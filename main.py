from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

from flask import Flask, jsonify
from flask_cors import CORS

# Import models
from src.models.user import db, User
from src.models.client import Client
from src.models.candidate import Candidate
from src.models.job_position import JobPosition
from src.models.application import Application
from src.models.interview import Interview
from src.models.partner import Partner
from src.models.activity import Activity

# Import routes
from src.routes.auth import auth_bp
from src.routes.candidates import candidates_bp
from src.routes.clients import clients_bp
from src.routes.jobs import jobs_bp
from src.routes.applications import applications_bp
from src.routes.interviews import interviews_bp
from src.routes.partners import partners_bp
from src.routes.analytics import analytics_bp
from src.routes.landing import landing_bp

def create_app(test_config=None):
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Configure database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_development')
    
    # Enable CORS
    CORS(app)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(candidates_bp, url_prefix='/api/candidates')
    app.register_blueprint(clients_bp, url_prefix='/api/clients')
    app.register_blueprint(jobs_bp, url_prefix='/api/jobs')
    app.register_blueprint(applications_bp, url_prefix='/api/applications')
    app.register_blueprint(interviews_bp, url_prefix='/api/interviews')
    app.register_blueprint(partners_bp, url_prefix='/api/partners')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(landing_bp, url_prefix='/')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'Bad request'
        }), 400
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'Internal server error'
        }), 500
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
