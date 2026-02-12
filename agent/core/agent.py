import socketio
import time
import platform
import threading
from datetime import datetime
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.screen_capture import ScreenCapture
from core.process_monitor import ProcessMonitor
from core.network_handler import NetworkHandler
from utils.compression import compress_image
from utils.logger import get_logger
from config import AgentConfig

logger = get_logger('agent')

class StudentAgent:
    """Main student agent - cross-platform compatible"""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.running = False

        # Initialize components
        self.screen_capture = ScreenCapture()
        self.process_monitor = ProcessMonitor()
        self.network = NetworkHandler(config.server_url, self._on_connect, self._on_disconnect)

        # State
        self.student_id = None
        self.is_locked = False

        logger.info(f"Agent initialized on {platform.system()}")

    def start(self):
        """Start the agent"""
        logger.info("Starting agent...")
        self.running = True

        # Connect to server
        self.network.connect()

        # Start monitoring threads
        screenshot_thread = threading.Thread(target=self._screenshot_loop, daemon=True)
        process_thread = threading.Thread(target=self._process_loop, daemon=True)

        screenshot_thread.start()
        process_thread.start()

        # Register event handlers
        self._register_handlers()

        logger.info("Agent started successfully")

        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the agent"""
        logger.info("Stopping agent...")
        self.running = False
        self.network.disconnect()
        logger.info("Agent stopped")

    def _on_connect(self):
        """Callback when connected to server"""
        logger.info("Connected to server")

        # Register with server
        self.network.emit('register_student', {
            'name': self.config.student_name,
            'computer_id': self.config.computer_id,
            'platform': platform.system(),
            'hostname': platform.node()
        })

    def _on_disconnect(self):
        """Callback when disconnected from server"""
        logger.warning("Disconnected from server")

    def _screenshot_loop(self):
        """Continuous screenshot capture and transmission"""
        while self.running:
            try:
                if not self.is_locked:
                    # Capture screenshot
                    screenshot_data = self.screen_capture.capture()

                    if screenshot_data:
                        # Compress
                        compressed, img_hash, size_kb = compress_image(
                            screenshot_data,
                            quality=self.config.screenshot_quality
                        )

                        # Get active window info
                        active_window = self.screen_capture.get_active_window()
                        active_app = self.screen_capture.get_active_app()

                        # Send to server
                        self.network.emit('screen_update', {
                            'screenshot': compressed,
                            'hash': img_hash,
                            'size_kb': size_kb,
                            'active_window': active_window,
                            'active_app': active_app,
                            'timestamp': datetime.now().isoformat()
                        })

                        logger.debug(f"Screenshot sent ({size_kb:.1f} KB)")

                time.sleep(self.config.screenshot_interval)

            except Exception as e:
                logger.error(f"Screenshot loop error: {e}")
                time.sleep(5)  # Wait before retry

    def _process_loop(self):
        """Continuous process monitoring"""
        while self.running:
            try:
                # Get running processes
                processes = self.process_monitor.get_processes()

                # Get browser URLs (if applicable)
                urls = self.process_monitor.get_browser_urls()

                # Send to server
                self.network.emit('process_update', {
                    'processes': processes,
                    'urls': urls,
                    'timestamp': datetime.now().isoformat()
                })

                logger.debug(f"Process update sent ({len(processes)} processes)")

                time.sleep(5)  # Update every 5 seconds

            except Exception as e:
                logger.error(f"Process loop error: {e}")
                time.sleep(10)

    def _register_handlers(self):
        """Register event handlers for server messages"""

        @self.network.on('receive_message')
        def handle_message(data):
            """Show message from teacher"""
            logger.info(f"Message received: {data.get('message')}")
            print(f"\n📨 MESSAGE FROM TEACHER: {data.get('message')}\n")

        @self.network.on('screen_lock')
        def handle_lock(data):
            """Lock the screen"""
            logger.warning("Screen lock received")
            self.is_locked = True
            print(f"\n🔒 SCREEN LOCKED: {data.get('message')}\n")

        @self.network.on('screen_unlock')
        def handle_unlock(data):
            """Unlock the screen"""
            logger.info("Screen unlock received")
            self.is_locked = False
            print("\n🔓 SCREEN UNLOCKED\n")

        @self.network.on('show_poll')
        def handle_poll(data):
            """Show poll to student"""
            logger.info(f"Poll received: {data.get('question')}")
            print(f"\n📊 POLL: {data.get('question')}")
            for i, option in enumerate(data.get('options', []), 1):
                print(f"  {i}. {option}")
            print()

        @self.network.on('shutdown')
        def handle_shutdown(data):
            """Emergency shutdown"""
            logger.warning("Shutdown command received")
            self.stop()

def main():
    """Main entry point"""
    from config import AgentConfig

    # Load configuration
    config = AgentConfig()

    # Create and start agent
    agent = StudentAgent(config)
    agent.start()

if __name__ == '__main__':
    main()
