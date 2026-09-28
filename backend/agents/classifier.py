"""
Classification Agent - Agent 1 of 8
Categorizes returns into categories (sizing, quality, fraud, etc.)
Target accuracy: 96.2%
"""

import anthropic
import json
import logging
import os
from typing import Dict

logger = logging.getLogger(__name__)

class ClassifierAgent:
    """Classifies returns into 10+ categories"""

    def __init__(self, metrics_collector=None):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.metrics = metrics_collector

    async def classify(self, return_data: Dict) -> Dict:
        """
        Classify return into categories
        Input: return reason + customer comments + product metadata
        Output: Classification + confidence score
        """
        if self.metrics:
            self.metrics.start_timer("agent.classifier")

        system_prompt = """You are a retail return classification expert. Analyze the return reason and customer comments to classify the return into one of these categories:

1. SIZING - Customer ordered wrong size
2. QUALITY - Product has defects or poor quality
3. DEFECTIVE - Product doesn't work/DOA
4. FRAUD - Wardrobing, return-and-resell, damaged on purpose
5. LOGISTICS - Damaged in shipping
6. DUPLICATE - Accidentally ordered duplicate
7. CHANGE_MIND - Customer changed their mind
8. DAMAGED - Customer damaged the product
9. INCOMPATIBLE - Product incompatible with customer needs
10. OTHER - Doesn't fit other categories

Return a JSON response with:
- category: One of the categories above
- confidence: 0.0-1.0 confidence score
- reasoning: Brief explanation (2-3 sentences)
- key_indicators: List of phrases that led to this classification"""

        user_prompt = f"""
Classify this return:

Return Reason: {return_data.get('return_reason', '')}

Customer Comments: {return_data.get('customer_comments', '')}

Product Info: {json.dumps(return_data.get('product_info', {}), indent=2)}

Previous Returns by Customer: {json.dumps(return_data.get('customer_history', []), indent=2)}
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            try:
                result = json.loads(response.content[0].text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse classifier response as JSON: {e}")
                result = {
                    "category": "OTHER",
                    "confidence": 0.0,
                    "reasoning": "Failed to parse AI response",
                    "key_indicators": []
                }

            if self.metrics:
                self.metrics.record_metric("classification.confidence", result['confidence'])
                self.metrics.end_timer("agent.classifier")

            return {
                "category": result.get('category', 'OTHER'),
                "confidence": result.get('confidence', 0.0),
                "reasoning": result.get('reasoning', ''),
                "key_indicators": result.get('key_indicators', []),
                "agent_version": "1.0"
            }

        except Exception as e:
            logger.error(f"Classifier agent error: {str(e)}")
            if self.metrics:
                self.metrics.record_error("agent.classifier", str(e))
            raise
