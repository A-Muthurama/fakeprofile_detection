"""
Fake Profile Detection System - Main Flask Application
Entry point for the web application
"""

import os
import sys
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

# Load environment variables
load_dotenv()

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ============================================
# Flask App Initialization
# ============================================

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # Load config
    if config_name == 'production':
        from config.production import ProductionConfig as Config
    elif config_name == 'testing':
        from config.testing import TestingConfig as Config
    else:
        from config.development import DevelopmentConfig as Config
    
    app.config.from_object(Config)
    
    # Setup logging
    setup_logging(app)
    
    # Initialize extensions
    CORS(app, resources={
        r"/api/*": {
            "origins": os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(','),
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Create necessary directories
    create_directories()
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints (routes)
    register_blueprints(app)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': os.getenv('APP_VERSION', '1.0.0')
        }), 200
    
    # Root endpoint
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # API info endpoint
    @app.route('/api/info', methods=['GET'])
    def api_info():
        return jsonify({
            'app_name': os.getenv('APP_NAME', 'Fake Profile Detection System'),
            'version': os.getenv('APP_VERSION', '1.0.0'),
            'api_version': os.getenv('API_VERSION', 'v1'),
            'environment': os.getenv('FLASK_ENV', 'development')
        }), 200
    
    return app


# ============================================
# Logging Setup
# ============================================

def setup_logging(app):
    """Configure application logging"""
    
    # Remove default handler
    if app.logger.hasHandlers():
        app.logger.handlers.clear()
    
    # Log level
    log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO'))
    app.logger.setLevel(log_level)
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # File handler
    file_handler = RotatingFileHandler(
        os.getenv('LOG_FILE', 'logs/app.log'),
        maxBytes=int(os.getenv('LOG_MAX_SIZE', 10485760)),
        backupCount=int(os.getenv('LOG_BACKUP_COUNT', 10))
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    
    # Formatter (WITHOUT emoji characters to avoid Windows encoding issues)
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    
    app.logger.info('========== Application Started ==========')
    app.logger.info(f'Environment: {os.getenv("FLASK_ENV", "development")}')
    app.logger.info(f'Debug: {os.getenv("DEBUG", False)}')


# ============================================
# Error Handlers
# ============================================

def register_error_handlers(app):
    """Register global error handlers"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'error': 'Bad Request',
            'message': str(error),
            'status': 400
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required',
            'status': 401
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource',
            'status': 403
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found',
            'status': 404
        }), 404
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return jsonify({
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests. Please try again later.',
            'status': 429
        }), 429
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal Server Error: {str(error)}')
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred',
            'status': 500
        }), 500
    
    @app.errorhandler(503)
    def service_unavailable(error):
        return jsonify({
            'error': 'Service Unavailable',
            'message': 'The service is temporarily unavailable',
            'status': 503
        }), 503


# ============================================
# Blueprint Registration
# ============================================

def register_blueprints(app):
    """Register all route blueprints"""
    
    try:
        from routes.analysis_routes import analysis_bp
        app.register_blueprint(analysis_bp, url_prefix='/api/v1')
        app.logger.info('Analysis routes registered [OK]')
    except Exception as e:
        app.logger.error(f'Failed to register analysis routes: {str(e)}')
    
    try:
        from routes.health_routes import health_bp
        app.register_blueprint(health_bp, url_prefix='/api/v1')
        app.logger.info('Health routes registered [OK]')
    except Exception as e:
        app.logger.error(f'Failed to register health routes: {str(e)}')
    
    try:
        from routes.admin_routes import admin_bp
        app.register_blueprint(admin_bp, url_prefix='/api/v1/admin')
        app.logger.info('Admin routes registered [OK]')
    except Exception as e:
        app.logger.error(f'Failed to register admin routes: {str(e)}')


# ============================================
# Directory Creation
# ============================================

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        'logs',
        'uploads',
        'temp',
        'reports',
        'ml_models/trained_models',
        'static/uploads'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


# ============================================
# Development Server
# ============================================
app = create_app()
if __name__ == '__main__':
    # Run development server
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', True) == 'True'
    
    print(f"""
╔════════════════════════════════════════════════════════════╗
║     Fake Profile Detection System - Starting Server         ║
║════════════════════════════════════════════════════════════║
║  URL:     http://{host}:{port}
║  Debug:   {debug}
║  Env:     {os.getenv('FLASK_ENV', 'development')}
╚════════════════════════════════════════════════════════════╝
    """)
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=True,
        use_debugger=True
    )