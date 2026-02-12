import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///classguard.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

    # Redis Cache
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TYPE = 'redis'
    CACHE_DEFAULT_TIMEOUT = 300

    # SocketIO
    SOCKETIO_MESSAGE_QUEUE = os.environ.get('REDIS_URL')
    SOCKETIO_CORS_ALLOWED_ORIGINS = '*'

    # Security
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    BCRYPT_LOG_ROUNDS = 12

    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL')
    RATELIMIT_DEFAULT = "100 per hour"

    # AI Configuration
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    GEMINI_MODEL = 'gemini-1.5-flash'  # Fast and free
    AI_RATE_LIMIT = 15  # requests per minute (free tier)
    AI_TIMEOUT = 10  # seconds

    # Image Compression
    SCREENSHOT_QUALITY = 60  # JPEG quality (1-100)
    SCREENSHOT_MAX_WIDTH = 1280
    SCREENSHOT_MAX_HEIGHT = 720

    # Monitoring
    SCREENSHOT_INTERVAL = 3  # seconds
    MAX_STUDENTS = 50

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # Use PostgreSQL in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
