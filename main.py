"""
PredictiveGuard — Main Entry Point
===================================
Orchestrates all components:
1. Initializes the database
2. Trains ML models (synthetic data for demo)
3. Starts the log generator
4. Runs the analysis loop (detect anomalies, predict failures, trigger recovery)
5. Launches the Flask dashboard

Run: python main.py
Open: http://localhost:5000
"""

import os
import sys
import time
import threading
import numpy as np
from datetime import datetime

# Add project root to path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

import config
from src.database import Database
from src.log_generator import LogGenerator
from src.log_collector import LogCollector
from src.feature_engine import FeatureEngine
from src.anomaly_detector import AnomalyDetector
from src.failure_predictor import FailurePredictor
from src.recovery_engine import RecoveryEngine
from src.alert_manager import AlertManager
from src.app import create_app


# ── Shared state dict (read by Flask, written by the analysis loop) ──────
system_state = {
    'health_score': 100,
    'status': 'starting',
    'anomaly_model_info': {},
    'predictor_model_info': {},
    'manual_recovery': None,
}


def train_models(anomaly_detector, failure_predictor):
    """
    Train ML models on synthetic data so the demo works immediately.
    """
    print("[INIT] Training anomaly detector on synthetic data...")
    # Generate synthetic normal + anomalous feature vectors for the anomaly detector
    predictor_X, predictor_y, feature_names = failure_predictor.generate_training_data(n_samples=1200)
    anomaly_detector.train(predictor_X)

    print("[INIT] Training failure predictor on synthetic data...")
    failure_predictor.auto_train()

    system_state['anomaly_model_info'] = {'status': 'trained', 'features': len(feature_names)}
    system_state['predictor_model_info'] = {'status': 'trained', 'classes': FailurePredictor.FAILURE_TYPES}
    print("[INIT] Models trained successfully.\n")


def analysis_loop(database, log_generator, log_collector, feature_engine,
                  anomaly_detector, failure_predictor, recovery_engine, alert_manager):
    """
    Main loop that runs every LOG_GENERATION_INTERVAL seconds:
    1. Generate synthetic logs & metrics
    2. Store them in the database
    3. Extract features
    4. Detect anomalies
    5. Predict failures
    6. Trigger recovery if needed
    """
    cycle = 0

    while True:
        try:
            cycle += 1
            now = datetime.now().isoformat()

            # ── 1. Generate logs & metrics ───────────────────────────────
            data = log_generator.generate_all()

            # Store logs in database
            for log_key in ['system_log', 'application_log', 'network_log']:
                log = data[log_key]
                database.insert_log(
                    timestamp=log['timestamp'],
                    source=log['source'],
                    level=log['level'],
                    message=log['message'],
                )

            # Store metrics
            m = data['metrics']
            database.insert_metric(
                timestamp=m['timestamp'],
                cpu=m['cpu_percent'],
                mem=m['memory_percent'],
                disk=m['disk_percent'],
                net_sent=m['network_bytes_sent'],
                net_recv=m['network_bytes_recv'],
                disk_read=m['disk_io_read'],
                disk_write=m['disk_io_write'],
            )

            # ── 2. Extract features ──────────────────────────────────────
            metrics_list = database.get_recent_metrics(limit=30)
            logs_list = database.get_recent_logs(limit=100)

            metric_feats = feature_engine.extract_metric_features(metrics_list)
            log_feats = feature_engine.extract_log_features(logs_list)
            combined = feature_engine.combine_features(metric_feats, log_feats)

            if not combined:
                time.sleep(config.LOG_GENERATION_INTERVAL)
                continue

            feature_names = sorted(combined.keys())
            feature_vector = np.array([combined.get(k, 0) for k in feature_names], dtype=np.float64)

            # ── 3. Anomaly detection ─────────────────────────────────────
            try:
                # Pad or trim feature vector to match model's expected input
                score, is_anomaly = anomaly_detector.detect(feature_vector)

                if is_anomaly:
                    severity = anomaly_detector.classify_severity(score, combined)
                    description = anomaly_detector.get_anomaly_description(combined, severity)

                    database.insert_anomaly(
                        timestamp=now,
                        anomaly_type='system',
                        severity=severity,
                        score=float(score),
                        features=combined,
                        description=description,
                    )

                    alert_manager.create_alert(severity, f"Anomaly: {description}")

                    if cycle % 5 == 0:
                        print(f"[ANOMALY] {severity}: {description}")
            except Exception as e:
                if cycle <= 3:
                    print(f"[WARN] Anomaly detection skipped: {e}")

            # ── 4. Failure prediction ────────────────────────────────────
            try:
                prediction = failure_predictor.predict(feature_vector)
                pred_type = prediction['predicted_failure_type']
                confidence = prediction['confidence']

                if pred_type != 'normal' and confidence > config.PREDICTION_THRESHOLD:
                    database.insert_prediction(
                        timestamp=now,
                        failure_type=pred_type,
                        confidence=confidence,
                        predicted_time=now,
                        features=prediction['all_probabilities'],
                        status='pending',
                    )

                    alert_manager.create_alert(
                        'WARNING',
                        f"Predicted {pred_type} (confidence: {confidence:.0%})"
                    )

                    if cycle % 5 == 0:
                        print(f"[PREDICT] {pred_type} ({confidence:.0%})")

                    # ── 5. Autonomous recovery ───────────────────────────
                    report = recovery_engine.execute_recovery(pred_type, confidence)
                    if report['status'] == 'completed':
                        print(f"[RECOVERY] {pred_type}: {[a['action'] for a in report['actions']]}")

            except Exception as e:
                if cycle <= 3:
                    print(f"[WARN] Prediction skipped: {e}")

            # ── 6. Check manual recovery trigger ─────────────────────────
            manual = system_state.get('manual_recovery')
            if manual:
                system_state['manual_recovery'] = None
                report = recovery_engine.execute_recovery(manual, 1.0)
                print(f"[MANUAL RECOVERY] {manual}: {report['status']}")

            # ── 7. Update health score ───────────────────────────────────
            cpu = combined.get('current_cpu', 0)
            mem = combined.get('current_memory', 0)
            disk = combined.get('current_disk', 0)
            health = max(0, 100 - (cpu * 0.4 + mem * 0.35 + disk * 0.25))
            system_state['health_score'] = round(health, 1)
            system_state['status'] = 'running'

        except Exception as e:
            print(f"[ERROR] Analysis loop: {e}")

        time.sleep(config.LOG_GENERATION_INTERVAL)


def main():
    """Start the PredictiveGuard system."""
    print("=" * 60)
    print("  PredictiveGuard — AI Predictive Failure Detection")
    print("  Autonomous Recovery System")
    print("=" * 60)
    print()

    # ── Initialize components ─────────────────────────────────────────────
    print("[INIT] Setting up database...")
    os.makedirs(config.DATA_DIR, exist_ok=True)
    os.makedirs(config.MODEL_DIR, exist_ok=True)
    os.makedirs(config.LOG_DIR, exist_ok=True)
    database = Database(config.DATABASE_PATH)

    print("[INIT] Setting up log generator...")
    log_generator = LogGenerator(config.LOG_DIR)

    print("[INIT] Setting up log collector...")
    log_collector = LogCollector(config.LOG_SOURCES, database)

    print("[INIT] Setting up feature engine...")
    feature_engine = FeatureEngine(database)

    print("[INIT] Setting up anomaly detector...")
    anomaly_model_path = os.path.join(config.MODEL_DIR, 'anomaly_model.joblib')
    anomaly_detector = AnomalyDetector(model_path=anomaly_model_path)

    print("[INIT] Setting up failure predictor...")
    predictor_model_path = os.path.join(config.MODEL_DIR, 'predictor_model.joblib')
    failure_predictor = FailurePredictor(model_path=predictor_model_path)

    print("[INIT] Setting up recovery engine...")
    recovery_engine = RecoveryEngine(database)

    print("[INIT] Setting up alert manager...")
    alert_manager = AlertManager(database, cooldown=config.ALERT_COOLDOWN)

    # ── Train models ──────────────────────────────────────────────────────
    train_models(anomaly_detector, failure_predictor)

    # ── Start analysis loop in background thread ──────────────────────────
    print("[START] Launching analysis loop...")
    analysis_thread = threading.Thread(
        target=analysis_loop,
        args=(database, log_generator, log_collector, feature_engine,
              anomaly_detector, failure_predictor, recovery_engine, alert_manager),
        daemon=True,
    )
    analysis_thread.start()

    # ── Start Flask dashboard ─────────────────────────────────────────────
    print(f"[START] Dashboard at http://localhost:{config.DASHBOARD_PORT}")
    print()
    app = create_app(database, system_state)
    app.run(host='0.0.0.0', port=config.DASHBOARD_PORT, debug=False, use_reloader=False)


if __name__ == '__main__':
    main()
