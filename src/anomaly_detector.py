import os
import joblib
from sklearn.ensemble import IsolationForest

class AnomalyDetector:
    """
    Anomaly detection model using Isolation Forest to detect abnormal system states.
    """
    def __init__(self, model_path='models/anomaly_model.joblib'):
        """
        Initialize the anomaly detector. Load model if it exists.
        """
        self.model_path = model_path
        self.model = None
        
        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
            except Exception as e:
                print(f"Failed to load model from {model_path}: {e}")

    def train(self, feature_matrix):
        """
        Trains Isolation Forest with contamination=0.1
        """
        self.model = IsolationForest(contamination=0.1, n_estimators=100, random_state=42)
        self.model.fit(feature_matrix)
        
        # Ensure directory exists before saving
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(self.model, self.model_path)
        print(f"Anomaly model saved to {self.model_path}")

    def detect(self, feature_vector):
        """
        Returns anomaly_score (negative is anomaly) and is_anomaly boolean.
        """
        if self.model is None:
            raise ValueError("Model is not trained or loaded.")
            
        # Reshape to 2D array for sklearn
        X = feature_vector.reshape(1, -1)
        score = self.model.decision_function(X)[0]
        # prediction = 1 for normal, -1 for anomaly
        prediction = self.model.predict(X)[0]
        is_anomaly = prediction == -1
        
        return score, is_anomaly

    def classify_severity(self, score, features_dict):
        """
        Returns severity string based on score and specific features.
        """
        if score < -0.5:
            severity = "CRITICAL"
        elif score < -0.3:
            severity = "HIGH"
        elif score < -0.1:
            severity = "MEDIUM"
        else:
            severity = "LOW"
            
        # Bump severity if key resources are dangerously high
        cpu = features_dict.get('current_cpu', 0)
        memory = features_dict.get('current_memory', 0)
        disk = features_dict.get('current_disk', 0)
        
        if cpu > 95 or memory > 95 or disk > 95:
            if severity == "LOW":
                severity = "MEDIUM"
            elif severity == "MEDIUM":
                severity = "HIGH"
            elif severity == "HIGH":
                severity = "CRITICAL"
                
        return severity

    def get_anomaly_description(self, features_dict, severity):
        """
        Generates human-readable description of the anomaly based on features.
        """
        desc = [f"Anomaly detected with severity: {severity}."]
        
        cpu = features_dict.get('current_cpu', 0)
        if cpu > 90:
            desc.append(f"High CPU usage: {cpu:.1f}%.")
            
        memory = features_dict.get('current_memory', 0)
        if memory > 90:
            desc.append(f"High Memory usage: {memory:.1f}%.")
            
        disk = features_dict.get('current_disk', 0)
        if disk > 90:
            desc.append(f"High Disk usage: {disk:.1f}%.")
            
        errors = features_dict.get('error_count', 0)
        if errors > 10:
            desc.append(f"High error count: {errors} errors in recent window.")
            
        if len(desc) == 1:
            desc.append("System is exhibiting abnormal behavior across multiple metrics.")
            
        return " ".join(desc)
