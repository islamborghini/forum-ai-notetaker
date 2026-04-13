"""
Shared response helpers.

I separated this because I want all routes to return data
in a consistent structure. That makes frontend integration
cleaner and avoids random response formats.
"""

from flask import jsonify
from typing import Any


def success_response(message: str, data: Any = None, status_code: int = 200):
    """
    Standard success response format.
    """
    return jsonify({
        "success": True,
        "message": message,
        "data": data
    }), status_code


def error_response(message: str, status_code: int = 400):
    """
    Standard error response format.
    """
    return jsonify({
        "success": False,
        "error": message
    }), status_code