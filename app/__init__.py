"""
IT Career Match - Application Factory
Flask app factory pattern with blueprint registration.
"""
import os
import sys
import logging
from pathlib import Path
from flask import Flask, session, g
from dotenv import load_dotenv
from werkzeug.local import LocalProxy

# Load .env file BEFORE importing config (config reads os.environ at import time)
load_dotenv()

from config import config, get_config

# Import database functions
from database.connection_pool import get_db_pool, close_db_pool

# Import routes
from app.routes.auth import auth_bp
from app.routes.profile import profile_bp
from app.routes.jobs import jobs_bp
from app.routes.cv import cv_bp
from app.routes.admin import admin_bp
from app.routes.chatbot import chatbot_bp


def create_app(config_name=None):
    """
    Application factory function.

    Args:
        config_name: Configuration name ('development', 'production', 'testing')
                    If None, uses FLASK_ENV environment variable.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__,
                template_folder="../templates",
                static_folder="../static")

    # Load configuration
    if config_name is None:
        if os.environ.get("FLASK_ENV") is None and "pytest" in sys.modules:
            config_name = "testing"
    if config_name is None:
        config_class = get_config()
    else:
        config_class = config.get(config_name, config["default"])

    app.config.from_object(config_class)

    # Validate production config
    if config_class.__name__ == "ProductionConfig":
        config_class.validate()

    # Ensure upload folder exists
    upload_folder = Path(app.config["UPLOAD_FOLDER"])
    upload_folder.mkdir(parents=True, exist_ok=True)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, app.config["LOG_LEVEL"]),
        format=app.config["LOG_FORMAT"]
    )

    # Tests mock database operations and must not require a live database.
    if not app.config.get("TESTING"):
        with app.app_context():
            get_db_pool(app.config["DATABASE_URL"])

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(jobs_bp, url_prefix="/jobs")
    app.register_blueprint(cv_bp, url_prefix="/cv")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(chatbot_bp, url_prefix="/api")

    # Custom Jinja filters
    @app.template_filter("remove_filter")
    def remove_filter(filters_dict, key_to_remove):
        """Return new dict without the specified key."""
        return {k: v for k, v in filters_dict.items() if k != key_to_remove}

    @app.template_filter("merge")
    def merge_dicts(dict1, dict2):
        """Merge two dicts, dict2 overrides dict1."""
        result = dict1.copy()
        result.update(dict2)
        return result

    # Add built-in functions to template globals
    app.jinja_env.globals.update(max=max, min=min, range=range)

    # Health check endpoint
    @app.route("/health")
    def health_check():
        return {"status": "healthy", "service": "it-career-match"}, 200

    # Root route - landing page
    @app.route("/")
    def index():
        from flask import render_template
        return render_template("index.html")

    # Context processor for templates
    @app.context_processor
    def inject_user():
        if app.config.get("TESTING"):
            return dict(current_user=None)

        user = getattr(g, 'user', None)
        if not user and 'user_id' in session:
            from database.database import get_user_by_id
            user = get_user_by_id(session['user_id'])
            g.user = user
        return dict(current_user=user)

    # Teardown
    @app.teardown_appcontext
    def teardown_db_pool(exception=None):
        pass  # Pool managed separately

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        app.logger.error(f"Internal server error: {error}")
        return render_template("errors/500.html"), 500

    return app


_default_app = None


def _get_default_app():
    global _default_app
    if _default_app is None:
        _default_app = create_app()
    return _default_app


# Keep the WSGI-compatible default app without connecting to the database at import time.
app = LocalProxy(_get_default_app)