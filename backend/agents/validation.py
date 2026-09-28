"""
Validation Agent - Agent 7 of 8
Quality-gates recommendations before display
"""

import anthropic
import json
import logging
import os
from typing import Dict

logger = logging.getLogger(__name__)

class ValidationAgent:
    """Validates recommendations for quality and safety"""

    def __init__(self, metrics_collector=None):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.metrics = metrics_collector

    async def validate(self, recommendation: Dict) -> Dict:
        """Validate recommendation before display"""
        if self.metrics:
            self.metrics.start_timer("agent.validation")

        system_prompt = """You are a quality assurance specialist for AI recommendations. Validate before display.

Validation criteria:
1. Confidence: > 70%?
2. Evidence: Backed by supporting data?
3. Harmfulness: No harmful suggestions?
4. Factuality: Statistics accurate?
5. Fairness: Doesn't disproportionately impact one segment?

Return JSON with:
- status: "approved" or "flagged"
- reasons: Array of validation reasons
- confidence_score: 0.0-1.0
- concerns: Array of any concerns
- recommended_human_review: boolean
- approval_summary: 1-2 sentence summary"""

        user_prompt = f"""Validate this recommendation:

{json.dumps(recommendation, indent=2)}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=600,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            result = json.loads(response.content[0].text)

            if self.metrics:
                self.metrics.end_timer("agent.validation")

            return result

        except Exception as e:
            logger.error(f"Validation agent error: {str(e)}")
            if self.metrics:
                self.metrics.record_error("agent.validation", str(e))
            raise
