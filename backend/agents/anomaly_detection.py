"""
Anomaly Detection Agent - Agent 4 of 8
Flags unusual spikes in real-time
Z-score > 2σ triggers alerts
"""

import anthropic
import json
import logging
import os
from typing import Dict

logger = logging.getLogger(__name__)

class AnomalyDetectionAgent:
    """Detects anomalies and spikes in metrics"""

    def __init__(self, metrics_collector=None):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.metrics = metrics_collector

    async def detect(self, current_metrics: Dict, baseline_metrics: Dict) -> Dict:
        """Flag unusual spikes"""
        if self.metrics:
            self.metrics.start_timer("agent.anomaly_detection")

        system_prompt = """You are an anomaly detection specialist. Compare current metrics to baseline and identify unusual spikes.

For each anomaly:
1. Calculate Z-score: (current - baseline_mean) / baseline_std_dev
2. Flag if Z-score > 2σ (unusual)
3. Assess severity: critical (>3σ), high (2-3σ), moderate (1-2σ)
4. Estimate impact
5. Recommend immediate action

Return JSON with:
- anomalies: Array of detected anomalies
- total_anomalies: Count
- critical_alerts: Count of critical anomalies
- recommended_actions: Array of immediate actions"""

        user_prompt = f"""Current Metrics (today):
{json.dumps(current_metrics, indent=2)}

Baseline Metrics (7-day average):
{json.dumps(baseline_metrics, indent=2)}

Analyze for anomalies and spikes."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            result = json.loads(response.content[0].text)

            if self.metrics:
                self.metrics.record_metric("anomalies.detected_count", result.get('total_anomalies', 0))
                self.metrics.end_timer("agent.anomaly_detection")

            return result

        except Exception as e:
            logger.error(f"Anomaly detection agent error: {str(e)}")
            if self.metrics:
                self.metrics.record_error("agent.anomaly_detection", str(e))
            raise
