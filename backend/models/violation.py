from extensions import db
from datetime import datetime

class Violation(db.Model):
    __tablename__ = 'violations'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)

    violation_type = db.Column(db.String(50), nullable=False, index=True)
    # Types: game, social_media, video, blocked_url, plagiarism, idle

    detail = db.Column(db.Text)
    severity = db.Column(db.String(20), default='medium')  # low/medium/high

    resolved = db.Column(db.Boolean, default=False)
    resolved_by = db.Column(db.String(36), db.ForeignKey('users.id'))
    resolved_at = db.Column(db.DateTime)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        db.Index('idx_user_type_time', 'user_id', 'violation_type', 'timestamp'),
    )
