"""
Main Flask application entry point.

This file is responsible for starting the backend server and
registering all route groups.

In our project the backend acts as the coordination layer.
It receives requests from the frontend, validates them, and
connects those requests to the rest of the system such as the
processing pipeline and the database layer.

I am not implementing the database schema or AI models here.
Those belong to other roles on the team. My responsibility is
to build a clean backend API that connects everything together.
"""

from flask import Flask
from flask_cors import CORS

from forum_ai_notetaker.db import init_db

# Import route groups
from routes.sessions import sessions_bp
from routes.transcripts import transcripts_bp
from routes.notes import notes_bp


def create_app():
    """
    Application factory.

    Keeping app creation inside a function makes the backend
    easier to configure, test, and expand later.
    """

    app = Flask(__name__)

    # Enable cross-origin requests so the React frontend
    # can communicate with the backend server.
    CORS(app)

    # Create tables if they don't exist yet.
    init_db()

    # Configuration
    # Uploaded recordings will be stored locally for now.
    app.config["UPLOAD_FOLDER"] = "uploads"

    # Register API route groups
    app.register_blueprint(sessions_bp, url_prefix="/api/sessions")
    app.register_blueprint(transcripts_bp, url_prefix="/api/transcripts")
    app.register_blueprint(notes_bp, url_prefix="/api/notes")

    @app.route("/", methods=["GET"])
    def home():
        """
        Root route.

        This prevents the base URL from returning a 404 and
        provides a quick message confirming the API is running.
        """
        return {
            "message": "Backend API is running.",
            "hint": "Try /api/health to test the server."
        }, 200

    @app.route("/api/health", methods=["GET"])
    def health():
        """
        Health check endpoint.

        This route is mainly used during development to confirm
        that the backend server is running and reachable.
        """
        return {
            "status": "ok",
            "message": "Backend is running"
        }, 200

    return app


# Create the Flask application
app = create_app()


if __name__ == "__main__":
    """
    Run the development server.

    Debug mode is enabled so the server automatically reloads
    when code changes during development.
    """
    app.run(debug=True)