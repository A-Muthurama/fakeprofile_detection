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
    
    valid_domains = ['instagram.com', 'facebook.com', 'twitter.com', 'x.com', 'linkedin.com']
    if not any(domain in url for domain in valid_domains):
        return False, "URL must be from Instagram, Facebook, or Twitter"
    
    return True, None


def validate_platform(platform):
    """Validate platform selection"""
    valid_platforms = ['instagram', 'facebook', 'twitter', 'linkedin']
    if platform not in valid_platforms:
        return False, f"Invalid platform. Must be one of: {', '.join(valid_platforms)}"
    return True, None


# ============================================
# API Routes
# ============================================

@analysis_bp.route('/analyze', methods=['POST'])
def analyze_profile():
    """
    Main analysis endpoint
    - Checks Local DB for community reports FIRST (Real-Time)
    - Falls back to AnalyzerService (Scraping/Simulation)
    """
    logger.info("TEST LOG - ANALYZE REQUEST RECEIVED")
    global report_counter, reports_storage
    
    try:
        data = request.json
        url = data.get('url', '') or data.get('profile_url', '') # Handle both keys
        platform = data.get('platform', 'instagram').lower()
        
        # 1. Check if username is provided directly or via URL
        username = url.split('/')[-1] if '/' in url else url
        username = username.strip().lower().replace('@', '')
        
        # 2. Check Local Database (Real-Time Protection)
        try:
            from database import check_username
            community_report = check_username(username)
            if community_report:
                return jsonify({
                    'status': 'success',
                    'success': True, # Maintain compatibility
                    'username': username,
                    'is_local_report': True,
                    'score': {
                        'final_score': 10, # Critical Risk
                        'risk_level': 'CRITICAL - Flagged by Community',
                        'red_flags': [f"Reported {community_report['report_count']} times by users", f"Categories: {', '.join(community_report['categories'])}"],
                        'recommendations': ["Do not pay money.", "Block immediately.", "This profile is confirmed as dangerous."]
                    },
                    'analysis': { # Mock analysis structure for frontend compatibility
                        'metadata': {'followers': 0, 'following': 0, 'posts': 0},
                        'image': {'confidence': 0.99},
                        'text': {'originality_score': 0},
                        'behavior': {'is_bot_like': True}
                    },
                    'data_source': 'community_database'
                }), 200
        except Exception as e:
            logger.error(f"DB Check failed: {e}")
            pass # Continue to normal analysis

        # 3. Fallback to AI Analysis
        if not url:
            return jsonify({'success': False, 'error': 'URL is required'}), 400
            
        # Import service here to avoid circular imports
        try:
            try:
                from services.analyzer_service import AnalyzerService
            except ImportError:
                from app.services.analyzer_service import AnalyzerService
        except ImportError as e:
            return jsonify({'success': False, 'error': f'Service unavailable: {str(e)}'}), 503
            
        analyzer = AnalyzerService()
        result = analyzer.analyze(url, platform)
        
        # Save to in-memory storage (temporary legacy support)
        report_counter += 1
        report_id = f"report_{report_counter}"
        reports_storage[report_id] = {
            'profile_url': url,
            'platform': platform,
            'result': result,
            'timestamp': datetime.now()
        }
        result['report_id'] = report_id
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f'Analysis Error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@analysis_bp.route('/report', methods=['POST'])
def report_scam():
    """Submit a new scam report"""
    try:
        data = request.json
        
        # Handle import inside function to avoid circular imports if any
        try:
            from database import add_report
        except ImportError:
            from app.database import add_report
        
        # Get IP for rate limiting/logging
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        row_id = add_report(
            username=data.get('username'),
            platform=data.get('platform', 'instagram'),
            category=data.get('category', 'general'),
            description=data.get('description'),
            evidence=data.get('evidence'),
            ip_address=ip
        )
        
        if row_id:
            return jsonify({'success': True, 'id': row_id, 'message': 'Report submitted successfully'}), 201
        else:
            return jsonify({'success': False, 'error': 'Database error'}), 500
            
    except Exception as e:
        logger.error(f"Report Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@analysis_bp.route('/recent', methods=['GET'])
def recent_reports():
    """Get recent reports for the live ticker"""
    try:
        try:
            from database import get_recent_reports
        except ImportError:
            from app.database import get_recent_reports
            
        reports = get_recent_reports(limit=10)
        return jsonify({'success': True, 'reports': reports}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@analysis_bp.route('/manual', methods=['POST'])
def manual_audit():
    """Manual Profile Audit Endpoint"""
    logger.info("TEST LOG - MANUAL REQUEST RECEIVED")
    try:
        data = request.json
        
        try:
            from services.analyzer_service import AnalyzerService
        except ImportError:
            from app.services.analyzer_service import AnalyzerService
            
        analyzer = AnalyzerService()
        result = analyzer.analyze_manual(data)
        
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 400
            
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f'Manual Analysis Error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


@analysis_bp.route('/message', methods=['POST'])
def analyze_message():
    """Scam Message Detector Endpoint"""
    logger.info("TEST LOG - MESSAGE REQUEST RECEIVED")
    try:
        data = request.json
        text = data.get('message', '')
        
        if not text:
            return jsonify({'success': False, 'error': 'Message text required'}), 400
            
        try:
            from services.analyzer_service import AnalyzerService
        except ImportError:
            from app.services.analyzer_service import AnalyzerService
            
        analyzer = AnalyzerService()
        result = analyzer.analyze_message(text)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f'Message Analysis Error: {str(e)}')
        return jsonify({'success': False, 'error': str(e)}), 500


# Legacy/Batch Endpoints (kept for compatibility)

@analysis_bp.route('/analyze/batch', methods=['POST'])
def analyze_batch():
    try:
        data = request.get_json()
        profiles = data.get('profiles', [])
        
        if not profiles or not isinstance(profiles, list):
            return jsonify({'success': False, 'error': 'profiles must be a non-empty array'}), 400
        
        if len(profiles) > 10:
            return jsonify({'success': False, 'error': 'Maximum 10 profiles per batch'}), 400
        
        try:
            from services.analyzer_service import AnalyzerService
        except ImportError:
            from app.services.analyzer_service import AnalyzerService
        analyzer = AnalyzerService()
        
        results = []
        for profile in profiles:
            url = profile.get('url', '').strip()
            platform = profile.get('platform', 'instagram').lower()
            try:
                result = analyzer.analyze(url, platform)
                results.append({'url': url, 'platform': platform, 'success': True, 'score': result.get('score', {})})
            except Exception as e:
                results.append({'url': url, 'platform': platform, 'success': False, 'error': str(e)})
        
        return jsonify({'success': True, 'results': results, 'timestamp': datetime.now().isoformat()}), 200
    except Exception as e:
        logger.error(f'Batch analysis error: {str(e)}')
        return jsonify({'success': False, 'error': 'Batch analysis failed'}), 500

@analysis_bp.route('/history', methods=['GET'])
def get_analysis_history():
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        all_reports = []
        for report_id, report in reports_storage.items():
            report_copy = report.copy()
            report_copy['id'] = report_id
            report_copy['timestamp'] = report['timestamp'].isoformat()
            all_reports.append(report_copy)
        
        all_reports.sort(key=lambda x: x['timestamp'], reverse=True)
        paginated_reports = all_reports[offset:offset + limit]
        
        return jsonify({'success': True, 'reports': paginated_reports, 'pagination': {'limit': limit, 'offset': offset, 'total': len(all_reports)}}), 200
    except Exception as e:
        logger.error(f'Failed to retrieve history: {str(e)}')
        return jsonify({'success': False, 'error': 'Failed to retrieve history'}), 500

@analysis_bp.route('/statistics', methods=['GET'])
def get_statistics():
    try:
        total = len(reports_storage)
        high_risk = 0
        medium_risk = 0
        low_risk = 0
        total_score = 0
        
        for report in reports_storage.values():
            score = report['result']['score']['final_score']
            total_score += score
            if score >= 80: low_risk += 1
            elif score >= 50: medium_risk += 1
            else: high_risk += 1
        
        avg_score = total_score / total if total > 0 else 0
        stats = {'total_analyses': total, 'fake_detected': high_risk, 'suspicious': medium_risk, 'authentic': low_risk, 'average_score': round(avg_score, 2)}
        return jsonify({'success': True, 'statistics': stats}), 200
    except Exception as e:
        logger.error(f'Failed to get statistics: {str(e)}')
        return jsonify({'success': False, 'error': 'Failed to get statistics'}), 500