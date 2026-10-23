"""
Feature engineering pipeline.
Transforms raw metrics and logs into a numeric feature vector for ML models.
Uses pandas for aggregation and numpy for the output array.
"""

import numpy as np
import pandas as pd


class FeatureEngine:
    """Extracts features from metrics and logs for anomaly detection and failure prediction."""

    def __init__(self, database):
        self.db = database

    def extract_metric_features(self, metrics_list):
        """
        Compute statistical features from a list of metric dicts.
        Each dict has keys like cpu_percent, memory_percent, disk_percent, etc.
        Returns a flat dict of features.
        """
        if not metrics_list:
            return {}

        df = pd.DataFrame(metrics_list)
        features = {}

        # Current values (most recent reading)
        last = df.iloc[-1]
        features['current_cpu'] = float(last.get('cpu_percent', 0))
        features['current_memory'] = float(last.get('memory_percent', 0))
        features['current_disk'] = float(last.get('disk_percent', 0))
        features['current_network'] = float(last.get('network_bytes_recv', 0))

        # Stats over the window for each metric
        for col in ['cpu_percent', 'memory_percent', 'disk_percent']:
            if col in df.columns:
                features[f'{col}_mean'] = float(df[col].mean())
                features[f'{col}_std'] = float(df[col].std()) if len(df) > 1 else 0.0
                features[f'{col}_min'] = float(df[col].min())
                features[f'{col}_max'] = float(df[col].max())

                # Rate of change
                if len(df) > 1:
                    roc = float(df[col].iloc[-1] - df[col].iloc[0])
                    features[f'{col}_roc'] = roc
                else:
                    features[f'{col}_roc'] = 0.0

        return features

    def extract_log_features(self, logs_list, time_span_minutes=5):
        """
        Extract features from recent log entries.
        Returns counts and keyword flags.
        """
        features = {
            'error_count': 0,
            'warning_count': 0,
            'critical_count': 0,
            'error_rate': 0.0,
            'unique_error_types': 0,
            'has_timeout': 0,
            'has_oom': 0,
            'has_connection_refused': 0,
            'has_disk_full': 0,
        }

        if not logs_list:
            return features

        df = pd.DataFrame(logs_list)

        # Count log levels
        if 'level' in df.columns:
            counts = df['level'].value_counts()
            features['error_count'] = int(counts.get('ERROR', 0))
            features['warning_count'] = int(counts.get('WARNING', 0))
            features['critical_count'] = int(counts.get('CRITICAL', 0))

        features['error_rate'] = features['error_count'] / max(time_span_minutes, 1)

        # Check for specific keywords in messages
        if 'message' in df.columns:
            msgs = df['message'].str.lower()
            features['unique_error_types'] = int(df['message'].nunique())
            features['has_timeout'] = int(msgs.str.contains('timeout', na=False).any())
            features['has_oom'] = int(msgs.str.contains('oom|out of memory', na=False).any())
            features['has_connection_refused'] = int(msgs.str.contains('connection refused', na=False).any())
            features['has_disk_full'] = int(msgs.str.contains('disk full|no space', na=False).any())

        return features

    def combine_features(self, metric_features, log_features):
        """Merge metric and log features into one dict."""
        combined = {}
        combined.update(metric_features)
        combined.update(log_features)
        return combined

    def get_feature_vector(self, minutes=5):
        """
        Pull recent data from the database, extract features, and return
        a numpy array + list of feature names (sorted for consistency).
        """
        metrics = self.db.get_recent_metrics(limit=minutes * 30)
        logs = self.db.get_recent_logs(limit=200)

        metric_feats = self.extract_metric_features(metrics)
        log_feats = self.extract_log_features(logs, time_span_minutes=minutes)

        combined = self.combine_features(metric_feats, log_feats)

        # Sort keys so the ML model always gets features in the same order
        feature_names = sorted(combined.keys())
        feature_vector = np.array([combined[k] for k in feature_names], dtype=np.float64)

        return feature_vector, feature_names
