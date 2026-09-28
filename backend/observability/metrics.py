"""Metrics collection for ReturnIQ observability"""

from prometheus_client import Counter, Histogram, Gauge
from datetime import datetime
from collections import defaultdict
import time

class MetricsCollector:
    """Collects and tracks all system metrics"""

    def __init__(self):
        # LLM Metrics
        self.llm_tokens = Counter('llm_tokens_total', 'Total LLM tokens used')
        self.llm_latency = Histogram('llm_latency_seconds', 'LLM API latency')
        self.llm_errors = Counter('llm_errors_total', 'LLM API errors')
        self.hallucination_rate = Gauge('llm_hallucination_rate', 'Hallucination rate')

        # Agent Metrics
        self.classification_accuracy = Gauge('classification_accuracy', 'Classification accuracy')
        self.recommendation_approval_rate = Gauge('recommendation_approval_rate', 'Approval rate')

        # RAG Metrics
        self.retrieval_accuracy = Gauge('rag_retrieval_accuracy', 'Retrieval accuracy')

        # Business Metrics
        self.returns_prevented = Counter('business_returns_prevented', 'Returns prevented')
        self.estimated_savings = Gauge('business_savings_usd', 'Estimated savings')

        # Internal tracking
        self.timers = {}
        self.metrics_history = defaultdict(list)
        self.start_time = datetime.now()
        self.last_error = None

    def start_timer(self, name):
        """Start tracking time for an operation"""
        self.timers[name] = time.time()

    def end_timer(self, name):
        """End timer and record latency"""
        if name in self.timers:
            elapsed = time.time() - self.timers[name]
            del self.timers[name]
            self.llm_latency.observe(elapsed)
            return elapsed
        return None

    def record_metric(self, name, value):
        """Record a metric value"""
        self.metrics_history[name].append({
            'value': value,
            'timestamp': datetime.now()
        })

        if name == 'classification.accuracy':
            self.classification_accuracy.set(value)
        elif name == 'classification.confidence':
            pass  # Track separately
        elif name == 'hallucination_rate':
            self.hallucination_rate.set(value)

    def record_error(self, component, error_msg):
        """Record an error"""
        self.llm_errors.inc()
        self.last_error = {
            'component': component,
            'error': error_msg,
            'timestamp': datetime.now()
        }

    def record_event(self, event_name, data=None):
        """Record an event"""
        self.metrics_history[f'event.{event_name}'].append({
            'data': data,
            'timestamp': datetime.now()
        })

    def get_metric(self, name):
        """Get current metric value"""
        history = self.metrics_history.get(name, [])
        if history:
            return history[-1]['value']
        return 0

    def get_timeseries(self, name, days=7):
        """Get time series data for a metric"""
        history = self.metrics_history.get(name, [])
        return [
            {
                'timestamp': h['timestamp'].isoformat(),
                'value': h['value']
            }
            for h in history[-days*24:]  # Last N days
        ]

    def get_last_error(self):
        """Get last recorded error"""
        return self.last_error

    def get_uptime(self):
        """Get system uptime in seconds"""
        return (datetime.now() - self.start_time).total_seconds()

    def start(self):
        """Start metrics collection"""
        pass

    def stop(self):
        """Stop metrics collection"""
        pass
