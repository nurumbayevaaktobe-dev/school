import socketio
import time

class NetworkHandler:
    """Handle WebSocket connection with auto-reconnect"""

    def __init__(self, server_url, on_connect_callback, on_disconnect_callback):
        self.server_url = server_url
        self.on_connect_callback = on_connect_callback
        self.on_disconnect_callback = on_disconnect_callback

        # Create SocketIO client
        self.sio = socketio.Client(reconnection=True, reconnection_attempts=0, reconnection_delay=2)

        # Register built-in event handlers
        @self.sio.event
        def connect():
            if self.on_connect_callback:
                self.on_connect_callback()

        @self.sio.event
        def disconnect():
            if self.on_disconnect_callback:
                self.on_disconnect_callback()

    def connect(self):
        """Connect to server with retry logic"""
        max_retries = 5
        retry_count = 0

        while retry_count < max_retries:
            try:
                self.sio.connect(self.server_url, transports=['websocket', 'polling'])
                return True
            except Exception as e:
                retry_count += 1
                print(f"Connection failed (attempt {retry_count}/{max_retries}): {e}")
                if retry_count < max_retries:
                    time.sleep(2 ** retry_count)  # Exponential backoff

        return False

    def disconnect(self):
        """Disconnect from server"""
        try:
            self.sio.disconnect()
        except:
            pass

    def emit(self, event, data):
        """Emit event to server"""
        try:
            self.sio.emit(event, data)
        except Exception as e:
            print(f"Emit error: {e}")

    def on(self, event):
        """Decorator to register event handler"""
        return self.sio.on(event)
