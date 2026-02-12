import platform
import base64
import io

OS = platform.system()

class ScreenCapture:
    """Cross-platform screenshot capture"""

    def __init__(self):
        try:
            # Use mss library for cross-platform support
            import mss
            self.sct = mss.mss()
            self.use_mss = True
        except ImportError:
            print("Warning: mss not installed, screenshots disabled")
            self.use_mss = False

    def capture(self):
        """
        Capture screenshot
        Returns: base64 encoded PNG image
        """
        if not self.use_mss:
            return None

        try:
            from PIL import Image

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
            print(f"Capture error: {e}")
            return None

    def get_active_window(self):
        """Get title of active window"""
        try:
            if OS == 'Windows':
                import win32gui
                hwnd = win32gui.GetForegroundWindow()
                return win32gui.GetWindowText(hwnd)
            elif OS == 'Darwin':  # macOS
                from AppKit import NSWorkspace
                active_app = NSWorkspace.sharedWorkspace().activeApplication()
                return active_app['NSApplicationName']
            else:  # Linux
                import subprocess
                result = subprocess.run(
                    ['xdotool', 'getactivewindow', 'getwindowname'],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                return result.stdout.strip()
        except:
            return "Unknown"

    def get_active_app(self):
        """Get name of active application"""
        try:
            if OS == 'Windows':
                import win32gui
                import win32process
                import psutil
                hwnd = win32gui.GetForegroundWindow()
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                process = psutil.Process(pid)
                return process.name()
            elif OS == 'Darwin':  # macOS
                from AppKit import NSWorkspace
                active_app = NSWorkspace.sharedWorkspace().activeApplication()
                return active_app['NSApplicationName']
            else:  # Linux
                return self.get_active_window()
        except:
            return "Unknown"
