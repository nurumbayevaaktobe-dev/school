"""Windows-specific screen capture implementation"""

import base64
import io

try:
    import mss
    from PIL import Image
    import win32gui
    import win32process
    import psutil
    HAS_WINDOWS_DEPS = True
except ImportError:
    HAS_WINDOWS_DEPS = False


class WindowsScreenCapture:
    """Windows-specific screen capture using mss and pywin32"""

    def __init__(self):
        if not HAS_WINDOWS_DEPS:
            raise ImportError(
                "Windows dependencies not installed. "
                "Install: pip install mss pillow pywin32 psutil"
            )
        self.sct = mss.mss()

    def capture(self):
        """
        Capture primary monitor screenshot
        Returns: base64 encoded PNG image
        """
        try:
            # Capture primary monitor
            monitor = self.sct.monitors[1]
            screenshot = self.sct.grab(monitor)

            # Convert to PIL Image
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)

            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_bytes = buffer.getvalue()

            return base64.b64encode(img_bytes).decode('utf-8')

        except Exception as e:
            print(f"Windows capture error: {e}")
            return None

    def get_active_window(self):
        """Get title of active window"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            return window_title if window_title else "Unknown"
        except Exception as e:
            print(f"Error getting active window: {e}")
            return "Unknown"

    def get_active_app(self):
        """Get name of active application"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            return process.name()
        except Exception as e:
            print(f"Error getting active app: {e}")
            return "Unknown"
