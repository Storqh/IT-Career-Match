"""
Chatbot Engine - Rule-based chatbot with externalized knowledge base
Loads knowledge from JSON file, provides Vietnamese diacritic normalization,
keyword matching, and context-aware responses.
"""
import json
import re
import unicodedata
from pathlib import Path
from typing import List, Dict, Optional
from functools import lru_cache

from database.database import save_chat_message, get_user_skills, get_user_cvs


# =========================================================
# Vietnamese Text Normalization
# =========================================================

VIETNAMESE_CHAR_MAP = {
    'à': 'a', 'á': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
    'ă': 'a', 'ằ': 'a', 'ắ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
    'â': 'a', 'ầ': 'a', 'ấ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
    'đ': 'd',
    'è': 'e', 'é': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
    'ê': 'e', 'ề': 'e', 'ế': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
    'ì': 'i', 'í': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
    'ò': 'o', 'ó': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
    'ô': 'o', 'ồ': 'o', 'ố': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
    'ơ': 'o', 'ờ': 'o', 'ớ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
    'ù': 'u', 'ú': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
    'ư': 'u', 'ừ': 'u', 'ứ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
    'ỳ': 'y', 'ý': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
    # Uppercase
    'À': 'A', 'Á': 'A', 'Ả': 'A', 'Ã': 'A', 'Ạ': 'A',
    'Ă': 'A', 'Ằ': 'A', 'Ắ': 'A', 'Ẳ': 'A', 'Ẵ': 'A', 'Ặ': 'A',
    'Â': 'A', 'Ầ': 'A', 'Ấ': 'A', 'Ẩ': 'A', 'Ẫ': 'A', 'Ậ': 'A',
    'Đ': 'D',
    'È': 'E', 'É': 'E', 'Ẻ': 'E', 'Ẽ': 'E', 'Ẹ': 'E',
    'Ê': 'E', 'Ề': 'E', 'Ế': 'E', 'Ể': 'E', 'Ễ': 'E', 'Ệ': 'E',
    'Ì': 'I', 'Í': 'I', 'Ỉ': 'I', 'Ĩ': 'I', 'Ị': 'I',
    'Ò': 'O', 'Ó': 'O', 'Ỏ': 'O', 'Õ': 'O', 'Ọ': 'O',
    'Ô': 'O', 'Ồ': 'O', 'Ố': 'O', 'Ổ': 'O', 'Ỗ': 'O', 'Ộ': 'O',
    'Ơ': 'O', 'Ờ': 'O', 'Ớ': 'O', 'Ở': 'O', 'Ỡ': 'O', 'Ợ': 'O',
    'Ù': 'U', 'Ú': 'U', 'Ủ': 'U', 'Ũ': 'U', 'Ụ': 'U',
    'Ư': 'U', 'Ừ': 'U', 'Ứ': 'U', 'Ử': 'U', 'Ữ': 'U', 'Ự': 'U',
    'Ỳ': 'Y', 'Ý': 'Y', 'Ỷ': 'Y', 'Ỹ': 'Y', 'Ỵ': 'Y',
}


def normalize_vietnamese(text: str) -> str:
    """
    Normalize Vietnamese text by removing diacritics.
    'tiếng việt' -> 'tieng viet'
    """
    result = []
    for char in text:
        result.append(VIETNAMESE_CHAR_MAP.get(char, char))
    return ''.join(result)


def normalize_text(text: str) -> str:
    """
    Full text normalization: lowercase, remove diacritics, extra spaces.
    """
    text = text.lower().strip()
    text = normalize_vietnamese(text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text


# =========================================================
# Knowledge Base Loading
# =========================================================

_KNOWLEDGE_BASE: List[Dict] = []
_KNOWLEDGE_BASE_NORMALIZED: List[Dict] = []


def load_knowledge_base() -> List[Dict]:
    """Load knowledge base from JSON file."""
    global _KNOWLEDGE_BASE, _KNOWLEDGE_BASE_NORMALIZED

    if _KNOWLEDGE_BASE:
        return _KNOWLEDGE_BASE

    kb_path = Path(__file__).parent / "knowledge_base.json"

    try:
        with open(kb_path, 'r', encoding='utf-8') as f:
            _KNOWLEDGE_BASE = json.load(f)

        # Pre-normalize keywords for faster matching
        for item in _KNOWLEDGE_BASE:
            normalized_keywords = [normalize_text(kw) for kw in item.get("keywords", [])]
            item["_normalized_keywords"] = normalized_keywords

        _KNOWLEDGE_BASE_NORMALIZED = _KNOWLEDGE_BASE
        print(f"[Chatbot] Loaded {len(_KNOWLEDGE_BASE)} knowledge entries")

    except FileNotFoundError:
        print(f"[Chatbot] WARNING: Knowledge base not found at {kb_path}")
        _KNOWLEDGE_BASE = []
    except json.JSONDecodeError as e:
        print(f"[Chatbot] ERROR: Invalid JSON in knowledge base: {e}")
        _KNOWLEDGE_BASE = []

    return _KNOWLEDGE_BASE


def reload_knowledge_base():
    """Force reload knowledge base (useful for development)."""
    global _KNOWLEDGE_BASE, _KNOWLEDGE_BASE_NORMALIZED
    _KNOWLEDGE_BASE = []
    _KNOWLEDGE_BASE_NORMALIZED = []
    return load_knowledge_base()


# =========================================================
# Matching Logic
# =========================================================

def calculate_match_score(user_msg_normalized: str, keywords: List[str]) -> float:
    """
    Calculate match score between user message and keywords.
    Returns 0-1 score: 1.0 if any keyword fully matches, proportional for partial.
    """
    if not keywords:
        return 0.0

    best_score = 0.0
    for kw in keywords:
        if kw in user_msg_normalized:
            # Full keyword match
            best_score = max(best_score, 1.0)
        else:
            # Partial match - check if keyword words appear in message
            kw_words = kw.split()
            if len(kw_words) > 1:
                matched_words = sum(1 for w in kw_words if w in user_msg_normalized)
                partial_score = matched_words / len(kw_words) * 0.5  # Max 0.5 for partial
                best_score = max(best_score, partial_score)

    return best_score


def find_best_match(user_message: str, threshold: float = 0.3) -> Optional[Dict]:
    """
    Find best matching knowledge entry for user message.
    Returns the entry with highest score above threshold.
    """
    kb = load_knowledge_base()
    if not kb:
        return None

    user_normalized = normalize_text(user_message)

    best_match = None
    best_score = 0.0

    for entry in kb:
        score = calculate_match_score(user_normalized, entry.get("_normalized_keywords", []))
        if score > best_score and score >= threshold:
            best_score = score
            best_match = entry

    return best_match


# =========================================================
# Context-Aware Responses
# =========================================================

def get_contextual_reply(user_id: int, user_message: str, base_reply: str) -> str:
    """
    Enhance reply with user context (skills, CV, recent activity).
    """
    try:
        # Get user skills
        skills = get_user_skills(user_id)
        skill_names = [s["skill_name"] for s in skills] if skills else []

        # Get latest CV
        cvs = get_user_cvs(user_id)
        latest_cv_skills = []
        if cvs:
            latest_cv_skills = cvs[0].get("extracted_skills", [])

        all_user_skills = list(set(skill_names + latest_cv_skills))

        # Add personalized suggestions based on skills
        if all_user_skills:
            skill_hints = []
            skill_lower = [s.lower() for s in all_user_skills]

            if any(s in skill_lower for s in ["react", "vue", "angular", "frontend", "javascript", "typescript"]):
                skill_hints.append("frontend")
            if any(s in skill_lower for s in ["node", "python", "java", "go", "backend", "api", "database", "sql"]):
                skill_hints.append("backend")
            if any(s in skill_lower for s in ["docker", "kubernetes", "aws", "azure", "gcp", "ci/cd", "terraform"]):
                skill_hints.append("devops")
            if any(s in skill_lower for s in ["machine learning", "tensorflow", "pytorch", "pandas", "data"]):
                skill_hints.append("data/ai")

            if skill_hints:
                base_reply += f"\n\n💡 **Dựa trên kỹ năng của bạn ({', '.join(skill_hints)})**, bạn có thể quan tâm:\n"
                if "frontend" in skill_hints:
                    base_reply += "• Roadmap Frontend, React/Next.js advanced, Performance optimization\n"
                if "backend" in skill_hints:
                    base_reply += "• System Design, Microservices, Database optimization\n"
                if "devops" in skill_hints:
                    base_reply += "• Kubernetes deep dive, GitOps, Platform Engineering\n"
                if "data/ai" in skill_hints:
                    base_reply += "• MLOps, LLM/RAG applications, Vector databases\n"

    except Exception as e:
        print(f"[Chatbot] Context error: {e}")

    return base_reply


# =========================================================
# Public API
# =========================================================

def get_bot_reply(user_message: str, user_id: int = None) -> str:
    """
    Main entry point: Get bot reply for user message.
    """
    if not user_message or not user_message.strip():
        return "Bạn chưa nhập tin nhắn. Hãy hỏi tôi về CV, tìm việc, phỏng vấn, hoặc lộ trình học tập nhé!"

    # Find matching knowledge
    match = find_best_match(user_message)

    if match:
        reply = match["reply"]

        # Add contextual info if user_id provided
        if user_id:
            reply = get_contextual_reply(user_id, user_message, reply)

        # Add follow-up suggestions
        follow_ups = match.get("follow_up", [])
        if follow_ups:
            kb = load_knowledge_base()
            follow_up_texts = []
            for fu_id in follow_ups[:3]:  # Limit to 3
                for entry in kb:
                    if entry["id"] == fu_id:
                        # Create short label from first keyword
                        label = entry["keywords"][0].title() if entry["keywords"] else fu_id
                        follow_up_texts.append(label)
                        break

            if follow_up_texts:
                reply += f"\n\n💬 **Gợi ý tiếp:** {', '.join(follow_up_texts)}"

        return reply

    # No match - fallback responses
    fallbacks = [
        "Tôi chưa hiểu câu hỏi. Bạn có thể thử hỏi về: viết CV, tìm việc IT, phỏng vấn kỹ thuật, lộ trình học Frontend/Backend/DevOps, đàm phán lương...",
        "Xin lỗi, tôi không có thông tin cho câu hỏi này. Hãy thử: 'CV frontend template', 'học backend roadmap', 'phỏng vấn system design', 'đàm phán lương'...",
        "Tôi chỉ hỗ trợ các chủ đề: CV, tìm việc, phỏng vấn, career path, skill roadmap, salary negotiation. Bạn muốn hỏi chủ đề nào?"
    ]

    import random
    return random.choice(fallbacks)


def get_suggestions() -> List[str]:
    """Get suggested questions for chatbot UI."""
    kb = load_knowledge_base()

    suggestions = []
    for entry in kb:
        if entry["keywords"]:
            # Use first keyword as suggestion
            suggestions.append(entry["keywords"][0].title())

    # Return unique suggestions, limited
    seen = set()
    unique = []
    for s in suggestions:
        if s.lower() not in seen:
            seen.add(s.lower())
            unique.append(s)

    return unique[:10]


def get_categories() -> List[str]:
    """Get available knowledge categories."""
    kb = load_knowledge_base()
    categories = list(set(entry.get("category", "general") for entry in kb))
    return sorted(categories)


def search_knowledge(query: str, limit: int = 5) -> List[Dict]:
    """Search knowledge base entries by query."""
    kb = load_knowledge_base()
    query_norm = normalize_text(query)

    results = []
    for entry in kb:
        score = calculate_match_score(query_norm, entry.get("_normalized_keywords", []))
        if score > 0:
            results.append({
                "id": entry["id"],
                "category": entry.get("category", "general"),
                "keywords": entry["keywords"][:3],
                "score": score
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]


# =========================================================
# Initialize on import
# =========================================================

load_knowledge_base()


if __name__ == "__main__":
    # Test
    print("=== Chatbot Engine Test ===\n")

    test_messages = [
        "viet cv frontend",
        "học backend roadmap",
        "phỏng vấn system design",
        "đàm phán lương",
        "tìm việc it",
        "xyz abc"
    ]

    for msg in test_messages:
        print(f"User: {msg}")
        reply = get_bot_reply(msg)
        print(f"Bot: {reply[:200]}...\n")

    print("=== Suggestions ===")
    print(get_suggestions())

    print("\n=== Categories ===")
    print(get_categories())