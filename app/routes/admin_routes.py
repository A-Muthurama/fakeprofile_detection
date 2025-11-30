from flask import Blueprint, jsonify
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get admin statistics"""
    return jsonify({
        'success': True,
        'total_analyses': 0,
        'fake_detected': 0,
        'authentic': 0,
        'timestamp': datetime.now().isoformat()
    }), 200
