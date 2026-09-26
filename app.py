"""
SkillSprint AI - Web-Based Employee Onboarding Intelligence Platform
Theme: OnboardVerse | Category: Generative AI PowerPlay

Flask Application Entry Point
"""

import os
from flask import Flask, jsonify, render_template, send_from_directory
from dotenv import load_dotenv

from src.core.config import BASE_DIR, DB_PATH, SECRET_KEY
from src.database.db import init_db
from src.database.seed_data import seed_database
from src.routes.app_routes import routes_bp
from src.routes.auth_routes import auth_bp

load_dotenv()


def create_app() -> Flask:
    """Application factory for SkillSprint AI."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static"),
        static_url_path="/static"
    )

    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

    # Ensure DB is created or mirrored
    from src.database.db import resolve_db_path
    effective_db = resolve_db_path()
    if not os.path.exists(effective_db) or os.path.getsize(effective_db) == 0:
        try:
            seed_database()
        except Exception as ex:
            print(f"[SkillSprint App] Database init notice: {ex}")

    # Explicit static file handler for serverless hosting (Vercel / AWS Lambda)
    @app.route("/static/<path:filename>")
    def serve_static(filename):
        return send_from_directory(os.path.join(base_dir, "static"), filename)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)

    # Error Handlers
    @app.errorhandler(404)
    def handle_not_found(e):
        return render_template(
            "base.html",
            content_override="""
            <div class="card-3d" style="max-width: 580px; margin: 40px auto; border-top: 3px solid var(--status-warning); padding: 32px; text-align: center;">
                <h2 style="color: var(--status-warning); margin-bottom: 12px; font-size: 22px;">404 - Page Not Found</h2>
                <p style="color: var(--text-secondary); margin-bottom: 20px;">The requested resource or page does not exist.</p>
                <a href="/" class="btn btn-primary btn-sm">Return Home</a>
            </div>
            """
        ), 404

    @app.errorhandler(403)
    def handle_forbidden(e):
        return render_template(
            "base.html",
            content_override="""
            <div class="card-3d" style="max-width: 580px; margin: 40px auto; border-top: 3px solid var(--status-critical); padding: 32px; text-align: center;">
                <h2 style="color: var(--status-critical); margin-bottom: 12px; font-size: 22px;">403 - Access Denied</h2>
                <p style="color: var(--text-secondary); margin-bottom: 20px;">You do not have permission to access this resource.</p>
                <a href="/login" class="btn btn-primary btn-sm">Sign In</a>
            </div>
            """
        ), 403

    @app.errorhandler(500)
    def handle_server_error(e):
        import traceback
        err_msg = str(e)
        print(f"[SkillSprint 500 Error] {err_msg}", flush=True)
        return render_template(
            "base.html",
            content_override=f"""
            <div class="card-3d" style="max-width: 620px; margin: 40px auto; border-top: 3px solid var(--status-critical); padding: 32px;">
                <h2 style="color: var(--status-critical); margin-bottom: 12px; font-size: 22px;">500 - System Exception</h2>
                <p style="color: var(--text-secondary); margin-bottom: 16px;">An unexpected error occurred while processing this request.</p>
                <div style="background-color: var(--bg-primary); border: 1px solid var(--border-subtle); padding: 12px 16px; border-radius: var(--radius-sm); font-family: monospace; font-size: 12px; color: var(--status-critical); word-break: break-all; margin-bottom: 20px;">
                    {err_msg}
                </div>
                <div style="display: flex; gap: 12px;">
                    <a href="/login" class="btn btn-primary btn-sm">Return to Sign In</a>
                    <a href="/" class="btn btn-secondary btn-sm">Home Page</a>
                </div>
            </div>
            """
        ), 500

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting SkillSprint AI Platform on http://127.0.0.1:{port} ...")
    app.run(host="0.0.0.0", port=port, debug=True)
