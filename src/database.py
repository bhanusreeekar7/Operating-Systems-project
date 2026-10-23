"""
Database module for storing logs, metrics, anomalies, predictions, and recovery actions.
Uses SQLite for simple, dependency-free storage.
"""

import sqlite3
import json
import os
from datetime import datetime

class Database:
    """Manages SQLite database connections and schema."""
    
    def __init__(self, db_path: str):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def _get_conn(self):
        """Helper to get a new thread-safe connection with dictionary-like row access."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize database schema, creating necessary tables if they don't exist."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # 1. Logs Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    source TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT,
                    parsed_data TEXT
                )
            ''')
            
            # 2. Metrics Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_percent REAL,
                    memory_percent REAL,
                    disk_percent REAL,
                    network_bytes_sent INTEGER,
                    network_bytes_recv INTEGER,
                    disk_io_read INTEGER,
                    disk_io_write INTEGER
                )
            ''')
            
            # 3. Anomalies Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS anomalies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    anomaly_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    score REAL,
                    features TEXT,
                    description TEXT
                )
            ''')
            
            # 4. Predictions Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    failure_type TEXT NOT NULL,
                    confidence REAL,
                    predicted_time TEXT,
                    features TEXT,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            
            # 5. Recovery Actions Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recovery_actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    failure_type TEXT NOT NULL,
                    action_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT,
                    pre_health_score REAL,
                    post_health_score REAL
                )
            ''')
            
            # 6. Alerts Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    acknowledged BOOLEAN DEFAULT 0
                )
            ''')
            
            conn.commit()

    def insert_log(self, timestamp: str, source: str, level: str, message: str, parsed_data: dict = None):
        """Insert a single log entry."""
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO logs (timestamp, source, level, message, parsed_data) VALUES (?, ?, ?, ?, ?)",
                (timestamp, source, level, message, json.dumps(parsed_data) if parsed_data else "{}")
            )

    def insert_metric(self, timestamp: str, cpu: float, mem: float, disk: float, net_sent: int, net_recv: int, disk_read: int, disk_write: int):
        """Insert system resource metrics."""
        with self._get_conn() as conn:
            conn.execute(
                """INSERT INTO metrics 
                (timestamp, cpu_percent, memory_percent, disk_percent, network_bytes_sent, network_bytes_recv, disk_io_read, disk_io_write) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (timestamp, cpu, mem, disk, net_sent, net_recv, disk_read, disk_write)
            )

    def insert_anomaly(self, timestamp: str, anomaly_type: str, severity: str, score: float, features: dict, description: str):
        """Insert a detected anomaly."""
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO anomalies (timestamp, anomaly_type, severity, score, features, description) VALUES (?, ?, ?, ?, ?, ?)",
                (timestamp, anomaly_type, severity, score, json.dumps(features) if features else "{}", description)
            )

    def insert_prediction(self, timestamp: str, failure_type: str, confidence: float, predicted_time: str, features: dict, status: str = "pending"):
        """Insert a predicted failure."""
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO predictions (timestamp, failure_type, confidence, predicted_time, features, status) VALUES (?, ?, ?, ?, ?, ?)",
                (timestamp, failure_type, confidence, predicted_time, json.dumps(features) if features else "{}", status)
            )

    def insert_recovery_action(self, timestamp: str, failure_type: str, action_name: str, status: str, details: str = "", pre_health: float = None, post_health: float = None):
        """Record an executed recovery action."""
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO recovery_actions (timestamp, failure_type, action_name, status, details, pre_health_score, post_health_score) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (timestamp, failure_type, action_name, status, details, pre_health, post_health)
            )

    def insert_alert(self, timestamp: str, severity: str, message: str, acknowledged: bool = False):
        """Insert a system alert."""
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO alerts (timestamp, severity, message, acknowledged) VALUES (?, ?, ?, ?)",
                (timestamp, severity, message, int(acknowledged))
            )

    def get_recent_logs(self, limit: int = 100):
        """Get most recent logs."""
        with self._get_conn() as conn:
            return [dict(row) for row in conn.execute("SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?", (limit,))]

    def get_recent_metrics(self, limit: int = 100):
        """Get most recent system metrics."""
        with self._get_conn() as conn:
            return [dict(row) for row in conn.execute("SELECT * FROM metrics ORDER BY timestamp DESC LIMIT ?", (limit,))]

    def get_recent_anomalies(self, limit: int = 50):
        """Get most recent anomalies."""
        with self._get_conn() as conn:
            return [dict(row) for row in conn.execute("SELECT * FROM anomalies ORDER BY timestamp DESC LIMIT ?", (limit,))]

    def get_recent_predictions(self, limit: int = 20):
        """Get most recent predictions."""
        with self._get_conn() as conn:
            return [dict(row) for row in conn.execute("SELECT * FROM predictions ORDER BY timestamp DESC LIMIT ?", (limit,))]

    def get_recent_recovery_actions(self, limit: int = 20):
        """Get most recent recovery actions."""
        with self._get_conn() as conn:
            return [dict(row) for row in conn.execute("SELECT * FROM recovery_actions ORDER BY timestamp DESC LIMIT ?", (limit,))]

    def get_dashboard_stats(self):
        """Retrieve aggregated stats for dashboard summary."""
        with self._get_conn() as conn:
            logs_count = conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
            anomalies_count = conn.execute("SELECT COUNT(*) FROM anomalies").fetchone()[0]
            predictions_count = conn.execute("SELECT COUNT(*) FROM predictions WHERE status='pending'").fetchone()[0]
            actions_count = conn.execute("SELECT COUNT(*) FROM recovery_actions WHERE status='success'").fetchone()[0]
            
            # Simple health check based on recent metrics
            latest_metric = conn.execute("SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 1").fetchone()
            
            return {
                "total_logs": logs_count,
                "total_anomalies": anomalies_count,
                "pending_predictions": predictions_count,
                "successful_recoveries": actions_count,
                "latest_cpu": latest_metric["cpu_percent"] if latest_metric else 0.0,
                "latest_mem": latest_metric["memory_percent"] if latest_metric else 0.0
            }

    def get_metrics_timeseries(self, minutes: int = 30):
        """Get metrics data for the last N minutes to plot charts."""
        limit = minutes * 60
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM (SELECT * FROM metrics ORDER BY timestamp DESC LIMIT ?) ORDER BY timestamp ASC", (limit,)).fetchall()
            return [dict(row) for row in rows]

    def get_recent_alerts(self, limit: int = 50):
        """Get most recent alerts."""
        with self._get_conn() as conn:
            return [dict(row) for row in conn.execute("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?", (limit,))]

    def get_unacknowledged_alert_count(self):
        """Get count of unacknowledged alerts."""
        with self._get_conn() as conn:
            return conn.execute("SELECT COUNT(*) FROM alerts WHERE acknowledged = 0").fetchone()[0]

    def acknowledge_alert(self, alert_id: int):
        """Mark an alert as acknowledged."""
        with self._get_conn() as conn:
            conn.execute("UPDATE alerts SET acknowledged = 1 WHERE id = ?", (alert_id,))
            conn.commit()

    def get_timeline_events(self, limit: int = 50):
        """Get a unified timeline of all system events sorted by time."""
        with self._get_conn() as conn:
            query = """
                SELECT timestamp, 'log' AS event_type, level AS severity, message AS detail, source AS extra
                FROM logs
                UNION ALL
                SELECT timestamp, 'anomaly' AS event_type, severity, description AS detail, anomaly_type AS extra
                FROM anomalies
                UNION ALL
                SELECT timestamp, 'prediction' AS event_type,
                    CASE WHEN confidence > 0.8 THEN 'CRITICAL' WHEN confidence > 0.6 THEN 'WARNING' ELSE 'INFO' END AS severity,
                    failure_type AS detail, status AS extra
                FROM predictions
                UNION ALL
                SELECT timestamp, 'recovery' AS event_type,
                    CASE WHEN status = 'success' THEN 'INFO' ELSE 'ERROR' END AS severity,
                    action_name AS detail, failure_type AS extra
                FROM recovery_actions
                ORDER BY timestamp DESC
                LIMIT ?
            """
            return [dict(row) for row in conn.execute(query, (limit,))]
