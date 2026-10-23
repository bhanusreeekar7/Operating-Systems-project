"""
Comprehensive Test Suite for PredictiveGuard
==============================================
Validates all system components, models, database layers, and API routes.
"""

import os
import tempfile
import pytest
import numpy as np
from src.database import Database
from src.log_generator import LogGenerator
from src.log_collector import LogCollector
from src.feature_engine import FeatureEngine
from src.anomaly_detector import AnomalyDetector
from src.failure_predictor import FailurePredictor
from src.recovery_engine import RecoveryEngine
from src.alert_manager import AlertManager
from src.app import create_app


@pytest.fixture
def temp_db(tmp_path):
    db_file = str(tmp_path / "test_predictive_guard.db")
    db = Database(db_file)
    return db


@pytest.fixture
def temp_log_dir(tmp_path):
    log_dir = str(tmp_path / "logs")
    os.makedirs(log_dir, exist_ok=True)
    return log_dir


# ── 1. Database Layer Tests ─────────────────────────────────────────────────

def test_db_initialization(temp_db):
    stats = temp_db.get_dashboard_stats()
    assert stats['total_logs'] == 0
    assert stats['total_anomalies'] == 0
    assert stats['pending_predictions'] == 0
    assert stats['successful_recoveries'] == 0


def test_db_insert_and_get_logs(temp_db):
    temp_db.insert_log("2026-09-19T20:00:00", "system", "INFO", "System initialized")
    temp_db.insert_log("2026-09-19T20:00:01", "application", "ERROR", "Out of memory error")
    logs = temp_db.get_recent_logs(limit=10)
    assert len(logs) == 2
    assert logs[0]['level'] == "ERROR"


def test_db_insert_and_get_metrics(temp_db):
    temp_db.insert_metric("2026-09-19T20:00:00", 45.2, 60.1, 75.0, 1024, 2048, 50, 100)
    metrics = temp_db.get_recent_metrics(limit=10)
    assert len(metrics) == 1
    assert metrics[0]['cpu_percent'] == 45.2


def test_db_insert_and_get_anomalies(temp_db):
    temp_db.insert_anomaly("2026-09-19T20:00:00", "system", "CRITICAL", -0.75, {"cpu": 98.0}, "High CPU load")
    anomalies = temp_db.get_recent_anomalies(limit=5)
    assert len(anomalies) == 1
    assert anomalies[0]['severity'] == "CRITICAL"


def test_db_insert_and_get_predictions(temp_db):
    temp_db.insert_prediction("2026-09-19T20:00:00", "disk_failure", 0.88, "2026-09-19T20:10:00", {"disk_io": 95}, "pending")
    preds = temp_db.get_recent_predictions(limit=5)
    assert len(preds) == 1
    assert preds[0]['failure_type'] == "disk_failure"
    assert preds[0]['confidence'] == 0.88


def test_db_insert_and_get_recovery_actions(temp_db):
    temp_db.insert_recovery_action("2026-09-19T20:00:00", "service_crash", "service_restart", "success", "Service daemon restarted", 55.0, 89.0)
    rec = temp_db.get_recent_recovery_actions(limit=5)
    assert len(rec) == 1
    assert rec[0]['action_name'] == "service_restart"
    assert rec[0]['status'] == "success"


def test_db_insert_and_get_alerts(temp_db):
    temp_db.insert_alert("2026-09-19T20:00:00", "WARNING", "High memory usage detected")
    alerts = temp_db.get_recent_alerts()
    assert len(alerts) == 1
    assert temp_db.get_unacknowledged_alert_count() == 1
    temp_db.acknowledge_alert(alerts[0]['id'])
    assert temp_db.get_unacknowledged_alert_count() == 0


def test_db_timeline_events(temp_db):
    temp_db.insert_log("2026-09-19T20:00:00", "system", "INFO", "System initialized")
    temp_db.insert_anomaly("2026-09-19T20:01:00", "system", "HIGH", -0.5, {}, "Spike detected")
    temp_db.insert_prediction("2026-09-19T20:02:00", "cpu_overload", 0.85, "2026-09-19T20:05:00", {}, "pending")
    temp_db.insert_recovery_action("2026-09-19T20:03:00", "cpu_overload", "kill_runaway_process", "success", "Terminated process", 40.0, 85.0)
    events = temp_db.get_timeline_events(limit=10)
    assert len(events) == 4
    types = {e['event_type'] for e in events}
    assert {'log', 'anomaly', 'prediction', 'recovery'}.issubset(types)


def test_db_metrics_timeseries(temp_db):
    temp_db.insert_metric("2026-09-19T20:00:00", 30.0, 40.0, 50.0, 100, 200, 5, 10)
    temp_db.insert_metric("2026-09-19T20:01:00", 35.0, 42.0, 50.0, 150, 250, 6, 12)
    ts = temp_db.get_metrics_timeseries(minutes=10)
    assert len(ts) == 2
    assert ts[0]['cpu_percent'] == 30.0


# ── 2. Log Generator Tests ──────────────────────────────────────────────────

def test_log_generator_system_log(temp_log_dir):
    gen = LogGenerator(temp_log_dir)
    sys_log = gen.generate_system_log()
    assert sys_log['source'] == 'system'
    assert 'timestamp' in sys_log
    assert 'message' in sys_log
    assert sys_log['level'] in ['INFO', 'WARNING', 'ERROR', 'CRITICAL']


def test_log_generator_application_log(temp_log_dir):
    gen = LogGenerator(temp_log_dir)
    app_log = gen.generate_application_log()
    assert app_log['source'] == 'application'
    assert 'message' in app_log
    assert app_log['level'] in ['INFO', 'WARNING', 'ERROR', 'CRITICAL']


def test_log_generator_network_log(temp_log_dir):
    gen = LogGenerator(temp_log_dir)
    net_log = gen.generate_network_log()
    assert net_log['source'] == 'network'
    assert 'message' in net_log
    assert net_log['level'] in ['INFO', 'WARNING', 'ERROR', 'CRITICAL']


def test_log_generator_metrics(temp_log_dir):
    gen = LogGenerator(temp_log_dir)
    m = gen.generate_metrics()
    assert 0 <= m['cpu_percent'] <= 100
    assert 0 <= m['memory_percent'] <= 100
    assert 0 <= m['disk_percent'] <= 100
    assert m['network_bytes_sent'] >= 0
    assert m['network_bytes_recv'] >= 0


def test_log_generator_generate_all(temp_log_dir):
    gen = LogGenerator(temp_log_dir)
    data = gen.generate_all()
    assert 'system_log' in data
    assert 'application_log' in data
    assert 'network_log' in data
    assert 'metrics' in data


def test_log_generator_anomaly_injection(temp_log_dir):
    gen = LogGenerator(temp_log_dir)
    gen.anomaly_state = 'active'
    gen.anomaly_duration = 5
    gen.anomaly_type = 'cpu_spike'
    m = gen.generate_metrics()
    assert m['cpu_percent'] >= 35.0
    assert 0 <= m['cpu_percent'] <= 100.0


def test_anomaly_detector_not_trained_error():
    ad = AnomalyDetector(model_path="non_existent_file.joblib")
    with pytest.raises(ValueError):
        ad.detect(np.array([1.0, 2.0]))


def test_failure_predictor_empty_model_predict():
    fp = FailurePredictor(model_path="non_existent_file.joblib")
    res = fp.predict(np.array([1.0, 2.0]))
    assert res['predicted_failure_type'] == 'normal'
    assert res['confidence'] == 0.0


def test_feature_engine_roc_calculation(temp_db):
    fe = FeatureEngine(temp_db)
    metrics_sample = [
        {'cpu_percent': 20.0, 'memory_percent': 30.0, 'disk_percent': 40.0, 'network_bytes_recv': 1000},
        {'cpu_percent': 80.0, 'memory_percent': 70.0, 'disk_percent': 40.0, 'network_bytes_recv': 5000},
    ]
    feats = fe.extract_metric_features(metrics_sample)
    assert feats['cpu_percent_roc'] == 60.0
    assert feats['memory_percent_roc'] == 40.0



# ── 3. Log Collector & Parser Tests ─────────────────────────────────────────

def test_log_collector_parse_syslog(temp_db):
    collector = LogCollector({}, temp_db)
    line = "Sep 19 20:00:00 server-01 ERROR: OOM killer invoked for process X"
    parsed = collector.parse_syslog(line)
    assert parsed is not None
    assert parsed['level'] == 'ERROR'
    assert 'OOM killer' in parsed['message']


def test_log_collector_parse_app_log(temp_db):
    collector = LogCollector({}, temp_db)
    line = "[2026-09-19T20:00:00] [ERROR] HTTP 500 Internal Server Error on /api/data"
    parsed = collector.parse_app_log(line)
    assert parsed is not None
    assert parsed['level'] == 'ERROR'
    assert parsed['endpoint'] == '/api/data'


def test_log_collector_parse_network_log(temp_db):
    collector = LogCollector({}, temp_db)
    line = "[2026-09-19T20:00:00] [WARNING] Network: Packet loss detected: 15% on eth0"
    parsed = collector.parse_network_log(line)
    assert parsed is not None
    assert parsed['level'] == 'WARNING'
    assert parsed['interface'] == 'eth0'


def test_log_collector_collect_and_parse(temp_db):
    collector = LogCollector({}, temp_db)
    collector.collect_and_parse("application", "[2026-09-19T20:00:00] [INFO] Cache hit rate: 94%")
    logs = temp_db.get_recent_logs(limit=5)
    assert len(logs) == 1
    assert logs[0]['level'] == 'INFO'


# ── 4. Feature Engine Tests ─────────────────────────────────────────────────

def test_feature_engine_metric_features(temp_db):
    fe = FeatureEngine(temp_db)
    metrics_sample = [
        {'cpu_percent': 30.0, 'memory_percent': 50.0, 'disk_percent': 40.0, 'network_bytes_recv': 2000},
        {'cpu_percent': 40.0, 'memory_percent': 55.0, 'disk_percent': 40.5, 'network_bytes_recv': 2500},
        {'cpu_percent': 50.0, 'memory_percent': 60.0, 'disk_percent': 41.0, 'network_bytes_recv': 3000},
    ]
    feats = fe.extract_metric_features(metrics_sample)
    assert 'cpu_percent_mean' in feats
    assert 'memory_percent_mean' in feats
    assert 'disk_percent_mean' in feats
    assert feats['cpu_percent_mean'] == 40.0
    assert feats['current_cpu'] == 50.0


def test_feature_engine_empty_metrics(temp_db):
    fe = FeatureEngine(temp_db)
    feats = fe.extract_metric_features([])
    assert feats == {}


def test_feature_engine_log_features(temp_db):
    fe = FeatureEngine(temp_db)
    logs_sample = [
        {'level': 'INFO', 'message': 'Everything normal'},
        {'level': 'ERROR', 'message': 'Connection timeout while querying redis'},
        {'level': 'CRITICAL', 'message': 'Kernel out of memory: oom process killed'},
    ]
    feats = fe.extract_log_features(logs_sample)
    assert feats['error_count'] == 1
    assert feats['critical_count'] == 1
    assert feats['has_timeout'] == 1
    assert feats['has_oom'] == 1


def test_feature_engine_combined_features(temp_db):
    fe = FeatureEngine(temp_db)
    m_feats = {'current_cpu': 45.0, 'memory_percent_mean': 60.0}
    l_feats = {'error_count': 2, 'warning_count': 1}
    combined = fe.combine_features(m_feats, l_feats)
    assert combined['current_cpu'] == 45.0
    assert combined['error_count'] == 2
    assert len(combined) == 4


# ── 5. Anomaly Detector Tests ───────────────────────────────────────────────

def test_anomaly_detector_training_and_saving(tmp_path):
    model_file = str(tmp_path / "test_anomaly.joblib")
    ad = AnomalyDetector(model_path=model_file)
    synthetic_data = np.random.normal(loc=0.5, scale=0.1, size=(200, 15))
    ad.train(synthetic_data)
    assert ad.model is not None
    assert os.path.exists(model_file)


def test_anomaly_detector_detect(tmp_path):
    model_file = str(tmp_path / "test_anomaly.joblib")
    ad = AnomalyDetector(model_path=model_file)
    X = np.random.normal(loc=0.5, scale=0.1, size=(200, 15))
    ad.train(X)
    normal_vector = np.full(15, 0.5)
    score, is_anomaly = ad.detect(normal_vector)
    assert isinstance(score, float)
    assert isinstance(is_anomaly, (bool, np.bool_))


def test_anomaly_detector_severity_classification():
    ad = AnomalyDetector(model_path="dummy_path.joblib")
    sev_crit = ad.classify_severity(-0.75, {'current_cpu': 98.0})
    assert sev_crit == "CRITICAL"
    sev_high = ad.classify_severity(-0.35, {})
    assert sev_high == "HIGH"
    sev_med = ad.classify_severity(-0.15, {})
    assert sev_med == "MEDIUM"
    sev_low = ad.classify_severity(-0.02, {})
    assert sev_low == "LOW"


def test_anomaly_detector_description_generation():
    ad = AnomalyDetector(model_path="dummy_path.joblib")
    desc = ad.get_anomaly_description({'current_cpu': 96.5, 'error_rate': 0.45}, 'CRITICAL')
    assert isinstance(desc, str)
    assert len(desc) > 5


# ── 6. Failure Predictor Tests ──────────────────────────────────────────────

def test_failure_predictor_dataset_generation():
    fp = FailurePredictor(model_path="dummy_pred.joblib")
    X, y, feature_names = fp.generate_training_data(n_samples=250)
    assert len(X) >= 200
    assert len(y) >= 200
    assert len(feature_names) > 5
    assert set(FailurePredictor.FAILURE_TYPES).issubset(set(np.unique(y)))


def test_failure_predictor_auto_train(tmp_path):
    model_file = str(tmp_path / "test_pred.joblib")
    fp = FailurePredictor(model_path=model_file)
    fp.auto_train()
    assert fp.model is not None
    assert os.path.exists(model_file)


def test_failure_predictor_prediction(tmp_path):
    model_file = str(tmp_path / "test_pred.joblib")
    fp = FailurePredictor(model_path=model_file)
    fp.auto_train()
    sample_vec = np.zeros(len(fp.feature_names))
    res = fp.predict(sample_vec)
    assert 'predicted_failure_type' in res
    assert 'confidence' in res
    assert 'all_probabilities' in res
    assert 0.0 <= res['confidence'] <= 1.0


def test_failure_predictor_top_features(tmp_path):
    model_file = str(tmp_path / "test_pred.joblib")
    fp = FailurePredictor(model_path=model_file)
    fp.auto_train()
    sample_vec = np.ones(len(fp.feature_names)) * 50.0
    top = fp.get_top_contributing_features(sample_vec, fp.feature_names)
    assert len(top) <= 5
    assert 'feature' in top[0]
    assert 'importance' in top[0]


# ── 7. Recovery Engine Tests ────────────────────────────────────────────────

def test_recovery_engine_policies(temp_db):
    re = RecoveryEngine(temp_db)
    assert 'disk_failure' in re.policies
    assert 'memory_exhaustion' in re.policies
    assert 'service_crash' in re.policies


def test_recovery_engine_execution_disk_failure(temp_db):
    re = RecoveryEngine(temp_db)
    report = re.execute_recovery('disk_failure', confidence=0.85)
    assert report['status'] == 'completed'
    assert report['failure_type'] == 'disk_failure'
    actions = temp_db.get_recent_recovery_actions()
    assert len(actions) > 0


def test_recovery_engine_execution_memory_exhaustion(temp_db):
    re = RecoveryEngine(temp_db)
    report = re.execute_recovery('memory_exhaustion', confidence=0.92)
    assert report['status'] == 'completed'


def test_recovery_engine_skips_low_confidence(temp_db):
    re = RecoveryEngine(temp_db)
    report = re.execute_recovery('cpu_overload', confidence=0.40)
    assert report['status'] == 'skipped'


# ── 8. Alert Manager Tests ──────────────────────────────────────────────────

def test_alert_manager_create_alert(temp_db):
    am = AlertManager(temp_db, cooldown=1)
    res = am.create_alert('WARNING', 'Memory reached threshold 85%')
    assert res is not None
    assert res['severity'] == 'WARNING'
    alerts = temp_db.get_recent_alerts()
    assert len(alerts) == 1


def test_alert_manager_cooldown_throttling(temp_db):
    am = AlertManager(temp_db, cooldown=60)
    c1 = am.create_alert('WARNING', 'Identical warning message')
    c2 = am.create_alert('WARNING', 'Identical warning message')
    assert c1 is not None
    assert c2 is None  # Throttled by cooldown


def test_alert_manager_unthrottled_distinct_messages(temp_db):
    am = AlertManager(temp_db, cooldown=60)
    c1 = am.create_alert('WARNING', 'Disk space warning 1')
    c2 = am.create_alert('CRITICAL', 'CPU thermal event 2')
    assert c1 is not None
    assert c2 is not None


# ── 9. Flask Web API & Integration Tests ────────────────────────────────────

@pytest.fixture
def test_client(temp_db):
    state = {
        'health_score': 94.5,
        'status': 'running',
        'anomaly_model_info': {'status': 'trained', 'features': 28},
        'predictor_model_info': {'status': 'trained', 'classes': FailurePredictor.FAILURE_TYPES}
    }
    app = create_app(temp_db, state)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_api_dashboard_endpoint(test_client, temp_db):
    temp_db.insert_log("2026-09-19T20:00:00", "system", "INFO", "Booting")
    rv = test_client.get('/api/dashboard')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['health_score'] == 94.5
    assert data['total_logs'] == 1


def test_api_metrics_endpoint(test_client, temp_db):
    temp_db.insert_metric("2026-09-19T20:00:00", 25.0, 50.0, 60.0, 500, 1000, 10, 20)
    rv = test_client.get('/api/metrics?minutes=5')
    assert rv.status_code == 200
    data = rv.get_json()
    assert len(data) == 1
    assert data[0]['cpu_percent'] == 25.0


def test_api_logs_endpoint(test_client, temp_db):
    temp_db.insert_log("2026-09-19T20:00:00", "application", "ERROR", "Connection dropped")
    rv = test_client.get('/api/logs?limit=10')
    assert rv.status_code == 200
    data = rv.get_json()
    assert len(data) == 1
    assert data[0]['level'] == 'ERROR'


def test_api_anomalies_endpoint(test_client, temp_db):
    temp_db.insert_anomaly("2026-09-19T20:00:00", "system", "HIGH", -0.65, {}, "High latency anomaly")
    rv = test_client.get('/api/anomalies?limit=5')
    assert rv.status_code == 200
    data = rv.get_json()
    assert len(data) == 1
    assert data[0]['severity'] == 'HIGH'


def test_api_predictions_endpoint(test_client, temp_db):
    temp_db.insert_prediction("2026-09-19T20:00:00", "cpu_overload", 0.91, "2026-09-19T20:05:00", {}, "pending")
    rv = test_client.get('/api/predictions?limit=5')
    assert rv.status_code == 200
    data = rv.get_json()
    assert len(data) == 1
    assert data[0]['failure_type'] == 'cpu_overload'


def test_api_recovery_endpoint(test_client, temp_db):
    temp_db.insert_recovery_action("2026-09-19T20:00:00", "memory_exhaustion", "clear_cache", "success", "Flushed buffer cache", 45.0, 85.0)
    rv = test_client.get('/api/recovery?limit=5')
    assert rv.status_code == 200
    data = rv.get_json()
    assert len(data) == 1
    assert data[0]['action_name'] == 'clear_cache'


def test_api_manual_recovery_trigger(test_client):
    rv = test_client.post('/api/recovery/trigger', json={'failure_type': 'service_crash'})
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['status'] == 'triggered'


def test_api_alerts_and_acknowledge(test_client, temp_db):
    temp_db.insert_alert("2026-09-19T20:00:00", "CRITICAL", "Database deadlock detected")
    rv = test_client.get('/api/alerts')
    assert rv.status_code == 200
    data = rv.get_json()
    assert len(data['alerts']) == 1
    alert_id = data['alerts'][0]['id']

    rv_ack = test_client.post(f'/api/alerts/{alert_id}/acknowledge')
    assert rv_ack.status_code == 200
    assert rv_ack.get_json()['status'] == 'acknowledged'


def test_api_timeline_endpoint(test_client, temp_db):
    temp_db.insert_log("2026-09-19T20:00:00", "system", "INFO", "System initialized")
    rv = test_client.get('/api/timeline?limit=10')
    assert rv.status_code == 200
    data = rv.get_json()
    assert len(data) == 1


def test_api_system_info_endpoint(test_client):
    rv = test_client.get('/api/system-info')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['status'] == 'running'
    assert 'models' in data


def test_index_page_serves_html(test_client):
    rv = test_client.get('/')
    assert rv.status_code == 200
    assert b'PredictiveGuard' in rv.data
    assert b'System Metrics' in rv.data
