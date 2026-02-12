"""Placeholder for UI overlays (notifications, lock screen)"""

class NotificationOverlay:
    """Display notifications to student"""

    def show(self, message, message_type='normal', duration=10):
        """Show notification"""
        print(f"\n{'='*60}")
        print(f"NOTIFICATION ({message_type.upper()})")
        print(f"{message}")
        print(f"{'='*60}\n")

class LockOverlay:
    """Display lock screen overlay"""

    def show(self, message, duration, unlock_callback):
        """Show lock screen"""
        print(f"\n{'#'*60}")
        print(f"SCREEN LOCKED")
        print(f"{message}")
        print(f"Duration: {duration} seconds")
        print(f"{'#'*60}\n")

    def hide(self):
        """Hide lock screen"""
        print("\nScreen unlocked\n")
