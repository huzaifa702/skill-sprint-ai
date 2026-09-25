"""
SkillSprint AI - Authentication & Role-Based Access Control (RBAC)
Theme: OnboardVerse | Category: Generative AI PowerPlay

Supports 5 system roles:
- Administrator
- Training Manager
- Reviewer
- Manager
- Employee
"""

from functools import wraps
from typing import Any, Callable, Dict, List, Optional
from flask import g, jsonify, redirect, request, session, url_for
from src.database.db import query_one


def get_current_user() -> Optional[Dict[str, Any]]:
    """Retrieve logged-in user profile from session and database."""
    user_id = session.get("user_id")
    if not user_id:
        return None

    user = query_one(
        """
        SELECT u.user_id, u.username, u.email, u.full_name, u.is_active,
               sr.role_id as system_role_id, sr.name as role_name
        FROM users u
        JOIN system_roles sr ON u.system_role_id = sr.role_id
        WHERE u.user_id = ? AND u.is_active = 1
        """,
        (user_id,)
    )
    return user


def login_required(f: Callable) -> Callable:
    """Decorator to enforce user authentication on protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.is_json or request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required", "status": 401}), 401
            return redirect(url_for("auth.login_view", next=request.url))
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function


def roles_required(*allowed_roles: str) -> Callable:
    """Decorator to enforce specific system role permissions."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                if request.is_json or request.path.startswith("/api/"):
                    return jsonify({"error": "Authentication required", "status": 401}), 401
                return redirect(url_for("auth.login_view", next=request.url))

            if user["role_name"] not in allowed_roles:
                if request.is_json or request.path.startswith("/api/"):
                    return jsonify({
                        "error": "Forbidden",
                        "message": f"Requires one of roles: {', '.join(allowed_roles)}",
                        "user_role": user["role_name"],
                        "status": 403
                    }), 403
                return jsonify({"error": "Access Denied: Insufficient Role Permissions"}), 403

            g.current_user = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator
