from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# Initialize extensions
db = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins='*', async_mode='threading')
cache = Cache()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
bcrypt = Bcrypt()
jwt = JWTManager()

def init_extensions(app):
    """Initialize all Flask extensions"""
    db.init_app(app)
    socketio.init_app(app, message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'])
    cache.init_app(app)
    limiter.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
