from extensions import db
from datetime import datetime

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    receiver_id = db.Column(db.String(36), db.ForeignKey('users.id'), index=True)  # null for broadcast

    message_type = db.Column(db.String(20), default='normal')  # normal, warning, info, success
    content = db.Column(db.Text, nullable=False)

    read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        """Serialize message data"""
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'type': self.message_type,
            'content': self.content,
            'read': self.read,
            'timestamp': self.timestamp.isoformat()
        }
