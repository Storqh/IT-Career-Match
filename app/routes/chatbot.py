"""
Chatbot routes - Rule-based chatbot with externalized knowledge base
"""
from flask import Blueprint, render_template, request, jsonify, session
from functools import wraps

from ai.chatbot.engine import get_bot_reply, get_suggestions

chatbot_bp = Blueprint("chatbot", __name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function


@chatbot_bp.route("/chatbot", methods=["POST"])
@login_required
def chatbot_api():
    """Chatbot API endpoint."""
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"error": "Message required"}), 400

    user_message = data["message"].strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    user_id = session["user_id"]

    # Get bot reply
    reply = get_bot_reply(user_message, user_id)

    return jsonify({
        "reply": reply,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
    })


@chatbot_bp.route("/chatbot/suggestions")
@login_required
def chatbot_suggestions():
    """Get suggested questions for chatbot."""
    suggestions = get_suggestions()
    return jsonify({"suggestions": suggestions})


@chatbot_bp.route("/chatbot/history")
@login_required
def chatbot_history():
    """Get chat history for current user (last 50 messages)."""
    user_id = session["user_id"]

    from database.database import get_chat_history
    history = get_chat_history(user_id, limit=50)

    return jsonify({"history": history})