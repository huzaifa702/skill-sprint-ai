"""
SkillSprint AI - Authentication Routes & Fast Evaluator Access
Theme: OnboardVerse | Category: Generative AI PowerPlay
"""

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from src.core.auth import get_current_user
from src.core.security import verify_password
from src.database.db import execute_commit, query_one

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login_view():
    """Render login page and handle authentication."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = query_one(
            """
            SELECT u.user_id, u.username, u.password_hash, u.full_name, u.is_active,
                   sr.role_id as system_role_id, sr.name as role_name
            FROM users u
            JOIN system_roles sr ON u.system_role_id = sr.role_id
            WHERE u.username = ?
            """,
            (username,)
        )

        if user and user["is_active"] and verify_password(password, user["password_hash"]):
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["role_name"] = user["role_name"]

            # Update last login safely
            try:
                execute_commit("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?", (user["user_id"],))
            except Exception:
                pass

            flash(f"Welcome back, {user['full_name']}!", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("routes.dashboard_view"))
        else:
            flash("Invalid username or password. Please try again.", "error")

    return render_template("login.html")


@auth_bp.route("/fast-login", methods=["GET", "POST"])
def fast_login():
    """1-Click evaluator fast login for competition judges."""
    role_name = request.form.get("role_name") or request.args.get("role_name") or "Administrator"
    
    # Try exact match by system role name
    user = query_one(
        """
        SELECT u.user_id, u.username, u.full_name, sr.name as role_name
        FROM users u
        JOIN system_roles sr ON u.system_role_id = sr.role_id
        WHERE sr.name = ? AND u.is_active = 1
        LIMIT 1
        """,
        (role_name,)
    )

    # Fallback: match by username or substring
    if not user:
        user = query_one(
            """
            SELECT u.user_id, u.username, u.full_name, sr.name as role_name
            FROM users u
            JOIN system_roles sr ON u.system_role_id = sr.role_id
            WHERE (u.username = ? OR sr.name LIKE ?) AND u.is_active = 1
            LIMIT 1
            """,
            (role_name.lower(), f"%{role_name}%")
        )

    if user:
        session["user_id"] = user["user_id"]
        session["username"] = user["username"]
        session["role_name"] = user["role_name"]

        try:
            execute_commit("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?", (user["user_id"],))
        except Exception:
            pass

        flash(f"Authenticated as {user['full_name']} ({user['role_name']})", "success")
        return redirect(url_for("routes.dashboard_view"))

    flash("Could not perform fast login for requested role.", "error")
    return redirect(url_for("auth.login_view"))


@auth_bp.route("/logout")
def logout():
    """Clear session and log out."""
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("routes.landing_view"))
