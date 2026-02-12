"""Full-screen overlay for notifications and screen lock"""

import tkinter as tk
from tkinter import font as tkfont
import threading
import platform
from datetime import datetime, timedelta

class NotificationOverlay:
    """Display temporary notification overlay"""

    def __init__(self):
        self.window = None
        self.auto_hide_timer = None

    def show(self, message, message_type='normal', duration=10):
        """
        Show notification toast
        - message: Text to display
        - message_type: 'normal', 'warning', 'urgent', 'success', 'info'
        - duration: Seconds to display (0 = permanent)
        """
        # Run in separate thread to avoid blocking
        thread = threading.Thread(target=self._show_window, args=(message, message_type, duration), daemon=True)
        thread.start()

    def _show_window(self, message, message_type, duration):
        """Create and show notification window"""
        try:
            # Create window
            self.window = tk.Tk()
            self.window.title("ClassGuard Notification")

            # Get screen dimensions
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()

            # Notification size
            width = 400
            height = 120

            # Position at top-right
            x = screen_width - width - 20
            y = 20

            self.window.geometry(f"{width}x{height}+{x}+{y}")

            # Window properties
            self.window.attributes('-topmost', True)
            self.window.overrideredirect(True)  # No window decorations

            # Color scheme based on type
            colors = {
                'normal': {'bg': '#3B82F6', 'fg': 'white'},     # Blue
                'success': {'bg': '#10B981', 'fg': 'white'},    # Green
                'warning': {'bg': '#F59E0B', 'fg': 'white'},    # Orange
                'urgent': {'bg': '#EF4444', 'fg': 'white'},     # Red
                'info': {'bg': '#6366F1', 'fg': 'white'}        # Indigo
            }
            color = colors.get(message_type, colors['normal'])

            # Main frame
            frame = tk.Frame(self.window, bg=color['bg'], padx=20, pady=15)
            frame.pack(fill=tk.BOTH, expand=True)

            # Title
            title_font = tkfont.Font(family='Arial', size=12, weight='bold')
            title = tk.Label(
                frame,
                text=f"📢 ClassGuard - {message_type.upper()}",
                font=title_font,
                bg=color['bg'],
                fg=color['fg']
            )
            title.pack(anchor='w')

            # Message
            msg_font = tkfont.Font(family='Arial', size=10)
            msg_label = tk.Label(
                frame,
                text=message,
                font=msg_font,
                bg=color['bg'],
                fg=color['fg'],
                wraplength=360,
                justify='left'
            )
            msg_label.pack(anchor='w', pady=(5, 0))

            # Close button
            close_btn = tk.Button(
                frame,
                text="✕",
                command=self.hide,
                bg=color['bg'],
                fg=color['fg'],
                relief=tk.FLAT,
                cursor='hand2',
                font=tkfont.Font(size=14, weight='bold')
            )
            close_btn.place(relx=1.0, rely=0.0, anchor='ne')

            # Auto-hide after duration
            if duration > 0:
                self.auto_hide_timer = self.window.after(duration * 1000, self.hide)

            # Start event loop
            self.window.mainloop()

        except Exception as e:
            print(f"Notification error: {e}")

    def hide(self):
        """Hide notification"""
        if self.window:
            try:
                if self.auto_hide_timer:
                    self.window.after_cancel(self.auto_hide_timer)
                self.window.destroy()
                self.window = None
            except:
                pass


class LockOverlay:
    """Full-screen lock overlay that blocks all user input"""

    def __init__(self):
        self.window = None
        self.unlock_callback = None
        self.remaining_seconds = 0
        self.countdown_label = None
        self.timer_id = None
        self.is_active = False

    def show(self, message, duration, unlock_callback):
        """
        Show full-screen lock overlay
        - message: Text to display to student
        - duration: Seconds until auto-unlock (0 or 'manual' = no auto-unlock)
        - unlock_callback: Function to call when unlocking
        """
        self.unlock_callback = unlock_callback
        self.remaining_seconds = duration if isinstance(duration, int) else 0

        # Run in separate thread
        thread = threading.Thread(target=self._show_window, args=(message,), daemon=True)
        thread.start()

    def _show_window(self, message):
        """Create and show full-screen lock window"""
        try:
            self.is_active = True

            # Create window
            self.window = tk.Tk()
            self.window.title("Screen Locked")

            # Get screen dimensions
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()

            # Full screen
            self.window.geometry(f"{screen_width}x{screen_height}+0+0")

            # Window properties - CRITICAL for locking
            self.window.attributes('-topmost', True)        # Always on top
            self.window.attributes('-fullscreen', True)     # Full screen
            self.window.overrideredirect(True)              # No window controls

            # Disable close events
            self.window.protocol("WM_DELETE_WINDOW", lambda: None)

            # Grab focus and prevent other windows
            self.window.focus_force()
            self.window.grab_set()

            # Background
            self.window.configure(bg='#1F2937')

            # Main container
            container = tk.Frame(self.window, bg='#1F2937')
            container.place(relx=0.5, rely=0.5, anchor='center')

            # Lock icon (using emoji)
            icon_font = tkfont.Font(family='Arial', size=80)
            icon = tk.Label(
                container,
                text="🔒",
                font=icon_font,
                bg='#1F2937',
                fg='white'
            )
            icon.pack(pady=(0, 20))

            # Title
            title_font = tkfont.Font(family='Arial', size=32, weight='bold')
            title = tk.Label(
                container,
                text="SCREEN LOCKED",
                font=title_font,
                bg='#1F2937',
                fg='#EF4444'  # Red
            )
            title.pack(pady=(0, 10))

            # Message from teacher
            msg_font = tkfont.Font(family='Arial', size=18)
            msg_label = tk.Label(
                container,
                text=message,
                font=msg_font,
                bg='#1F2937',
                fg='white',
                wraplength=800,
                justify='center'
            )
            msg_label.pack(pady=(0, 30))

            # Countdown timer
            if self.remaining_seconds > 0:
                countdown_font = tkfont.Font(family='Arial', size=24, weight='bold')
                self.countdown_label = tk.Label(
                    container,
                    text=self._format_time(self.remaining_seconds),
                    font=countdown_font,
                    bg='#1F2937',
                    fg='#10B981'  # Green
                )
                self.countdown_label.pack(pady=(10, 0))

                # Start countdown
                self._update_countdown()
            else:
                # Manual unlock only
                manual_font = tkfont.Font(family='Arial', size=16)
                manual_label = tk.Label(
                    container,
                    text="Waiting for teacher to unlock...",
                    font=manual_font,
                    bg='#1F2937',
                    fg='#9CA3AF'  # Gray
                )
                manual_label.pack(pady=(10, 0))

            # Footer
            footer_font = tkfont.Font(family='Arial', size=12)
            footer = tk.Label(
                container,
                text="🎓 AI ClassGuard Pro",
                font=footer_font,
                bg='#1F2937',
                fg='#6B7280'
            )
            footer.pack(side='bottom', pady=(40, 0))

            # Prevent keyboard shortcuts
            self._disable_shortcuts()

            # Start event loop
            self.window.mainloop()

        except Exception as e:
            print(f"Lock overlay error: {e}")
            self.is_active = False

    def _update_countdown(self):
        """Update countdown timer"""
        if not self.window or not self.countdown_label:
            return

        if self.remaining_seconds > 0:
            # Update label
            self.countdown_label.config(text=self._format_time(self.remaining_seconds))
            self.remaining_seconds -= 1

            # Schedule next update
            self.timer_id = self.window.after(1000, self._update_countdown)
        else:
            # Auto-unlock
            self.hide()

    def _format_time(self, seconds):
        """Format seconds as MM:SS"""
        mins = seconds // 60
        secs = seconds % 60
        return f"Unlocking in: {mins:02d}:{secs:02d}"

    def _disable_shortcuts(self):
        """Disable common keyboard shortcuts"""
        # Bind all keys to do nothing
        shortcuts = [
            '<Alt-F4>',           # Windows close
            '<Command-q>',        # macOS quit
            '<Command-w>',        # macOS close window
            '<Control-Alt-Delete>',  # Windows task manager
            '<Escape>',           # Escape key
            '<F11>',              # Full screen toggle
            '<Alt-Tab>',          # Switch windows
            '<Command-Tab>',      # macOS switch apps
        ]

        for shortcut in shortcuts:
            try:
                self.window.bind(shortcut, lambda e: "break")
            except:
                pass

        # Catch all other key presses
        self.window.bind('<Key>', lambda e: "break")

    def hide(self):
        """Hide lock overlay and call unlock callback"""
        if self.window and self.is_active:
            try:
                # Cancel timer if running
                if self.timer_id:
                    self.window.after_cancel(self.timer_id)

                # Release grab
                self.window.grab_release()

                # Destroy window
                self.window.destroy()
                self.window = None
                self.is_active = False

                # Call unlock callback
                if self.unlock_callback:
                    self.unlock_callback()

            except Exception as e:
                print(f"Error hiding lock overlay: {e}")
                self.is_active = False
