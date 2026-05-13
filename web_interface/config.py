"""
Configuration for DeepFaceLab Web Interface
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration"""
    
    # Flask Settings
    HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    PORT = int(os.getenv('FLASK_PORT', 5000))
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # File Upload Settings
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', './uploads')
    OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', './output')
    MODELS_FOLDER = os.getenv('MODELS_FOLDER', './models')
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_FILE_SIZE_MB', 100)) * 1024 * 1024
    
    # DeepFaceLab Settings
    DEEPFACELAB_PATH = os.getenv('DEEPFACELAB_PATH', './')
    DEEPFACELAB_WORKSPACE = os.getenv('DEEPFACELAB_WORKSPACE', './workspace')
    
    # Video Processing Settings
    VIDEO_CODEC = os.getenv('VIDEO_CODEC', 'libx264')
    VIDEO_QUALITY = int(os.getenv('VIDEO_QUALITY', 23))  # 0-51, lower is better
    VIDEO_FPS = int(os.getenv('VIDEO_FPS', 30))
    
    # GPU Settings
    USE_GPU = os.getenv('USE_GPU', 'True').lower() == 'true'
    GPU_DEVICE_ID = int(os.getenv('GPU_DEVICE_ID', 0))
    
    # Logging Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', './logs/deepfacelab_web.log')
    
    # Cleanup Settings
    AUTO_CLEANUP = os.getenv('AUTO_CLEANUP', 'True').lower() == 'true'
    CLEANUP_AGE_DAYS = int(os.getenv('CLEANUP_AGE_DAYS', 7))
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        'video': {'mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm'},
        'image': {'jpg', 'jpeg', 'png', 'bmp', 'gif', 'tiff'},
    }


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    # In production, use environment variables for sensitive data
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is required in production")


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    UPLOAD_FOLDER = './test_uploads'
    OUTPUT_FOLDER = './test_output'
    MODELS_FOLDER = './test_models'


# Get configuration based on environment
config_name = os.getenv('FLASK_ENV', 'development')
if config_name == 'production':
    config = ProductionConfig
elif config_name == 'testing':
    config = TestingConfig
else:
    config = DevelopmentConfig
