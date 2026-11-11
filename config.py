"""
Configuration management for IT Career Match.
Supports Development, Production, and Testing environments.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


class Config:
    """Base configuration class."""

    # Flask
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")

    # Database
    DATABASE_URL = os.environ.get("DATABASE_URL")

    # Email (Brevo/Sendinblue)
    BREVO_API_KEY = os.environ.get("BREVO_API_KEY")
    BREVO_SENDER_EMAIL = os.environ.get("BREVO_SENDER_EMAIL", "noreply@example.com")
    BREVO_SENDER_NAME = os.environ.get("BREVO_SENDER_NAME", "IT Career Match")

    # Upload
    UPLOAD_FOLDER = BASE_DIR / "uploads"
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {"pdf", "docx"}

    # Session
    SESSION_COOKIE_SECURE = False  # Set True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Pagination
    JOBS_PER_PAGE = 9
    RECOMMENDATIONS_TOP_K = 5

    # ML Models
    MODELS_DIR = BASE_DIR / "models"
    TFIDF_PATH = MODELS_DIR / "tfidf_vectorizer.joblib"
    CAREER_MODEL_PATH = MODELS_DIR / "career_classifier.joblib"

    # Chatbot
    CHATBOT_KNOWLEDGE_PATH = BASE_DIR / "ai" / "chatbot" / "knowledge_base.json"

    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = "development"
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = "production"
    SESSION_COOKIE_SECURE = True  # Requires HTTPS
    LOG_LEVEL = "WARNING"

    # Override with production values from env
    SECRET_KEY = os.environ.get("SECRET_KEY")

    @classmethod
    def validate(cls):
        """Validate required production settings."""
        errors = []
        if not cls.SECRET_KEY or cls.SECRET_KEY == "dev-secret-key-change-in-production":
            errors.append("SECRET_KEY must be set in production")
        if not cls.DATABASE_URL:
            errors.append("DATABASE_URL must be set")
        if not cls.BREVO_API_KEY:
            errors.append("BREVO_API_KEY must be set")
        if errors:
            raise ValueError("Production config errors: " + "; ".join(errors))


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    FLASK_ENV = "testing"

    # Database operations should be mocked in tests; the app uses PostgreSQL.
    DATABASE_URL = None

    # Disable email sending in tests
    BREVO_API_KEY = None

    # Fast hashing for tests
    BCRYPT_ROUNDS = 4

    LOG_LEVEL = "DEBUG"

    # Disable CSRF in tests
    WTF_CSRF_ENABLED = False


# Config dictionary for easy lookup
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}


def get_config():
    """Get configuration class based on FLASK_ENV."""
    env = os.environ.get("FLASK_ENV", "development").lower()
    return config.get(env, config["default"])