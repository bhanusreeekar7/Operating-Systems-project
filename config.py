"""
Configuration settings for the Predictive Failure Detection and Autonomous Recovery System.
"""
import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE_PATH = os.path.join(DATA_DIR, "system.db")
MODEL_DIR = os.path.join(BASE_DIR, "models")

# Log sources
LOG_SOURCES = [
    {"name": "system", "path": os.path.join(LOG_DIR, "syslog.log")},
    {"name": "application", "path": os.path.join(LOG_DIR, "app.log")},
    {"name": "database", "path": os.path.join(LOG_DIR, "db.log")}
]

# Machine Learning settings
ANOMALY_CONTAMINATION = 0.1
PREDICTION_THRESHOLD = 0.7

# Feature engineering sliding window sizes (in seconds)
SLIDING_WINDOW_SIZES = [60, 300, 900]

# Recovery policies mapping failure types to ordered actions
RECOVERY_POLICIES = {
    "disk_failure": ["clear_temp_files", "log_rotation"],
    "memory_exhaustion": ["restart_service", "clear_cache"],
    "cpu_overload": ["kill_runaway_process", "reduce_load"],
    "service_crash": ["restart_service", "failover"],
    "network_outage": ["reset_connection", "switch_interface"]
}

# Alert and Dashboard settings
ALERT_COOLDOWN = 300  # seconds
DASHBOARD_PORT = 5000

# Demo / Simulation Mode
DEMO_MODE = True
LOG_GENERATION_INTERVAL = 2  # seconds
