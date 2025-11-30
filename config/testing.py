"""Testing Configuration"""
import os

class TestingConfig:
    """Testing environment configuration"""
    
    # Flask
    DEBUG = True
    TESTING = True
    PROPAGATE_EXCEPTIONS = True
    
    # Security
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False
    
    # Database - Use test database
    MONGO_URI = 'mongodb://localhost:27017/'
    MONGO_DB_NAME = 'fake_profile_detection_test'
    
    # Redis
    REDIS_URL = 'redis://localhost:6379/2'
    
    # Upload
    MAX_CONTENT_LENGTH = 52428800
    UPLOAD_FOLDER = 'tests/uploads'
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = 'logs/test.log'
    
    # API
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    
    # Cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
