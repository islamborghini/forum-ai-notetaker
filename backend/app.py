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

    # Enable cross-origin requests so the React frontend can
    # communicate with the backend during development.
    CORS(app)

    # Create database tables if they do not exist yet.
    init_db()
    recover_interrupted_processing_sessions()

    # Resolve upload directory from the backend root so it stays stable
    # regardless of the process working directory.
    backend_root = Path(__file__).resolve().parent
    upload_folder = backend_root / "uploads"
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