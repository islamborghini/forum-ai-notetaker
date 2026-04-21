"""
Application entry point.

This module creates and configures the Flask application that powers
the backend API.

The backend acts as the coordination layer of the system:
- receives requests from the frontend
- validates and authorizes users
- routes requests to the appropriate service layer
- connects to the processing pipeline and database

Blueprints and their URL prefixes:
    /api/auth        — authentication and user identity
    /api/sessions    — upload, retrieve, and search recordings
    /api/transcripts — access transcript data
    /api/notes       — access AI-generated notes
    /api/courses     — course creation and membership

This file intentionally does not implement business logic. Its role is
to assemble the application and wire together all components in a
centralized and maintainable way.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

load_dotenv()

from forum_ai_notetaker.db import init_db
from services.session_service import recover_interrupted_processing_sessions

# Import route groups
from routes.auth import auth_bp
from routes.courses import courses_bp
from routes.notes import notes_bp
from routes.sessions import sessions_bp
from routes.transcripts import transcripts_bp


def create_app() -> Flask:
    """
    Create and configure the Flask application instance.

    This function is responsible for:
    - initializing the database schema
    - configuring global settings (e.g., upload directory)
    - enabling CORS for frontend communication
    - registering all route blueprints

    Using an application factory pattern improves testability,
    modularity, and scalability by avoiding global state and
    allowing multiple app instances if needed.

    Returns:
        A fully configured Flask application instance.
    """
    app = Flask(__name__)

    # Refuse to boot in production with a placeholder/fallback secret.
    # utils/auth.py falls back to "dev-secret-key" (in the public repo) if
    # JWT_SECRET_KEY is unset; .env.example ships "CHANGE_ME". Block both.
    # Detection: Railway reliably injects RAILWAY_ENVIRONMENT; FLASK_ENV was
    # removed in Flask 2.3 and cannot be relied on.
    is_production = bool(os.environ.get("RAILWAY_ENVIRONMENT"))
    # Known-weak values that must not be used in prod. The team default
    # "cs162-forum-ai-notetaker-2026" is checked in to the public repo
    # (see .env.example) so it counts as public and is blocked here too.
    weak_secrets = {"", "dev-secret-key", "CHANGE_ME", "cs162-forum-ai-notetaker-2026"}
    if is_production:
        if os.environ.get("JWT_SECRET_KEY", "") in weak_secrets:
            raise RuntimeError(
                "JWT_SECRET_KEY must be set to a real value in production "
                "(not blank, not 'dev-secret-key', not 'CHANGE_ME')"
            )
        # Professor-registration gate is a no-op if the secret is missing,
        # so require it explicitly in prod to avoid silent open registration.
        if os.environ.get("PROFESSOR_REGISTRATION_SECRET", "") in weak_secrets:
            raise RuntimeError(
                "PROFESSOR_REGISTRATION_SECRET must be set in production"
            )

    # Cap upload size at the Flask layer. nginx on the frontend has a 500M
    # cap but direct POSTs to the backend public URL bypass nginx entirely.
    app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024

    # CORS is env-driven. Pass "*" as a literal string (not ["*"]) because
    # flask-cors treats them differently on credentialed requests.
    raw_origins = os.environ.get("CORS_ORIGINS", "*").strip()
    cors_origins: object
    if raw_origins == "*":
        cors_origins = "*"
    else:
        cors_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
    CORS(
        app,
        resources={r"/api/*": {"origins": cors_origins}},
        expose_headers=["Content-Range", "Accept-Ranges", "Content-Length"],
    )

    # Create database tables if they do not exist yet.
    init_db()
    recover_interrupted_processing_sessions()

    # Upload directory is env-overridable so it can point at a Railway volume.
    backend_root = Path(__file__).resolve().parent
    upload_folder = Path(os.environ.get("UPLOAD_FOLDER", str(backend_root / "uploads")))
    upload_folder.mkdir(parents=True, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = str(upload_folder)

    # Register API route groups.
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(sessions_bp, url_prefix="/api/sessions")
    app.register_blueprint(transcripts_bp, url_prefix="/api/transcripts")
    app.register_blueprint(notes_bp, url_prefix="/api/notes")
    app.register_blueprint(courses_bp, url_prefix="/api/courses")

    @app.route("/", methods=["GET"])
    def home():
        """
        Root endpoint for basic API verification.
        """
        return {
            "message": "Backend API is running.",
            "hint": "Try /api/health to test the server.",
        }, 200

    @app.route("/api/health", methods=["GET"])
    def health():
        """
        Health check endpoint.
        """
        return {
            "status": "ok",
            "message": "Backend is running",
        }, 200

    return app


# Create the Flask application instance
app = create_app()


if __name__ == "__main__":
    # Run the development server with auto-reload enabled.
    app.run(debug=True)