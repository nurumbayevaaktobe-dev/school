import os
from dotenv import load_dotenv

load_dotenv()

class AgentConfig:
    """Agent configuration"""

    # Server connection
    server_url = os.environ.get('SERVER_URL', 'http://localhost:5000')

    # Student info
    student_name = os.environ.get('STUDENT_NAME', 'Student')
    computer_id = os.environ.get('COMPUTER_ID', f"{os.getenv('USER', 'unknown')}_{os.getenv('HOSTNAME', 'computer')}")

    # Screenshot settings
    screenshot_interval = int(os.environ.get('SCREENSHOT_INTERVAL', '3'))  # seconds
    screenshot_quality = int(os.environ.get('SCREENSHOT_QUALITY', '60'))  # 1-100

    # Monitoring
    process_update_interval = 5  # seconds

    def __repr__(self):
        return f"AgentConfig(server={self.server_url}, student={self.student_name})"
