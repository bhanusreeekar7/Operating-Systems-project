"""
Failure prediction using Random Forest classifier.
Classifies the current system state into one of several failure types.
Includes synthetic training data generation for demo mode.
"""

import os
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier


class FailurePredictor:
    """Predicts failure types using a Random Forest trained on system features."""

    FAILURE_TYPES = [
        'normal',
        'disk_failure',
        'memory_exhaustion',
        'cpu_overload',
        'service_crash',
        'network_outage',
    ]

    def __init__(self, model_path='models/predictor_model.joblib'):
        self.model_path = model_path
        self.model = None
        self.feature_names = None

        if os.path.exists(model_path):
            try:
                data = joblib.load(model_path)
                self.model = data['model']
                self.feature_names = data['feature_names']
            except Exception as e:
                print(f"Failed to load predictor model: {e}")

    def train(self, feature_matrix, labels, feature_names):
        """Train the Random Forest and save to disk."""
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(feature_matrix, labels)
        self.feature_names = feature_names

        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump({'model': self.model, 'feature_names': feature_names}, self.model_path)
        print(f"Predictor model saved to {self.model_path}")

    def predict(self, feature_vector):
        """
        Predict the failure type for a given feature vector.
        Returns dict with predicted type, confidence, and all probabilities.
        """
        if self.model is None:
            return {'predicted_failure_type': 'normal', 'confidence': 0.0, 'all_probabilities': {}}

        X = feature_vector.reshape(1, -1)
        pred = self.model.predict(X)[0]
        probs = self.model.predict_proba(X)[0]

        idx = list(self.model.classes_).index(pred)
        confidence = float(probs[idx])

        all_probs = {cls: float(p) for cls, p in zip(self.model.classes_, probs)}

        return {
            'predicted_failure_type': pred,
            'confidence': confidence,
            'all_probabilities': all_probs,
        }

    def generate_training_data(self, n_samples=1000):
        """
        Generate synthetic labeled training data.
        Feature names must match what FeatureEngine.get_feature_vector() produces.
        """
        # These feature names match the sorted output of FeatureEngine
        feature_names = sorted([
            'cpu_percent_max', 'cpu_percent_mean', 'cpu_percent_min',
            'cpu_percent_roc', 'cpu_percent_std',
            'critical_count', 'current_cpu', 'current_disk',
            'current_memory', 'current_network',
            'disk_percent_max', 'disk_percent_mean', 'disk_percent_min',
            'disk_percent_roc', 'disk_percent_std',
            'error_count', 'error_rate',
            'has_connection_refused', 'has_disk_full', 'has_oom', 'has_timeout',
            'memory_percent_max', 'memory_percent_mean', 'memory_percent_min',
            'memory_percent_roc', 'memory_percent_std',
            'unique_error_types', 'warning_count',
        ])

        X = []
        y = []
        per_class = max(1, n_samples // len(self.FAILURE_TYPES))

        for label in self.FAILURE_TYPES:
            for _ in range(per_class):
                feat = {k: 0.0 for k in feature_names}

                # Normal baselines
                feat['current_cpu'] = np.random.uniform(10, 50)
                feat['current_memory'] = np.random.uniform(20, 50)
                feat['current_disk'] = np.random.uniform(20, 50)
                feat['current_network'] = np.random.uniform(5000, 15000)
                feat['cpu_percent_mean'] = feat['current_cpu'] + np.random.uniform(-5, 5)
                feat['memory_percent_mean'] = feat['current_memory'] + np.random.uniform(-5, 5)
                feat['disk_percent_mean'] = feat['current_disk'] + np.random.uniform(-5, 5)

                # Add failure-specific patterns
                if label == 'disk_failure':
                    feat['current_disk'] = np.random.uniform(85, 99)
                    feat['disk_percent_max'] = np.random.uniform(90, 100)
                    feat['disk_percent_roc'] = np.random.uniform(2, 10)
                    feat['has_disk_full'] = 1.0
                    feat['error_count'] = np.random.randint(5, 20)
                elif label == 'memory_exhaustion':
                    feat['current_memory'] = np.random.uniform(88, 99)
                    feat['memory_percent_max'] = np.random.uniform(92, 100)
                    feat['memory_percent_roc'] = np.random.uniform(3, 12)
                    feat['has_oom'] = 1.0
                    feat['error_count'] = np.random.randint(5, 15)
                elif label == 'cpu_overload':
                    feat['current_cpu'] = np.random.uniform(90, 100)
                    feat['cpu_percent_max'] = np.random.uniform(95, 100)
                    feat['cpu_percent_roc'] = np.random.uniform(5, 20)
                elif label == 'service_crash':
                    feat['error_count'] = np.random.randint(15, 50)
                    feat['error_rate'] = np.random.uniform(5, 15)
                    feat['critical_count'] = np.random.randint(2, 10)
                    feat['has_timeout'] = 1.0
                elif label == 'network_outage':
                    feat['has_connection_refused'] = 1.0
                    feat['current_network'] = np.random.uniform(0, 1000)
                    feat['error_count'] = np.random.randint(10, 30)

                X.append([feat[k] for k in feature_names])
                y.append(label)

        return np.array(X), np.array(y), feature_names

    def auto_train(self):
        """Generate synthetic data and train the model. Used for demo mode."""
        X, y, names = self.generate_training_data()
        self.train(X, y, names)

    def get_top_contributing_features(self, feature_vector, feature_names):
        """Return top 5 features by importance for this prediction."""
        if self.model is None:
            return []

        importances = self.model.feature_importances_
        indices = np.argsort(importances)[::-1]

        top = []
        for i in indices[:5]:
            top.append({
                'feature': feature_names[i],
                'importance': float(importances[i]),
                'value': float(feature_vector[i]),
            })
        return top
