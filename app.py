"""
SkillSprint AI - Web-Based Employee Onboarding Intelligence Platform
Theme: OnboardVerse | Category: Generative AI PowerPlay

Flask Application Entry Point
"""

import os
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv

from src.core.config import BASE_DIR, DB_PATH, SECRET_KEY
from src.database.db import init_db
from src.database.seed_data import seed_database
from src.routes.app_routes import routes_bp
from src.routes.auth_routes import auth_bp

load_dotenv()


def create_app() -> Flask:
    """Application factory for SkillSprint AI."""
    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static")
    )

    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

    # Ensure DB is created
    if not os.path.exists(DB_PATH):
        seed_database()

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)

    # Error Handlers
    @app.errorhandler(404)
    def handle_not_found(e):
        return render_template("base.html", content_override="<div class='card-3d'><h2>404 - Page Not Found</h2><p>The requested resource does not exist.</p></div>"), 404

    @app.errorhandler(403)
    def handle_forbidden(e):
        return render_template("base.html", content_override="<div class='card-3d'><h2>403 - Access Denied</h2><p>You do not have permission to access this resource.</p></div>"), 403

    @app.errorhandler(500)
    def handle_server_error(e):
        return render_template("base.html", content_override="<div class='card-3d'><h2>500 - System Error</h2><p>An unexpected technical exception occurred.</p></div>"), 500

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting SkillSprint AI Platform on http://127.0.0.1:{port} ...")
    app.run(host="0.0.0.0", port=port, debug=True)
