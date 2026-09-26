"""
Fraud Detection Agent - Agent 5 of 8
Detects wardrobing, return-and-resell patterns
"""

import anthropic
import json
import logging
import os
from typing import Dict

logger = logging.getLogger(__name__)

class FraudDetectionAgent:
    """Detects fraudulent return patterns"""

    def __init__(self, metrics_collector=None):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.metrics = metrics_collector

    async def detect(self, return_data: Dict) -> Dict:
        """Detect wardrobing and return-and-resell patterns"""
        if self.metrics:
            self.metrics.start_timer("agent.fraud_detection")

        system_prompt = """You are a fraud detection specialist. Identify suspicious return patterns:

Red flags:
- Same customer, same product, multiple returns in 7 days
- Product returned "never worn" but customer has 10+ previous returns
- High-value items returned within 2 hours of purchase
- Product returned in different condition than purchased
- Serial number/tags removed but claimed "never opened"
- Coordinated returns from multiple accounts (same IP, card)

Return JSON with:
- fraud_risk_score: 0.0-1.0 (0=clean, 1.0=certain fraud)
- red_flags: Array of detected red flags
- risk_level: "low", "medium", "high"
- recommended_action: "approve", "investigate", "reject"
- confidence: Confidence in assessment"""

        user_prompt = f"""Analyze fraud risk:

Return Data:
{json.dumps(return_data, indent=2)}

Customer Return History:
{json.dumps(return_data.get('customer_return_history', []), indent=2)}

Product Price: ${return_data.get('product_price', 0)}
Condition Reported: {return_data.get('product_condition', 'unknown')}
Days Since Purchase: {return_data.get('days_since_purchase', 'unknown')}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            try:
                result = json.loads(response.content[0].text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse fraud detection response as JSON: {e}")
                result = {
                    "fraud_risk_score": 0.0,
                    "fraud_indicators": [],
                    "is_fraud": False,
                    "confidence": 0.0
                }

            if result.get('fraud_risk_score', 0) > 0.7:
                if self.metrics:
                    self.metrics.record_event("fraud.detected", {"risk_score": result['fraud_risk_score']})

            if self.metrics:
                self.metrics.end_timer("agent.fraud_detection")

            return result

        except Exception as e:
            logger.error(f"Fraud detection agent error: {str(e)}")
            if self.metrics:
                self.metrics.record_error("agent.fraud_detection", str(e))
            raise
