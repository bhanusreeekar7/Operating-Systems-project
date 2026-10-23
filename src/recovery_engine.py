"""
Autonomous recovery engine.
Maps predicted failure types to recovery actions using configurable policies.
Simulates action execution and records results in the database.
"""

import time
import random
from datetime import datetime

# Import recovery policies from config
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RECOVERY_POLICIES


class RecoveryEngine:
    """Policy-based autonomous recovery engine."""

    # Available recovery actions and their descriptions
    RECOVERY_ACTIONS = {
        'restart_service': 'Restarting failed service...',
        'clear_cache': 'Clearing application cache...',
        'clear_temp_files': 'Removing temporary files to free disk space...',
        'log_rotation': 'Rotating and compressing old log files...',
        'kill_runaway_process': 'Terminating runaway process consuming excessive CPU...',
        'reduce_load': 'Reducing system load by deferring non-critical tasks...',
        'reset_connection': 'Resetting network connections...',
        'switch_interface': 'Switching to backup network interface...',
        'failover': 'Initiating failover to backup system...',
    }

    def __init__(self, database):
        self.db = database
        self.policies = RECOVERY_POLICIES

    def execute_recovery(self, failure_type, confidence):
        """
        Execute recovery actions for a predicted failure.

        Args:
            failure_type: The type of failure predicted.
            confidence: Prediction confidence (0-1).

        Returns:
            dict: Recovery report with status and details.
        """
        now = datetime.now().isoformat()

        # Don't act if confidence is too low
        if confidence < 0.6:
            return {
                'status': 'skipped',
                'message': f'Confidence {confidence:.2f} too low for {failure_type}',
            }

        # Look up the policy for this failure type
        actions = self.policies.get(failure_type, [])
        if not actions:
            return {
                'status': 'no_policy',
                'message': f'No recovery policy for {failure_type}',
            }

        # Simulate a pre-recovery health score
        pre_health = round(random.uniform(25, 55), 1)

        results = []
        for action_name in actions:
            desc = self.RECOVERY_ACTIONS.get(action_name, action_name)
            success = self._simulate_action(action_name)
            status = 'success' if success else 'failed'

            # Post-health improves on success
            post_health = round(pre_health + random.uniform(15, 40), 1) if success else pre_health
            post_health = min(post_health, 100.0)

            # Record in database
            self.db.insert_recovery_action(
                timestamp=now,
                failure_type=failure_type,
                action_name=action_name,
                status=status,
                details=desc,
                pre_health=pre_health,
                post_health=post_health,
            )

            results.append({
                'action': action_name,
                'description': desc,
                'success': success,
                'pre_health': pre_health,
                'post_health': post_health,
            })

            if not success:
                break  # Stop on first failure

        return {
            'status': 'completed',
            'failure_type': failure_type,
            'confidence': confidence,
            'actions': results,
        }

    def _simulate_action(self, action_name):
        """Simulate executing a recovery action (90% success rate)."""
        time.sleep(random.uniform(0.3, 0.8))  # Simulate work
        return random.random() < 0.90

    def _calculate_health_score(self, metrics):
        """
        Simple health score: 100 minus average resource usage.
        Higher is better.
        """
        if not metrics:
            return 100.0
        avg = sum(metrics.values()) / len(metrics)
        return round(max(0.0, 100.0 - avg), 1)
