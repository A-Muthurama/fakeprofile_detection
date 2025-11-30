from flask import Blueprint, request, jsonify
from functools import wraps
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

# Create blueprint
analysis_bp = Blueprint('analysis', __name__)

# In-memory storage (temporary - will be lost when app restarts)
reports_storage = {}
report_counter = 0


# ============================================
# Input Validation
# ============================================

def validate_url(url):
    """Validate profile URL format"""
    if not url:
        return False, "URL is required"
    
    valid_domains = ['instagram.com', 'facebook.com', 'twitter.com', 'x.com']
    if not any(domain in url for domain in valid_domains):
        return False, "URL must be from Instagram, Facebook, or Twitter"
    
    return True, None


def validate_platform(platform):
    """Validate platform selection"""
    valid_platforms = ['instagram', 'facebook', 'twitter']
    if platform not in valid_platforms:
        return False, f"Invalid platform. Must be one of: {', '.join(valid_platforms)}"
    return True, None


# ============================================
# API Routes
# ============================================

@analysis_bp.route('/analyze', methods=['POST'])
def analyze_profile():
    """
    Main profile analysis endpoint
    
    Request body:
    {
        "profile_url": "https://instagram.com/username",
        "platform": "instagram"
    }
    
    Returns:
    {
        "success": true,
        "score": {...},
        "analysis": {...},
        "timestamp": "..."
    }
    """
    global report_counter, reports_storage
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body must be JSON'
            }), 400
        
        # Validate input
        profile_url = data.get('profile_url', '').strip()
        platform = data.get('platform', 'instagram').lower()
        
        # Validate URL
        is_valid, error = validate_url(profile_url)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        # Validate platform
        is_valid, error = validate_platform(platform)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': error
            }), 400
        
        logger.info(f'Analyzing profile: {profile_url} (platform: {platform})')
        
        # Import analyzer service
        try:
            from services.analyzer_service import AnalyzerService
        except ImportError as e:
            logger.error(f'Failed to import AnalyzerService: {str(e)}')
            return jsonify({
                'success': False,
                'error': 'Analysis service unavailable'
            }), 503
        
        # Create analyzer instance
        analyzer = AnalyzerService()
        
        # Run analysis
        try:
            result = analyzer.analyze(profile_url, platform)
            
            # Save to in-memory storage (temporary)
            report_counter += 1
            report_id = f"report_{report_counter}"
            reports_storage[report_id] = {
                'profile_url': profile_url,
                'platform': platform,
                'result': result,
                'timestamp': datetime.now()
            }
            
            result['report_id'] = report_id
            
            return jsonify({
                'success': True,
                'score': result.get('score', {}),
                'analysis': result.get('analysis', {}),
                'report_id': report_id,
                'timestamp': datetime.now().isoformat()
            }), 200
        
        except Exception as e:
            logger.error(f'Analysis failed: {str(e)}')
            return jsonify({
                'success': False,
                'error': f'Analysis failed: {str(e)}'
            }), 500
    
    except Exception as e:
        logger.error(f'Endpoint error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500


@analysis_bp.route('/analyze/batch', methods=['POST'])
def analyze_batch():
    """
    Batch analysis endpoint (multiple profiles)
    
    Request body:
    {
        "profiles": [
            {"url": "...", "platform": "instagram"},
            {"url": "...", "platform": "facebook"}
        ]
    }
    """
    try:
        data = request.get_json()
        profiles = data.get('profiles', [])
        
        if not profiles or not isinstance(profiles, list):
            return jsonify({
                'success': False,
                'error': 'profiles must be a non-empty array'
            }), 400
        
        if len(profiles) > 10:
            return jsonify({
                'success': False,
                'error': 'Maximum 10 profiles per batch'
            }), 400
        
        from services.analyzer_service import AnalyzerService
        analyzer = AnalyzerService()
        
        results = []
        for profile in profiles:
            url = profile.get('url', '').strip()
            platform = profile.get('platform', 'instagram').lower()
            
            try:
                result = analyzer.analyze(url, platform)
                results.append({
                    'url': url,
                    'platform': platform,
                    'success': True,
                    'score': result.get('score', {})
                })
            except Exception as e:
                results.append({
                    'url': url,
                    'platform': platform,
                    'success': False,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f'Batch analysis error: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Batch analysis failed'
        }), 500


@analysis_bp.route('/report/<report_id>', methods=['GET'])
def get_report(report_id):
    """
    Retrieve analysis report
    
    Returns:
    {
        "success": true,
        "report": {...}
    }
    """
    try:
        report = reports_storage.get(report_id)
        
        if not report:
            return jsonify({
                'success': False,
                'error': 'Report not found'
            }), 404
        
        # Convert datetime to string
        report_copy = report.copy()
        report_copy['timestamp'] = report['timestamp'].isoformat()
        
        return jsonify({
            'success': True,
            'report': report_copy
        }), 200
    
    except Exception as e:
        logger.error(f'Failed to retrieve report: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve report'
        }), 500


@analysis_bp.route('/history', methods=['GET'])
def get_analysis_history():
    """
    Get user's analysis history
    
    Query params:
    - limit: number of results (default: 20)
    - offset: pagination offset (default: 0)
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Validate parameters
        if limit > 100:
            limit = 100
        if limit < 1:
            limit = 1
        if offset < 0:
            offset = 0
        
        # Get all reports and convert to list
        all_reports = []
        for report_id, report in reports_storage.items():
            report_copy = report.copy()
            report_copy['id'] = report_id
            report_copy['timestamp'] = report['timestamp'].isoformat()
            all_reports.append(report_copy)
        
        # Sort by timestamp (newest first)
        all_reports.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Paginate
        paginated_reports = all_reports[offset:offset + limit]
        
        return jsonify({
            'success': True,
            'reports': paginated_reports,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': len(all_reports)
            }
        }), 200
    
    except Exception as e:
        logger.error(f'Failed to retrieve history: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve history'
        }), 500


@analysis_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """
    Get analysis statistics
    """
    try:
        total = len(reports_storage)
        
        # Calculate stats
        high_risk = 0
        medium_risk = 0
        low_risk = 0
        total_score = 0
        
        for report in reports_storage.values():
            score = report['result']['score']['final_score']
            total_score += score
            
            if score >= 80:
                low_risk += 1
            elif score >= 50:
                medium_risk += 1
            else:
                high_risk += 1
        
        avg_score = total_score / total if total > 0 else 0
        
        stats = {
            'total_analyses': total,
            'fake_detected': high_risk,
            'suspicious': medium_risk,
            'authentic': low_risk,
            'average_score': round(avg_score, 2)
        }
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
    
    except Exception as e:
        logger.error(f'Failed to get statistics: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Failed to get statistics'
        }), 500