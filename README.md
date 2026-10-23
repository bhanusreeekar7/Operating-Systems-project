# PredictiveGuard — AI-Based Predictive Failure Detection & Autonomous Recovery

An intelligent system that ingests multi-source logs, detects anomalies using Machine Learning, predicts failures before they happen, and executes autonomous recovery actions.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Log Generator                         │
│     System Logs · Application Logs · Network Logs       │
│                    System Metrics                        │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│              Log Collector & Parser                      │
│         Regex-based parsing · Normalization              │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│               Feature Engineering                        │
│  Sliding window stats · Log keyword extraction           │
│  Rate of change · Error frequency                        │
└───────────────────────┬─────────────────────────────────┘
                        │
                ┌───────┴───────┐
                ▼               ▼
┌──────────────────┐  ┌──────────────────┐
│ Anomaly Detector │  │ Failure Predictor │
│ Isolation Forest │  │  Random Forest    │
└────────┬─────────┘  └────────┬─────────┘
         │                     │
         └──────────┬──────────┘
                    ▼
┌─────────────────────────────────────────────────────────┐
│              Recovery Engine                             │
│  Policy-based actions · Simulated execution              │
│  Service restart · Cache clear · Log rotation            │
└───────────────────────┬─────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│           Flask Dashboard (port 5000)                    │
│  Real-time charts · Log viewer · Anomaly timeline        │
│  Prediction cards · Recovery action log                  │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the System

```bash
python main.py
```

### 3. Open the Dashboard

Navigate to **http://localhost:5000** in your browser.

The system will:
- Generate synthetic multi-source logs every 2 seconds
- Train ML models on synthetic data at startup
- Detect anomalies using Isolation Forest
- Predict failures using Random Forest
- Execute recovery actions when failures are predicted
- Display everything on a real-time dark-mode dashboard

## Project Structure

```
operating systems project/
├── main.py                    # Entry point — orchestrates everything
├── config.py                  # Central configuration
├── requirements.txt           # Python dependencies
├── README.md                  # This file
│
├── src/
│   ├── __init__.py
│   ├── database.py            # SQLite database layer
│   ├── log_generator.py       # Synthetic multi-source log generator
│   ├── log_collector.py       # Log parsing engine
│   ├── feature_engine.py      # Feature extraction pipeline
│   ├── anomaly_detector.py    # Isolation Forest anomaly detection
│   ├── failure_predictor.py   # Random Forest failure prediction
│   ├── recovery_engine.py     # Autonomous recovery actions
│   ├── alert_manager.py       # Alert creation with throttling
│   └── app.py                 # Flask REST API
│
├── templates/
│   └── index.html             # Dashboard page
│
├── static/
│   ├── style.css              # Dark mode styles
│   └── app.js                 # Frontend JavaScript
│
├── data/                      # SQLite database (auto-created)
├── logs/                      # Generated log files (auto-created)
└── models/                    # Trained ML models (auto-created)
```

## Components

### Log Generator (`log_generator.py`)
Simulates realistic server logs from three sources:
- **System logs**: kernel messages, CRON jobs, OOM killer events
- **Application logs**: HTTP errors, database timeouts, connection pool exhaustion
- **Network logs**: packet loss, firewall blocks, interface status
- **Metrics**: CPU%, Memory%, Disk%, Network I/O

Has a 15% chance per cycle of entering a degradation state that gradually worsens metrics over 10-20 cycles, simulating real-world failure patterns.

### Feature Engine (`feature_engine.py`)
Transforms raw data into ML-ready features:
- Statistical aggregations (mean, std, min, max) over sliding windows
- Rate-of-change calculations
- Log-level frequency counts
- Keyword detection (timeout, OOM, connection refused, disk full)

### Anomaly Detector (`anomaly_detector.py`)
Uses **Isolation Forest** from scikit-learn to detect abnormal system states:
- Trained on synthetic normal + anomalous data
- Outputs anomaly score and severity (LOW → CRITICAL)
- Generates human-readable descriptions

### Failure Predictor (`failure_predictor.py`)
Uses **Random Forest Classifier** to predict specific failure types:
- `disk_failure`, `memory_exhaustion`, `cpu_overload`, `service_crash`, `network_outage`
- Returns confidence scores for each failure type
- Identifies top contributing features

### Recovery Engine (`recovery_engine.py`)
Executes autonomous recovery based on configurable policies:
- Maps each failure type to ordered recovery actions
- Actions: restart service, clear cache, log rotation, kill process, etc.
- Only acts when prediction confidence > 60%
- Records pre/post health scores

### Dashboard
Minimal dark-mode web interface built with Flask + Chart.js:
- Real-time system metrics charts (CPU, Memory, Disk, Network)
- Live log viewer with level-based color coding
- Anomaly timeline with severity badges
- Failure predictions with confidence bars
- Recovery action history

## Configuration

All settings are in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `DASHBOARD_PORT` | 5000 | Web server port |
| `LOG_GENERATION_INTERVAL` | 2 | Seconds between log cycles |
| `ANOMALY_CONTAMINATION` | 0.1 | Isolation Forest contamination |
| `PREDICTION_THRESHOLD` | 0.7 | Minimum confidence to act |
| `ALERT_COOLDOWN` | 300 | Seconds between duplicate alerts |
| `DEMO_MODE` | True | Use synthetic log generation |

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| ML | scikit-learn (Isolation Forest, Random Forest) |
| Database | SQLite |
| Web | Flask |
| Frontend | HTML + CSS + Vanilla JS |
| Charts | Chart.js |
