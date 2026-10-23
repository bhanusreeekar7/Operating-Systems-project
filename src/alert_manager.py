"""
Simple alert manager.
Creates alerts, stores them in the database, and throttles duplicate messages.
"""

import time
from datetime import datetime


class AlertManager:
    """Handles alert creation with cooldown-based throttling."""

    def __init__(self, database, cooldown=300):
        """
        Args:
            database: Database instance.
            cooldown: Minimum seconds between identical alert messages.
        """
        self.db = database
        self.cooldown = cooldown
        self.last_alert_times = {}  # message -> timestamp

    def create_alert(self, severity, message):
        """
        Create an alert if the same message hasn't been sent recently.

        Returns:
            dict with alert info, or None if throttled.
        """
        if self._should_throttle(message):
            return None

        now = datetime.now().isoformat()
        self.last_alert_times[message] = time.time()

        # Store in database using the Database class method
        self.db.insert_alert(
            timestamp=now,
            severity=severity,
            message=message,
            acknowledged=False,
        )

        return {
            'severity': severity,
            'message': message,
            'timestamp': now,
        }

    def _should_throttle(self, message):
        """Check if the same message was sent within the cooldown period."""
        last = self.last_alert_times.get(message, 0)
        return (time.time() - last) < self.cooldown
