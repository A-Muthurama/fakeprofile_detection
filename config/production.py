"""Production Configuration"""
import os

class ProductionConfig:
    """Production environment configuration"""
    
    # Flask
    DEBUG = False
    TESTING = False
    PROPAGATE_EXCEPTIONS = False
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError('SECRET_KEY environment variable not set')
    
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    PREFERRED_URL_SCHEME = 'https'
    
    # Database
    MONGO_URI = os.getenv('MONGO_ATLAS_URI', os.getenv('MONGO_URI'))
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'fake_profile_detection')
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Upload
    MAX_CONTENT_LENGTH = 52428800  # 50MB
    UPLOAD_FOLDER = '/var/uploads'
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = '/var/log/app.log'
    
    # API
    JSON_SORT_KEYS = True
    JSONIFY_PRETTYPRINT_REGULAR = False
    
    # Cache
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/1')
    CACHE_DEFAULT_TIMEOUT = 3600
    
    # Error tracking
    SENTRY_ENABLED = os.getenv('SENTRY_ENABLED', 'True') == 'True'
    SENTRY_DSN = os.getenv('SENTRY_DSN')
