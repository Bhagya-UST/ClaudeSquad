"""
Emotional Intelligence Agent - Analyzes customer sentiment and churn risk
Sentiment analysis from customer comments
EQ scoring (-5 to +5 scale)
Churn risk detection (EQ < -3.0)
Lifecycle tracking
"""

import anthropic
import json
import logging
import os
from typing import Dict

logger = logging.getLogger(__name__)

class EmotionalIntelligenceAgent:
    """Analyzes customer emotional intelligence and churn risk"""

    def __init__(self, metrics_collector=None):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.metrics = metrics_collector

    async def analyze(self, return_data: Dict) -> Dict:
        """
        Analyze emotional intelligence from return comments

        EQ Scoring:
        -5: Very Angry (intense frustration)
        -4: Angry (strong negative emotion)
        -3: Frustrated (disappointed)
        -2: Dissatisfied (minor complaint)
        0: Neutral
        +2: Satisfied (positive overall)
        +4: Happy (pleased with resolution)
        +5: Delighted (exceeded expectations)

        Intensity: 1-5 (low to extreme)
        Churn Risk: EQ < -3.0 with intensity > 3 = HIGH RISK
        """
        if self.metrics:
            self.metrics.start_timer("agent.emotional_intelligence")

        system_prompt = """You are an emotional intelligence specialist for customer service. Analyze customer sentiment and emotion.

Emotion Scale:
-5: Very Angry, intense frustration with company
-4: Angry, strong negative emotion
-3: Frustrated, disappointed with product/service
-2: Dissatisfied, minor complaint
0: Neutral, no strong emotion
+2: Satisfied, positive overall
+4: Happy, pleased with resolution
+5: Delighted, exceeded expectations

Intensity Scale: 1-5 (low to extreme)

Churn Risk:
- HIGH RISK: EQ < -3.0 with intensity > 3
- MEDIUM RISK: EQ < -2.0 or multiple returns
- LOW RISK: EQ >= 0 or satisfied customer

Return JSON with:
- sentiment_score: -5 to +5
- emotion: Emotion category (angry, frustrated, neutral, satisfied, delighted)
- intensity: 1-5
- churn_risk: boolean
- churn_risk_score: 0.0-1.0
- lifecycle_stage: pre-purchase, purchase, return, post-return
- intervention_needed: boolean
- suggested_intervention: Action to retain customer
- confidence: Confidence in assessment"""

        user_prompt = f"""Analyze emotional intelligence from this return:

Return Reason: {return_data.get('return_reason', '')}

Customer Comments (CRITICAL FOR SENTIMENT):
{return_data.get('customer_comments', '')}

Customer History:
- Total returns: {return_data.get('customer_return_count', 0)}
- Days as customer: {return_data.get('customer_tenure_days', 0)}
- Previous complaints: {return_data.get('previous_complaint_count', 0)}
- Estimated customer LTV: ${return_data.get('customer_ltv', 0)}"""

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
                logger.error(f"Failed to parse EI response as JSON: {e}")
                result = {
                    "sentiment_score": 0.0,
                    "emotion": "UNKNOWN",
                    "intensity": 0,
                    "churn_risk": False,
                    "churn_risk_score": 0.0,
                    "lifecycle_stage": "unknown"
                }

            if result.get('churn_risk', False):
                if self.metrics:
                    self.metrics.record_event("churn_risk.detected", {
                        "score": result.get('churn_risk_score', 0),
                        "customer_ltv": return_data.get('customer_ltv', 0)
                    })

            if self.metrics:
                self.metrics.end_timer("agent.emotional_intelligence")

            return result

        except Exception as e:
            logger.error(f"Emotional intelligence agent error: {str(e)}")
            if self.metrics:
                self.metrics.record_error("agent.emotional_intelligence", str(e))
            raise

    def get_churn_prevention_strategies(self, eq_score: float) -> Dict:
        """Get strategies to prevent churn based on EQ score"""
        strategies = {
            "very_angry": {  # EQ < -4
                "priority": "critical",
                "actions": [
                    "Immediate executive outreach",
                    "Offer proactive resolution",
                    "Personalized recovery plan",
                    "Executive discount/credit"
                ],
                "timeline": "within 1 hour"
            },
            "angry": {  # EQ -4 to -3
                "priority": "high",
                "actions": [
                    "Senior agent personal call",
                    "Acknowledge frustration",
                    "Offer solution options",
                    "Special offer/voucher"
                ],
                "timeline": "within 4 hours"
            },
            "frustrated": {  # EQ -3 to -2
                "priority": "medium",
                "actions": [
                    "Empathetic response",
                    "Explain improvements made",
                    "Offer return/exchange",
                    "Regular follow-up"
                ],
                "timeline": "within 24 hours"
            },
            "satisfied": {  # EQ +2 to +4
                "priority": "low",
                "actions": [
                    "Thank you message",
                    "Loyalty program offer",
                    "Referral incentive"
                ],
                "timeline": "ongoing"
            }
        }

        if eq_score < -4:
            return strategies["very_angry"]
        elif eq_score < -3:
            return strategies["angry"]
        elif eq_score < -2:
            return strategies["frustrated"]
        else:
            return strategies["satisfied"]
