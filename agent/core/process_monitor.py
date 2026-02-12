import psutil

class ProcessMonitor:
    """Monitor running processes"""

    def get_processes(self):
        """Get list of running process names"""
        try:
            processes = []
            for proc in psutil.process_iter(['name']):
                try:
                    processes.append(proc.info['name'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return list(set(processes))  # Remove duplicates
        except Exception as e:
            print(f"Process monitoring error: {e}")
            return []

    def get_browser_urls(self):
        """Get URLs from browser (simplified - would need browser extensions for full implementation)"""
        # This is a placeholder - real implementation would need browser automation
        return []
