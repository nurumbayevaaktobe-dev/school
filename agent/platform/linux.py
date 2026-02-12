"""Linux-specific screen capture implementation"""

import subprocess
import base64
import tempfile
import os

try:
    from PIL import Image
    import Xlib
    import Xlib.display
    HAS_LINUX_DEPS = True
except ImportError:
    HAS_LINUX_DEPS = False


class LinuxScreenCapture:
    """Linux-specific screen capture using scrot/imagemagick and X11"""

    def __init__(self):
        if HAS_LINUX_DEPS:
            try:
                self.display = Xlib.display.Display()
            except:
                self.display = None
                print("Warning: Could not connect to X11 display")
        else:
            self.display = None
            print(
                "Warning: Linux dependencies not installed. "
                "Install: pip install pillow python-xlib"
            )

    def capture(self):
        """
        Capture screen using scrot or imagemagick
        Returns: base64 encoded PNG image
        """
        try:
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name

            # Try scrot first (faster)
            try:
                subprocess.run(
                    ['scrot', tmp_path],
                    check=True,
                    capture_output=True,
                    stderr=subprocess.DEVNULL,
                    timeout=5
                )
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Fallback to imagemagick import
                try:
                    subprocess.run(
                        ['import', '-window', 'root', tmp_path],
                        check=True,
                        capture_output=True,
                        timeout=5
                    )
                except (subprocess.CalledProcessError, FileNotFoundError):
                    print("Error: Neither scrot nor imagemagick found")
                    return None

            # Read and encode
            with open(tmp_path, 'rb') as f:
                img_bytes = f.read()

            # Clean up
            os.unlink(tmp_path)

            return base64.b64encode(img_bytes).decode('utf-8')

        except subprocess.TimeoutExpired:
            print("Screenshot timeout on Linux")
            return None
        except Exception as e:
            print(f"Linux capture error: {e}")
            return None

    def get_active_window(self):
        """Get title of active window using X11"""
        if not self.display:
            return self._fallback_get_active_window()

        try:
            root = self.display.screen().root

            # Get active window
            window_id = root.get_full_property(
                self.display.intern_atom('_NET_ACTIVE_WINDOW'),
                Xlib.X.AnyPropertyType
            )

            if not window_id:
                return "Unknown"

            window = self.display.create_resource_object('window', window_id.value[0])

            # Get window name
            window_name = window.get_full_property(
                self.display.intern_atom('_NET_WM_NAME'),
                0
            )

            if window_name and window_name.value:
                return window_name.value.decode('utf-8', errors='ignore')

            # Fallback to WM_NAME
            window_name = window.get_full_property(
                self.display.intern_atom('WM_NAME'),
                0
            )

            if window_name and window_name.value:
                return window_name.value.decode('utf-8', errors='ignore')

            return "Unknown"

        except Exception as e:
            print(f"Error getting active window: {e}")
            return self._fallback_get_active_window()

    def _fallback_get_active_window(self):
        """Fallback method using xdotool"""
        try:
            result = subprocess.run(
                ['xdotool', 'getactivewindow', 'getwindowname'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.stdout.strip() if result.returncode == 0 else "Unknown"
        except:
            return "Unknown"

    def get_active_app(self):
        """Get name of active application"""
        if not self.display:
            return self._fallback_get_active_app()

        try:
            root = self.display.screen().root

            # Get active window
            window_id = root.get_full_property(
                self.display.intern_atom('_NET_ACTIVE_WINDOW'),
                Xlib.X.AnyPropertyType
            )

            if not window_id:
                return "Unknown"

            window = self.display.create_resource_object('window', window_id.value[0])

            # Get window class (application name)
            wm_class = window.get_wm_class()
            if wm_class:
                return wm_class[1] if len(wm_class) > 1 else wm_class[0]

            return "Unknown"

        except Exception as e:
            print(f"Error getting active app: {e}")
            return self._fallback_get_active_app()

    def _fallback_get_active_app(self):
        """Fallback method using xdotool and xprop"""
        try:
            # Get active window ID
            result = subprocess.run(
                ['xdotool', 'getactivewindow'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode != 0:
                return "Unknown"

            window_id = result.stdout.strip()

            # Get window class
            result = subprocess.run(
                ['xprop', '-id', window_id, 'WM_CLASS'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode == 0:
                # Parse WM_CLASS output
                output = result.stdout.strip()
                if '=' in output:
                    class_str = output.split('=')[1].strip()
                    # Extract second value from "instance", "class"
                    parts = class_str.split(',')
                    if len(parts) > 1:
                        return parts[1].strip(' "')

            return "Unknown"

        except:
            return "Unknown"
