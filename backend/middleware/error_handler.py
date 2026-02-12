"""Global error handling middleware for Flask application"""

from flask import jsonify
from werkzeug.exceptions import HTTPException
import logging

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    """Register error handlers for the Flask application"""

    @app.errorhandler(Exception)
    def handle_generic_error(e):
        """Handle all uncaught exceptions"""
        # Handle HTTP exceptions specially
        if isinstance(e, HTTPException):
            return jsonify({
                'error': e.description,
                'status': e.code
            }), e.code

        # Log the error
        app.logger.error(f'Unhandled exception: {str(e)}', exc_info=True)
        logger.error(f'Unhandled exception: {str(e)}', exc_info=True)

        # Return generic error to client
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred. Please try again later.'
        }), 500

    @app.errorhandler(400)
    def bad_request(e):
        """Handle bad request errors"""
        return jsonify({
            'error': 'Bad Request',
            'message': str(e.description) if e.description else 'The request was invalid'
        }), 400

    @app.errorhandler(401)
    def unauthorized(e):
        """Handle unauthorized errors"""
        return jsonify({
            'error': 'Unauthorized',
            'message': 'Authentication required'
        }), 401

    @app.errorhandler(403)
    def forbidden(e):
        """Handle forbidden errors"""
        return jsonify({
            'error': 'Forbidden',
            'message': 'You do not have permission to access this resource'
        }), 403

    @app.errorhandler(404)
    def not_found(e):
        """Handle not found errors"""
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested resource was not found'
        }), 404

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        """Handle rate limit errors"""
        return jsonify({
            'error': 'Rate Limit Exceeded',
            'message': 'Too many requests. Please try again later.',
            'retry_after': getattr(e, 'retry_after', 60)
        }), 429

    @app.errorhandler(500)
    def internal_server_error(e):
        """Handle internal server errors"""
        app.logger.error(f'Internal server error: {str(e)}', exc_info=True)
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An internal error occurred. Please try again later.'
        }), 500

    @app.errorhandler(503)
    def service_unavailable(e):
        """Handle service unavailable errors"""
        return jsonify({
            'error': 'Service Unavailable',
            'message': 'The service is temporarily unavailable. Please try again later.'
        }), 503

    # Custom error for AI service failures
    @app.errorhandler(Exception)
    def handle_ai_error(e):
        """Handle AI service specific errors"""
        error_message = str(e)

        if 'gemini' in error_message.lower() or 'api' in error_message.lower():
            app.logger.warning(f'AI Service error: {error_message}')
            return jsonify({
                'error': 'AI Service Error',
                'message': 'AI analysis is temporarily unavailable. Using fallback analysis.',
                'fallback': True
            }), 503

        # Re-raise if not AI related
        raise e


def create_error_response(error_type, message, status_code=500, **kwargs):
    """
    Helper function to create standardized error responses

    Args:
        error_type: Type of error (e.g., 'ValidationError', 'NotFoundError')
        message: Human-readable error message
        status_code: HTTP status code
        **kwargs: Additional fields to include in response

    Returns:
        Tuple of (json_response, status_code)
    """
    response = {
        'error': error_type,
        'message': message,
        'status': status_code
    }

    # Add any additional fields
    response.update(kwargs)

    return jsonify(response), status_code
