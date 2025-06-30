from flask import Blueprint, request, jsonify
from src.models.user import db, User, UserRole
from src.models.candidate import Candidate, CandidateStatus
from src.models.client import Client
from src.models.job_position import JobPosition, JobStatus
from src.models.application import Application, ApplicationStatus
from src.models.interview import Interview, InterviewStatus
from src.models.partner import Partner
from src.routes.auth import token_required, role_required
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard_analytics(current_user):
    """Get summary analytics for dashboard"""
    
    # Get counts for main entities
    active_candidates = Candidate.query.filter(Candidate.status != CandidateStatus.REJECTED, 
                                              Candidate.status != CandidateStatus.BLACKLISTED).count()
    active_jobs = JobPosition.query.filter_by(status=JobStatus.OPEN).count()
    active_clients = Client.query.count()
    pending_applications = Application.query.filter(
        Application.status != ApplicationStatus.HIRED,
        Application.status != ApplicationStatus.REJECTED,
        Application.status != ApplicationStatus.WITHDRAWN
    ).count()
    upcoming_interviews = Interview.query.filter(
        Interview.scheduled_at > datetime.utcnow(),
        Interview.status == InterviewStatus.SCHEDULED
    ).count()
    
    # Calculate hiring metrics
    total_applications = Application.query.count()
    hired_applications = Application.query.filter_by(status=ApplicationStatus.HIRED).count()
    
    hire_rate = (hired_applications / total_applications * 100) if total_applications > 0 else 0
    
    # Calculate average time metrics (in days)
    avg_time_to_hire = db.session.query(
        db.func.avg(
            db.func.julianday(Application.hired_at) - 
            db.func.julianday(Application.applied_at)
        )
    ).filter(
        Application.hired_at.isnot(None),
        Application.applied_at.isnot(None)
    ).scalar() or 0
    
    # Get recent activity counts
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    new_candidates_today = Candidate.query.filter(
        db.func.date(Candidate.created_at) == today
    ).count()
    
    new_candidates_week = Candidate.query.filter(
        Candidate.created_at >= week_ago
    ).count()
    
    new_applications_week = Application.query.filter(
        Application.created_at >= week_ago
    ).count()
    
    # Return dashboard data
    return jsonify({
        'summary': {
            'active_candidates': active_candidates,
            'active_jobs': active_jobs,
            'active_clients': active_clients,
            'pending_applications': pending_applications,
            'upcoming_interviews': upcoming_interviews
        },
        'hiring_metrics': {
            'hire_rate': round(hire_rate, 1),
            'avg_time_to_hire': round(avg_time_to_hire, 1)
        },
        'recent_activity': {
            'new_candidates_today': new_candidates_today,
            'new_candidates_week': new_candidates_week,
            'new_applications_week': new_applications_week
        }
    })

@analytics_bp.route('/recruitment-funnel', methods=['GET'])
@token_required
def get_recruitment_funnel(current_user):
    """Get recruitment funnel analytics"""
    
    # Get date range parameters
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Default to last 90 days if not specified
    if not date_from:
        date_from = (datetime.utcnow() - timedelta(days=90)).isoformat()
    
    if not date_to:
        date_to = datetime.utcnow().isoformat()
    
    # Parse dates
    try:
        from_date = datetime.fromisoformat(date_from)
        to_date = datetime.fromisoformat(date_to)
    except ValueError:
        return jsonify({'message': 'Invalid date format!'}), 400
    
    # Count applications at each stage
    applied_count = Application.query.filter(
        Application.applied_at >= from_date,
        Application.applied_at <= to_date
    ).count()
    
    screened_count = Application.query.filter(
        Application.screened_at >= from_date,
        Application.screened_at <= to_date
    ).count()
    
    interviewed_count = Application.query.filter(
        Application.interviewed_at >= from_date,
        Application.interviewed_at <= to_date
    ).count()
    
    shortlisted_count = Application.query.filter(
        Application.shortlisted_at >= from_date,
        Application.shortlisted_at <= to_date
    ).count()
    
    client_reviewed_count = Application.query.filter(
        Application.client_reviewed_at >= from_date,
        Application.client_reviewed_at <= to_date
    ).count()
    
    hired_count = Application.query.filter(
        Application.hired_at >= from_date,
        Application.hired_at <= to_date
    ).count()
    
    # Calculate conversion rates
    screen_rate = (screened_count / applied_count * 100) if applied_count > 0 else 0
    interview_rate = (interviewed_count / screened_count * 100) if screened_count > 0 else 0
    shortlist_rate = (shortlisted_count / interviewed_count * 100) if interviewed_count > 0 else 0
    client_review_rate = (client_reviewed_count / shortlisted_count * 100) if shortlisted_count > 0 else 0
    hire_rate = (hired_count / client_reviewed_count * 100) if client_reviewed_count > 0 else 0
    overall_rate = (hired_count / applied_count * 100) if applied_count > 0 else 0
    
    # Return funnel data
    return jsonify({
        'funnel_stages': {
            'applied': applied_count,
            'screened': screened_count,
            'interviewed': interviewed_count,
            'shortlisted': shortlisted_count,
            'client_reviewed': client_reviewed_count,
            'hired': hired_count
        },
        'conversion_rates': {
            'screen_rate': round(screen_rate, 1),
            'interview_rate': round(interview_rate, 1),
            'shortlist_rate': round(shortlist_rate, 1),
            'client_review_rate': round(client_review_rate, 1),
            'hire_rate': round(hire_rate, 1),
            'overall_rate': round(overall_rate, 1)
        },
        'date_range': {
            'from': from_date.isoformat(),
            'to': to_date.isoformat()
        }
    })

@analytics_bp.route('/time-to-hire', methods=['GET'])
@token_required
def get_time_to_hire_analytics(current_user):
    """Get time-to-hire analytics by job type, level, and client"""
    
    # Get date range parameters
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Default to last 180 days if not specified
    if not date_from:
        date_from = (datetime.utcnow() - timedelta(days=180)).isoformat()
    
    if not date_to:
        date_to = datetime.utcnow().isoformat()
    
    # Parse dates
    try:
        from_date = datetime.fromisoformat(date_from)
        to_date = datetime.fromisoformat(date_to)
    except ValueError:
        return jsonify({'message': 'Invalid date format!'}), 400
    
    # Get hired applications in date range
    hired_applications = db.session.query(
        Application, JobPosition
    ).join(
        JobPosition, Application.job_position_id == JobPosition.id
    ).filter(
        Application.hired_at >= from_date,
        Application.hired_at <= to_date,
        Application.applied_at.isnot(None)
    ).all()
    
    # Calculate time to hire for each application
    time_to_hire_data = []
    for app, job in hired_applications:
        if app.hired_at and app.applied_at:
            days_to_hire = (app.hired_at - app.applied_at).days
            
            time_to_hire_data.append({
                'application_id': app.id,
                'job_id': job.id,
                'job_title': job.title,
                'job_type': job.job_type.value,
                'job_level': job.job_level.value if job.job_level else 'Not specified',
                'client_id': job.client_id,
                'client_name': job.client.company_name,
                'days_to_hire': days_to_hire
            })
    
    # Convert to pandas DataFrame for analysis
    if time_to_hire_data:
        df = pd.DataFrame(time_to_hire_data)
        
        # Calculate average time to hire by job type
        job_type_avg = df.groupby('job_type')['days_to_hire'].mean().to_dict()
        
        # Calculate average time to hire by job level
        job_level_avg = df.groupby('job_level')['days_to_hire'].mean().to_dict()
        
        # Calculate average time to hire by client (top 5)
        client_avg = df.groupby(['client_id', 'client_name'])['days_to_hire'].mean().reset_index()
        client_avg = client_avg.sort_values('days_to_hire').head(5)
        client_data = client_avg.to_dict('records')
        
        # Overall average
        overall_avg = df['days_to_hire'].mean()
        
        # Time to hire trend (monthly)
        monthly_trend = []
    else:
        job_type_avg = {}
        job_level_avg = {}
        client_data = []
        overall_avg = 0
        monthly_trend = []
    
    # Return time to hire analytics
    return jsonify({
        'overall_avg_days': round(overall_avg, 1),
        'by_job_type': {k: round(v, 1) for k, v in job_type_avg.items()},
        'by_job_level': {k: round(v, 1) for k, v in job_level_avg.items()},
        'by_client': client_data,
        'monthly_trend': monthly_trend,
        'date_range': {
            'from': from_date.isoformat(),
            'to': to_date.isoformat()
        }
    })

@analytics_bp.route('/source-effectiveness', methods=['GET'])
@token_required
def get_source_effectiveness(current_user):
    """Get candidate source effectiveness analytics"""
    
    # Get date range parameters
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Default to last 180 days if not specified
    if not date_from:
        date_from = (datetime.utcnow() - timedelta(days=180)).isoformat()
    
    if not date_to:
        date_to = datetime.utcnow().isoformat()
    
    # Parse dates
    try:
        from_date = datetime.fromisoformat(date_from)
        to_date = datetime.fromisoformat(date_to)
    except ValueError:
        return jsonify({'message': 'Invalid date format!'}), 400
    
    # Get candidates by source
    candidates = Candidate.query.filter(
        Candidate.created_at >= from_date,
        Candidate.created_at <= to_date
    ).all()
    
    # Group by source
    source_data = {}
    for candidate in candidates:
        source = candidate.source or 'Unknown'
        
        if source not in source_data:
            source_data[source] = {
                'total': 0,
                'hired': 0,
                'rejected': 0,
                'in_process': 0
            }
        
        source_data[source]['total'] += 1
        
        if candidate.status == CandidateStatus.HIRED:
            source_data[source]['hired'] += 1
        elif candidate.status == CandidateStatus.REJECTED:
            source_data[source]['rejected'] += 1
        else:
            source_data[source]['in_process'] += 1
    
    # Calculate effectiveness metrics
    source_effectiveness = []
    for source, counts in source_data.items():
        hire_rate = (counts['hired'] / counts['total'] * 100) if counts['total'] > 0 else 0
        
        source_effectiveness.append({
            'source': source,
            'total_candidates': counts['total'],
            'hired': counts['hired'],
            'rejected': counts['rejected'],
            'in_process': counts['in_process'],
            'hire_rate': round(hire_rate, 1)
        })
    
    # Sort by total candidates (descending)
    source_effectiveness.sort(key=lambda x: x['total_candidates'], reverse=True)
    
    # Return source effectiveness data
    return jsonify({
        'source_effectiveness': source_effectiveness,
        'date_range': {
            'from': from_date.isoformat(),
            'to': to_date.isoformat()
        }
    })

@analytics_bp.route('/export-report', methods=['GET'])
@token_required
@role_required([UserRole.ADMIN, UserRole.MANAGER])
def export_analytics_report(current_user):
    """Generate and export analytics report in JSON format"""
    
    # Get date range parameters
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Default to last 30 days if not specified
    if not date_from:
        date_from = (datetime.utcnow() - timedelta(days=30)).isoformat()
    
    if not date_to:
        date_to = datetime.utcnow().isoformat()
    
    # Parse dates
    try:
        from_date = datetime.fromisoformat(date_from)
        to_date = datetime.fromisoformat(date_to)
    except ValueError:
        return jsonify({'message': 'Invalid date format!'}), 400
    
    # Compile comprehensive report
    report = {
        'report_date': datetime.utcnow().isoformat(),
        'date_range': {
            'from': from_date.isoformat(),
            'to': to_date.isoformat()
        },
        'summary': {
            'total_candidates': Candidate.query.filter(
                Candidate.created_at >= from_date,
                Candidate.created_at <= to_date
            ).count(),
            'total_applications': Application.query.filter(
                Application.created_at >= from_date,
                Application.created_at <= to_date
            ).count(),
            'total_interviews': Interview.query.filter(
                Interview.created_at >= from_date,
                Interview.created_at <= to_date
            ).count(),
            'total_hires': Application.query.filter(
                Application.hired_at >= from_date,
                Application.hired_at <= to_date
            ).count()
        }
    }
    
    # Add recruitment funnel data
    funnel_response = get_recruitment_funnel(current_user)
    funnel_data = json.loads(funnel_response.get_data(as_text=True))
    report['recruitment_funnel'] = funnel_data
    
    # Add time to hire data
    time_to_hire_response = get_time_to_hire_analytics(current_user)
    time_to_hire_data = json.loads(time_to_hire_response.get_data(as_text=True))
    report['time_to_hire'] = time_to_hire_data
    
    # Add source effectiveness data
    source_response = get_source_effectiveness(current_user)
    source_data = json.loads(source_response.get_data(as_text=True))
    report['source_effectiveness'] = source_data
    
    # Return full report
    return jsonify(report)
