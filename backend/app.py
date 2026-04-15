"""
Main Flask application entry point.

This file creates the Flask server and registers all route groups.

In this project, the backend acts as the coordination layer. It
receives requests from the frontend, validates them, and connects
them to the rest of the system, including the processing pipeline
and the data layer.

The database schema and AI models are handled by other roles on
the team. My responsibility here is to keep the backend API clean,
organized, and easy to extend.
"""

from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

load_dotenv()

from forum_ai_notetaker.db import init_db

# Import route groups
from routes.sessions import sessions_bp
from routes.transcripts import transcripts_bp
from routes.notes import notes_bp
from routes.courses import courses_bp
from routes.auth import auth_bp


def create_app():
    """
    Create and configure the Flask application.

    Keeping app creation inside a function makes the backend easier
    to test, configure, and scale as the project grows.
    """
    app = Flask(__name__)

    # Enable cross-origin requests so the React frontend can
    # communicate with the backend during development.
    CORS(app)

    # Create database tables if they do not exist yet.
    init_db()

    # Resolve upload directory from the backend root so it stays stable
    # regardless of the process working directory.
    backend_root = Path(__file__).resolve().parent
    upload_folder = backend_root / "uploads"
    upload_folder.mkdir(parents=True, exist_ok=True)
    app.config["UPLOAD_FOLDER"] = str(upload_folder)

    # Register API route groups.
    app.register_blueprint(sessions_bp, url_prefix="/api/sessions")
    app.register_blueprint(transcripts_bp, url_prefix="/api/transcripts")
    app.register_blueprint(notes_bp, url_prefix="/api/notes")
    app.register_blueprint(courses_bp, url_prefix="/api/courses")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    @app.route("/", methods=["GET"])
    def home():
        """
        Root route used to confirm the API is running.

        This avoids a 404 at the base URL and gives a small hint
        about where to test the backend.
        """
        return {
            "message": "Backend API is running.",
            "hint": "Try /api/health to test the server.",
        }, 200

    @app.route("/api/health", methods=["GET"])
    def health():
        """
        Health check route used during development.

        This is a simple way to confirm that the backend server
        is running and reachable before testing real endpoints.
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
