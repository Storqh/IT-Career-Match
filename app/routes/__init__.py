"""
App routes package - Blueprint registration
"""
from app.routes.auth import auth_bp
from app.routes.profile import profile_bp
from app.routes.jobs import jobs_bp
from app.routes.cv import cv_bp
from app.routes.admin import admin_bp
from app.routes.chatbot import chatbot_bp

__all__ = [
    "auth_bp",
    "profile_bp",
    "jobs_bp",
    "cv_bp",
    "admin_bp",
    "chatbot_bp",
]