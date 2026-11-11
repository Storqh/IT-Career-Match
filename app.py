"""
IT Career Match - Main Application Entry Point
Uses Flask application factory pattern.
"""
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Import factory
from app import create_app

# Create app instance
app = create_app()


if __name__ == "__main__":
    # Development server
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"

    print(f"Starting IT Career Match on port {port} (debug={debug})")
    app.run(host="0.0.0.0", port=port, debug=debug)