from extensions import db
from datetime import datetime
import json

class Activity(db.Model):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)

    # Screenshot data (stored separately in Redis/S3 for large files)
    screenshot_key = db.Column(db.String(200))  # Reference to cached image
    screenshot_hash = db.Column(db.String(64))  # For deduplication

    # Activity metadata
    active_window = db.Column(db.String(500))
    active_app = db.Column(db.String(200), index=True)
    processes = db.Column(db.Text)  # JSON array of processes
    urls = db.Column(db.Text)  # JSON array of URLs

    # Metrics
    idle_time = db.Column(db.Integer, default=0)  # seconds
    keyboard_events = db.Column(db.Integer, default=0)
    mouse_events = db.Column(db.Integer, default=0)

    # AI Analysis (cached)
    ai_analysis = db.Column(db.Text)  # JSON of AI insights

    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    @property
    def processes_list(self):
        """Parse processes JSON"""
        try:
            return json.loads(self.processes) if self.processes else []
        except:
            return []

    @processes_list.setter
    def processes_list(self, value):
        """Set processes as JSON"""
        self.processes = json.dumps(value)

    @property
    def urls_list(self):
        """Parse URLs JSON"""
        try:
            return json.loads(self.urls) if self.urls else []
        except:
            return []

    @urls_list.setter
    def urls_list(self, value):
        """Set URLs as JSON"""
        self.urls = json.dumps(value)
