"""
Flask web server with REST API for the PredictiveGuard dashboard.
Simple routes that pull data from the Database class and return JSON.
"""

from flask import Flask, render_template, jsonify, request
from datetime import datetime


def create_app(database, system_state):
    """
    Create and configure the Flask application.

    Args:
        database: Database instance with helper methods.
        system_state: Shared dict updated by the main loop with live health info.

    Returns:
        Configured Flask app.
    """
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    app.config['DB'] = database
    app.config['SYSTEM_STATE'] = system_state

    # Simple CORS headers so the frontend can fetch from any origin
    @app.after_request
    def after_request(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        return response

    # ── Pages ────────────────────────────────────────────────────────────

    @app.route('/')
    def index():
        return render_template('index.html')

    # ── API Routes ───────────────────────────────────────────────────────

    @app.route('/api/dashboard')
    def api_dashboard():
        """Returns live health score, stat counts, and recent alerts."""
        db = app.config['DB']
        state = app.config['SYSTEM_STATE']

        try:
            stats = db.get_dashboard_stats()
        except Exception:
            stats = {}

        return jsonify({
            'health_score': state.get('health_score', 100),
            'total_logs': stats.get('total_logs', 0),
            'active_anomalies': stats.get('total_anomalies', 0),
            'predictions_made': stats.get('pending_predictions', 0),
            'recoveries_executed': stats.get('successful_recoveries', 0),
        })

    @app.route('/api/logs')
    def api_logs():
        """Returns recent logs, optionally filtered by level."""
        db = app.config['DB']
        limit = request.args.get('limit', 50, type=int)

        try:
            logs = db.get_recent_logs(limit=limit)
            # Reverse so oldest first (frontend renders top-to-bottom)
            logs.reverse()
            return jsonify(logs)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/metrics')
    def api_metrics():
        """Returns metrics timeseries for charts."""
        db = app.config['DB']
        minutes = request.args.get('minutes', 5, type=int)

        try:
            metrics = db.get_metrics_timeseries(minutes=minutes)
            return jsonify(metrics)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/anomalies')
    def api_anomalies():
        """Returns recent anomalies."""
        db = app.config['DB']
        limit = request.args.get('limit', 10, type=int)

        try:
            anomalies = db.get_recent_anomalies(limit=limit)
            return jsonify(anomalies)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/predictions')
    def api_predictions():
        """Returns recent failure predictions."""
        db = app.config['DB']
        limit = request.args.get('limit', 10, type=int)

        try:
            predictions = db.get_recent_predictions(limit=limit)
            return jsonify(predictions)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/recovery')
    def api_recovery():
        """Returns recovery action history."""
        db = app.config['DB']
        limit = request.args.get('limit', 10, type=int)

        try:
            actions = db.get_recent_recovery_actions(limit=limit)
            return jsonify(actions)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/recovery/trigger', methods=['POST'])
    def api_trigger_recovery():
        """Manually trigger a recovery action."""
        data = request.get_json(silent=True) or {}
        failure_type = data.get('failure_type')

        if not failure_type:
            return jsonify({'error': 'failure_type is required'}), 400

        # Store intent in system_state so the main loop picks it up
        state = app.config['SYSTEM_STATE']
        state['manual_recovery'] = failure_type

        return jsonify({
            'status': 'triggered',
            'message': f'Manual recovery triggered for {failure_type}'
        })

    @app.route('/api/model-stats')
    def api_model_stats():
        """Returns model performance info from system state."""
        state = app.config['SYSTEM_STATE']
        return jsonify({
            'anomaly_detector': state.get('anomaly_model_info', {'status': 'not trained'}),
            'failure_predictor': state.get('predictor_model_info', {'status': 'not trained'}),
        })

    @app.route('/api/alerts')
    def api_alerts():
        """Returns recent alerts with acknowledgment status."""
        db = app.config['DB']
        limit = request.args.get('limit', 20, type=int)

        try:
            alerts = db.get_recent_alerts(limit=limit)
            unack_count = db.get_unacknowledged_alert_count()
            return jsonify({'alerts': alerts, 'unacknowledged_count': unack_count})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/alerts/<int:alert_id>/acknowledge', methods=['POST'])
    def api_acknowledge_alert(alert_id):
        """Mark an alert as acknowledged."""
        db = app.config['DB']
        try:
            db.acknowledge_alert(alert_id)
            return jsonify({'status': 'acknowledged', 'id': alert_id})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/timeline')
    def api_timeline():
        """Returns a unified event feed combining logs, anomalies, predictions, and recoveries."""
        db = app.config['DB']
        limit = request.args.get('limit', 50, type=int)

        try:
            events = db.get_timeline_events(limit=limit)
            return jsonify(events)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/system-info')
    def api_system_info():
        """Returns system metadata, uptime, and configuration summary."""
        state = app.config['SYSTEM_STATE']
        import config as cfg
        return jsonify({
            'status': state.get('status', 'unknown'),
            'health_score': state.get('health_score', 100),
            'demo_mode': getattr(cfg, 'DEMO_MODE', True),
            'dashboard_port': getattr(cfg, 'DASHBOARD_PORT', 5000),
            'log_interval': getattr(cfg, 'LOG_GENERATION_INTERVAL', 2),
            'prediction_threshold': getattr(cfg, 'PREDICTION_THRESHOLD', 0.7),
            'anomaly_contamination': getattr(cfg, 'ANOMALY_CONTAMINATION', 0.1),
            'recovery_policies': list(getattr(cfg, 'RECOVERY_POLICIES', {}).keys()),
            'models': {
                'anomaly_detector': state.get('anomaly_model_info', {}),
                'failure_predictor': state.get('predictor_model_info', {}),
            }
        })

    return app
