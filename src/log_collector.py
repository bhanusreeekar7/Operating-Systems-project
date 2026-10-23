import re
import datetime

class LogCollector:
    """
    Log collection and parsing engine.
    Parses incoming raw log lines into structured data.
    """
    def __init__(self, log_sources, database):
        self.log_sources = log_sources
        self.db = database
        
        # Regex for Syslog: Oct 12 14:22:10 server-01 INFO: System started
        self.syslog_pattern = re.compile(
            r"^(?P<timestamp>[A-Z][a-z]{2}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+\S+\s+(?P<level>INFO|WARNING|ERROR|CRITICAL):\s+(?P<message>.*)$"
        )
        
        # Regex for App log: [2023-10-12T14:22:10] [ERROR] HTTP 500 Internal Server Error on /api/data
        self.app_log_pattern = re.compile(
            r"^\[(?P<timestamp>.*?)\]\s+\[(?P<level>INFO|WARNING|ERROR|CRITICAL)\]\s+(?P<message>.*)$"
        )
        
        # Regex for Network log: [2023-10-12T14:22:10] [WARNING] Network: Packet loss detected: 15% on eth0
        self.network_log_pattern = re.compile(
            r"^\[(?P<timestamp>.*?)\]\s+\[(?P<level>INFO|WARNING|ERROR|CRITICAL)\]\s+Network:\s+(?P<message>.*)$"
        )

    def parse_syslog(self, line):
        """Extracts timestamp, level, message from syslog format"""
        match = self.syslog_pattern.match(line.strip())
        if match:
            return match.groupdict()
        return None

    def parse_app_log(self, line):
        """Extracts timestamp, level, message from app log format. Tries to extract endpoint."""
        match = self.app_log_pattern.match(line.strip())
        if match:
            data = match.groupdict()
            # Simple check for endpoint
            endpoint_match = re.search(r"on\s+(/[/\w]+)", data['message'])
            data['endpoint'] = endpoint_match.group(1) if endpoint_match else None
            return data
        return None

    def parse_network_log(self, line):
        """Extracts timestamp, level, message from network log. Tries to extract interface."""
        match = self.network_log_pattern.match(line.strip())
        if match:
            data = match.groupdict()
            # Simple check for interface (e.g. eth0)
            if_match = re.search(r"on\s+(\w+)", data['message'])
            data['interface'] = if_match.group(1) if if_match else None
            return data
        return None

    def collect_and_parse(self, source_name, raw_log):
        """Parses based on source type and stores in database."""
        parsed_data = None
        
        if source_name == 'system':
            parsed_data = self.parse_syslog(raw_log)
        elif source_name == 'application':
            parsed_data = self.parse_app_log(raw_log)
        elif source_name == 'network':
            parsed_data = self.parse_network_log(raw_log)
            
        if parsed_data:
            parsed_data['source'] = source_name
            # Store in database
            # Assuming db has an insert_log method
            if hasattr(self.db, 'insert_log'):
                self.db.insert_log(
                    source=parsed_data['source'],
                    level=parsed_data['level'],
                    message=parsed_data['message'],
                    timestamp=parsed_data['timestamp']
                )
            return parsed_data
        
        return None

    def get_log_stats(self, minutes=5):
        """
        Returns count of logs by level in last N minutes.
        Relies on the database having a get_logs_since method.
        """
        cutoff_time = datetime.datetime.now() - datetime.timedelta(minutes=minutes)
        
        # If database provides a way to get recent logs
        stats = {'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0}
        
        if hasattr(self.db, 'get_logs_since'):
            recent_logs = self.db.get_logs_since(cutoff_time)
            for log in recent_logs:
                level = log.get('level')
                if level in stats:
                    stats[level] += 1
                    
        return stats
