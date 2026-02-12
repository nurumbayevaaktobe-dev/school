from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from collections import defaultdict
from datetime import datetime, timedelta
import threading

class RateLimiter:
    """In-memory rate limiter with sliding window"""

    def __init__(self, max_calls, window_seconds):
        self.max_calls = max_calls
        self.window = window_seconds
        self.calls = defaultdict(list)
        self.lock = threading.Lock()

        # Cleanup old entries every minute
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()

    def allow(self, key):
        """Check if request is allowed"""
        with self.lock:
            now = datetime.now()
            cutoff = now - timedelta(seconds=self.window)

            # Remove old calls
            self.calls[key] = [ts for ts in self.calls[key] if ts > cutoff]

            # Check limit
            if len(self.calls[key]) < self.max_calls:
                self.calls[key].append(now)
                return True
            return False

    def _cleanup_loop(self):
        """Periodically clean up old entries"""
        while True:
            threading.Event().wait(60)  # Every minute
            with self.lock:
                cutoff = datetime.now() - timedelta(seconds=self.window * 2)
                for key in list(self.calls.keys()):
                    self.calls[key] = [ts for ts in self.calls[key] if ts > cutoff]
                    if not self.calls[key]:
                        del self.calls[key]

# Global rate limiters
ai_rate_limiter = RateLimiter(max_calls=15, window_seconds=60)  # 15/min
screenshot_rate_limiter = RateLimiter(max_calls=100, window_seconds=60)  # 100/min

def require_auth(role=None):
    """Decorator to require authentication"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()

                # Role check
                if role:
                    from models.user import User
                    user = User.query.get(user_id)
                    if not user or user.role != role:
                        return jsonify({'error': 'Unauthorized'}), 403

                return f(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': 'Invalid token'}), 401
        return decorated_function
    return decorator

def rate_limit(limiter, key_func=None):
    """Decorator for rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if key_func:
                key = key_func()
            else:
                key = request.remote_addr

            if not limiter.allow(key):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'retry_after': limiter.window
                }), 429

            return f(*args, **kwargs)
        return decorated_function
    return decorator
