"""macOS-specific screen capture implementation"""

import subprocess
import base64
import io
import tempfile
import os

try:
    from PIL import Image
    from AppKit import NSWorkspace
    import Quartz
    HAS_MACOS_DEPS = True
except ImportError:
    HAS_MACOS_DEPS = False


class MacOSScreenCapture:
    """macOS-specific screen capture using screencapture and AppKit"""

    def __init__(self):
        if not HAS_MACOS_DEPS:
            print(
                "Warning: macOS dependencies not fully installed. "
                "Install: pip install pillow pyobjc-framework-Cocoa pyobjc-framework-Quartz"
            )

    def capture(self):
        """
        Capture main display using screencapture command
        Returns: base64 encoded PNG image
        """
        try:
            # Use screencapture command (built into macOS)
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name

            # Capture to file (-x = no sound, -T 0 = no delay)
            subprocess.run(
                ['screencapture', '-x', '-T', '0', tmp_path],
                check=True,
                capture_output=True,
                timeout=5
            )

            # Read and encode
            with open(tmp_path, 'rb') as f:
                img_bytes = f.read()

            # Clean up
            os.unlink(tmp_path)

            return base64.b64encode(img_bytes).decode('utf-8')

        except subprocess.TimeoutExpired:
            print("Screenshot timeout on macOS")
            return None
        except Exception as e:
            print(f"macOS capture error: {e}")
            return None

    def get_active_window(self):
        """Get title of active window"""
        try:
            if HAS_MACOS_DEPS:
                active_app = NSWorkspace.sharedWorkspace().activeApplication()
                return active_app.get('NSApplicationName', 'Unknown')
            else:
                # Fallback using AppleScript
                script = 'tell application "System Events" to get name of first process whose frontmost is true'
                result = subprocess.run(
                    ['osascript', '-e', script],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                return result.stdout.strip() if result.returncode == 0 else "Unknown"
        except Exception as e:
            print(f"Error getting active window: {e}")
            return "Unknown"

    def get_active_app(self):
        """Get name of active application"""
        try:
            if HAS_MACOS_DEPS:
                active_app = NSWorkspace.sharedWorkspace().activeApplication()
                return active_app.get('NSApplicationName', 'Unknown')
            else:
                # Fallback using AppleScript
                script = 'tell application "System Events" to get name of first process whose frontmost is true'
                result = subprocess.run(
                    ['osascript', '-e', script],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                return result.stdout.strip() if result.returncode == 0 else "Unknown"
        except Exception as e:
            print(f"Error getting active app: {e}")
            return "Unknown"
