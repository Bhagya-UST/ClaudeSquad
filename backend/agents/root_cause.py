"""
Root Cause Agent - Agent 2 of 8
Traces issues to origin (product, supplier, logistics, customer)
"""

import anthropic
import json
import logging
import os
from typing import Dict

logger = logging.getLogger(__name__)

class RootCauseAgent:
    """Identifies root cause of returns"""

    def __init__(self, metrics_collector=None):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.metrics = metrics_collector

    async def analyze(self, return_data: Dict) -> Dict:
        """Trace issues to origin"""
        if self.metrics:
            self.metrics.start_timer("agent.root_cause")

        system_prompt = """You are a root cause analysis expert. Analyze returns to identify the true origin of issues.

Root cause categories:
- PRODUCT_DEFECT: Manufacturing defect
- PRODUCT_DESIGN: Poor product design
- SUPPLIER_QC: Supplier quality control issue
- SIZING_SPEC: Size chart inaccuracy
- LOGISTICS_DAMAGE: Damage in shipping/logistics
- WAREHOUSE_ISSUE: Warehouse handling problem
- CUSTOMER_MISUSE: Customer misuse or misunderstanding
- MARKETING_MISMATCH: Marketing description misleads customers
- RETURN_ABUSE: Abuse of return policy

Analyze and return JSON with:
1. primary_root_cause
2. contributing_factors
3. affected_skus
4. estimated_similar_returns
5. recommended_fixes"""

        user_prompt = f"""Analyze root cause:

Classification: {return_data.get('classification', {})}
Return Reason: {return_data.get('return_reason', '')}
Product Details: {json.dumps(return_data.get('product_info', {}), indent=2)}
Supplier: {return_data.get('supplier_name', 'Unknown')}

Historical Data:
- Total returns for this SKU: {return_data.get('sku_return_count', 0)}
- Return rate for this SKU: {return_data.get('sku_return_rate', 0.0):.1%}
- Other returns from same supplier: {return_data.get('supplier_return_count', 0)}
"""

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
                logger.error(f"Failed to parse root cause response as JSON: {e}")
                result = {
                    "root_cause": "UNKNOWN",
                    "confidence": 0.0,
                    "evidence": []
                }

            if self.metrics:
                self.metrics.end_timer("agent.root_cause")

            return result

        except Exception as e:
            logger.error(f"Root cause agent error: {str(e)}")
            if self.metrics:
                self.metrics.record_error("agent.root_cause", str(e))
            raise
