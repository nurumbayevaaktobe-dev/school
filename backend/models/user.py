from extensions import db, bcrypt
from datetime import datetime
import uuid

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # teacher/student

    # Student-specific
    computer_id = db.Column(db.String(100), unique=True, index=True)
    session_id = db.Column(db.String(100))  # Current WebSocket session
    status = db.Column(db.String(20), default='offline')  # online/offline/away
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    activities = db.relationship('Activity', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    violations = db.relationship('Violation', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verify password"""
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Serialize user data"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'status': self.status,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }
