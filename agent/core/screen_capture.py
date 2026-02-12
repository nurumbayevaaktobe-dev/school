"""Cross-platform screen capture with platform-specific implementations"""

import platform
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OS = platform.system()

# Import platform-specific implementation
try:
    if OS == 'Windows':
        from platform.windows import WindowsScreenCapture as PlatformCapture
    elif OS == 'Darwin':  # macOS
        from platform.macos import MacOSScreenCapture as PlatformCapture
    else:  # Linux
        from platform.linux import LinuxScreenCapture as PlatformCapture
    HAS_PLATFORM_CAPTURE = True
except ImportError as e:
    print(f"Warning: Platform-specific capture not available: {e}")
    HAS_PLATFORM_CAPTURE = False
    PlatformCapture = None


class ScreenCapture:
    """Cross-platform screenshot capture with platform-specific implementations"""

    def __init__(self):
        """Initialize platform-specific screen capture"""
        if HAS_PLATFORM_CAPTURE:
            try:
                self.platform_capture = PlatformCapture()
                self.use_platform = True
                print(f"✅ Using {OS}-specific screen capture")
            except Exception as e:
                print(f"⚠️ Platform capture initialization failed: {e}")
                self.use_platform = False
                self.platform_capture = None
        else:
            print(f"⚠️ No platform-specific capture available for {OS}")
            self.use_platform = False
            self.platform_capture = None
            self._init_fallback()

    def _init_fallback(self):
        """Initialize fallback generic capture using mss"""
        try:
            import mss
            self.sct = mss.mss()
            self.use_mss = True
            print("✅ Using fallback mss screen capture")
        except ImportError:
            print("❌ No screen capture available (mss not installed)")
            self.use_mss = False
            self.sct = None

    def capture(self):
        """
        Capture screenshot
        Returns: base64 encoded PNG image
        """
        # Try platform-specific first
        if self.use_platform and self.platform_capture:
            try:
                return self.platform_capture.capture()
            except Exception as e:
                print(f"Platform capture error: {e}")
                # Fall through to fallback

        # Fallback to mss
        if hasattr(self, 'use_mss') and self.use_mss:
            return self._fallback_capture()

        return None

    def _fallback_capture(self):
        """Fallback capture using mss"""
        try:
            from PIL import Image
            import base64
            import io

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
            print(f"Fallback capture error: {e}")
            return None

    def get_active_window(self):
        """Get title of active window"""
        if self.use_platform and self.platform_capture:
            try:
                return self.platform_capture.get_active_window()
            except Exception as e:
                print(f"Error getting active window: {e}")

        return "Unknown"

    def get_active_app(self):
        """Get name of active application"""
        if self.use_platform and self.platform_capture:
            try:
                return self.platform_capture.get_active_app()
            except Exception as e:
                print(f"Error getting active app: {e}")

        return "Unknown"
