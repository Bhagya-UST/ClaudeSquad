"""
Recommendation Engine - Agent 6 of 8
Generates 5-10 specific, actionable prevention recommendations
"""

import anthropic
import json
import logging
import os
from typing import Dict, List

logger = logging.getLogger(__name__)

class RecommendationAgent:
    """Generates prevention recommendations"""

    def __init__(self, metrics_collector=None):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.metrics = metrics_collector

    async def generate(self, analysis_context: Dict) -> List[Dict]:
        """Generate 5-10 specific recommendations"""
        if self.metrics:
            self.metrics.start_timer("agent.recommendations")

        system_prompt = """You are a retail operations expert. Generate specific, actionable recommendations to prevent similar returns.

Recommendation templates:
1. PRODUCT: Update size chart, add measurement guide, change materials
2. SUPPLIER: Audit QC process, tighten specifications, increase inspections
3. LOGISTICS: Switch carriers, add packaging protection, insurance
4. MARKETING: Adjust product description, add photos, set expectations
5. CUSTOMER: Proactive outreach, coupons for repurchase, loyalty program
6. POLICY: Tighten return eligibility, reduce return window

For each recommendation:
1. Type: PRODUCT, SUPPLIER, LOGISTICS, MARKETING, CUSTOMER, POLICY
2. Specific action (exact steps to implement)
3. Estimated impact (% return reduction)
4. Cost to implement ($)
5. ROI (return value / cost)
6. Timeline (days to implement)
7. Owner (which team)
8. Success metrics (how to measure)

Return JSON array of 5-10 recommendations sorted by impact."""

        user_prompt = f"""Generate prevention recommendations:

{json.dumps(analysis_context, indent=2)}

Focus on highest-ROI, fastest-to-implement actions."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            recommendations = json.loads(response.content[0].text)

            if self.metrics:
                self.metrics.record_metric("recommendations.generated_count", len(recommendations) if isinstance(recommendations, list) else 1)
                self.metrics.end_timer("agent.recommendations")

            return recommendations if isinstance(recommendations, list) else [recommendations]

        except Exception as e:
            logger.error(f"Recommendation agent error: {str(e)}")
            if self.metrics:
                self.metrics.record_error("agent.recommendations", str(e))
            raise
