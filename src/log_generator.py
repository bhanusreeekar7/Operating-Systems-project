import os
import random
import datetime
import json

class LogGenerator:
    """
    Synthetic log generator that simulates realistic multi-source server logs.
    """
    def __init__(self, log_dir):
        """Initialize generator, ensuring log directory exists and setting up paths."""
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        
        self.system_log_path = os.path.join(self.log_dir, 'system.log')
        self.application_log_path = os.path.join(self.log_dir, 'application.log')
        self.network_log_path = os.path.join(self.log_dir, 'network.log')
        self.metrics_log_path = os.path.join(self.log_dir, 'metrics.log')
        
        # Internal state tracking
        self.cpu_base = random.uniform(10.0, 30.0)
        self.memory_base = random.uniform(20.0, 40.0)
        self.disk_base = random.uniform(30.0, 50.0)
        self.network_health = 1.0 # 1.0 is healthy, lower is degraded
        self.uptime_counter = 0
        
        # Anomaly state
        self.anomaly_state = None
        self.anomaly_duration = 0
        self.anomaly_type = None

    def _inject_anomaly_pattern(self):
        """Randomly decides to inject degradation (memory leak, cpu spike, etc.)"""
        if self.anomaly_state is None:
            # 15% chance to start an anomaly pattern
            if random.random() < 0.15:
                self.anomaly_state = 'active'
                self.anomaly_duration = random.randint(10, 20)
                self.anomaly_type = random.choice([
                    'memory_leak', 'cpu_spike', 'disk_filling', 'network_issues'
                ])
        else:
            self.anomaly_duration -= 1
            if self.anomaly_duration <= 0:
                self.anomaly_state = None
                self.anomaly_type = None

    def generate_system_log(self):
        """Generates realistic syslog-format entries"""
        now = datetime.datetime.now().strftime("%b %d %H:%M:%S")
        host = "server-01"
        
        messages = [
            ("CRON[1234]: pam_unix(cron:session): session opened for user root", "INFO"),
            ("systemd[1]: Started Nginx Web Server.", "INFO"),
            ("User session started", "INFO"),
            ("CRON job completed", "INFO"),
            ("kernel: CPU temperature above threshold", "WARNING"),
            ("systemd[1]: service nginx restarting", "WARNING"),
            ("OOM killer invoked for process X", "ERROR"),
            ("kernel: Hardware Error: CPU 0: Machine Check Exception", "CRITICAL")
        ]
        
        # Increase likelihood of issues if an anomaly is active
        if self.anomaly_state == 'active' and self.anomaly_type in ['cpu_spike', 'memory_leak']:
            weights = [1, 1, 1, 1, 3, 3, 5, 2]
        else:
            weights = [10, 10, 10, 10, 2, 1, 0, 0]
            
        msg, level = random.choices(messages, weights=weights, k=1)[0]
        
        log_line = f"{now} {host} {level}: {msg}\n"
        with open(self.system_log_path, 'a') as f:
            f.write(log_line)
            
        return {'timestamp': now, 'source': 'system', 'level': level, 'message': msg}

    def generate_application_log(self):
        """Generates application log entries"""
        now = datetime.datetime.now().isoformat()
        
        messages = [
            ("Request processed in 45ms", "INFO"),
            ("Cache hit rate: 94%", "INFO"),
            ("User session created successfully", "INFO"),
            ("HTTP 500 Internal Server Error on /api/data", "ERROR"),
            ("Database connection timeout after 30s", "ERROR"),
            ("Connection pool exhausted (active: 100/100)", "CRITICAL")
        ]
        
        if self.anomaly_state == 'active':
            weights = [2, 2, 2, 5, 4, 3]
        else:
            weights = [20, 10, 10, 1, 0, 0]
            
        msg, level = random.choices(messages, weights=weights, k=1)[0]
        
        log_line = f"[{now}] [{level}] {msg}\n"
        with open(self.application_log_path, 'a') as f:
            f.write(log_line)
            
        return {'timestamp': now, 'source': 'application', 'level': level, 'message': msg}

    def generate_network_log(self):
        """Generates network log entries"""
        now = datetime.datetime.now().isoformat()
        
        messages = [
            ("Interface eth0 UP", "INFO"),
            ("DNS resolution: 2ms", "INFO"),
            ("New connection established", "INFO"),
            ("Packet loss detected: 15% on eth0", "WARNING"),
            ("Firewall blocked 50 connections from 192.168.1.x", "WARNING"),
            ("BGP peer session down", "ERROR")
        ]
        
        if self.anomaly_state == 'active' and self.anomaly_type == 'network_issues':
            weights = [1, 1, 1, 10, 5, 2]
        else:
            weights = [10, 10, 10, 1, 1, 0]
            
        msg, level = random.choices(messages, weights=weights, k=1)[0]
        
        log_line = f"[{now}] [{level}] Network: {msg}\n"
        with open(self.network_log_path, 'a') as f:
            f.write(log_line)
            
        return {'timestamp': now, 'source': 'network', 'level': level, 'message': msg}

    def generate_metrics(self):
        """Generates system metrics, reflecting any active anomalies"""
        self.uptime_counter += 1
        
        # Apply degradation based on anomaly state
        if self.anomaly_state == 'active':
            if self.anomaly_type == 'cpu_spike':
                self.cpu_base = min(99.0, self.cpu_base + random.uniform(10.0, 20.0))
            elif self.anomaly_type == 'memory_leak':
                self.memory_base = min(99.0, self.memory_base + random.uniform(3.0, 8.0))
            elif self.anomaly_type == 'disk_filling':
                self.disk_base = min(99.0, self.disk_base + random.uniform(2.0, 5.0))
            elif self.anomaly_type == 'network_issues':
                self.network_health = max(0.1, self.network_health - random.uniform(0.1, 0.2))
        else:
            # Gradual recovery to normal baselines
            self.cpu_base = max(10.0, self.cpu_base - random.uniform(1.0, 5.0))
            self.memory_base = max(20.0, self.memory_base - random.uniform(1.0, 3.0))
            self.disk_base = max(30.0, self.disk_base - random.uniform(0.5, 2.0))
            self.network_health = min(1.0, self.network_health + random.uniform(0.05, 0.1))

        # Add some random noise
        cpu = min(100.0, max(0.0, self.cpu_base + random.uniform(-5.0, 5.0)))
        memory = min(100.0, max(0.0, self.memory_base + random.uniform(-2.0, 2.0)))
        disk = min(100.0, max(0.0, self.disk_base + random.uniform(-1.0, 1.0)))
        
        bytes_sent = int(random.uniform(1000, 10000) * self.network_health)
        bytes_recv = int(random.uniform(5000, 20000) * self.network_health)
        disk_read = int(random.uniform(100, 500) * (cpu / 20.0))
        disk_write = int(random.uniform(50, 300) * (cpu / 20.0))

        metrics = {
            'timestamp': datetime.datetime.now().isoformat(),
            'cpu_percent': round(cpu, 2),
            'memory_percent': round(memory, 2),
            'disk_percent': round(disk, 2),
            'network_bytes_sent': bytes_sent,
            'network_bytes_recv': bytes_recv,
            'disk_io_read': disk_read,
            'disk_io_write': disk_write
        }
        
        with open(self.metrics_log_path, 'a') as f:
            f.write(json.dumps(metrics) + "\n")
            
        return metrics

    def generate_all(self):
        """Calls all generators and returns dict with logs and metrics"""
        self._inject_anomaly_pattern()
        
        return {
            'system_log': self.generate_system_log(),
            'application_log': self.generate_application_log(),
            'network_log': self.generate_network_log(),
            'metrics': self.generate_metrics()
        }
