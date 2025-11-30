"""Application configuration loader"""
import os
from dotenv import load_dotenv

load_dotenv()

# Import based on environment
if os.getenv('FLASK_ENV') == 'production':
    from config.production import ProductionConfig as Config
elif os.getenv('FLASK_ENV') == 'testing':
    from config.testing import TestingConfig as Config
else:
    from config.development import DevelopmentConfig as Config

__all__ = ['Config']
