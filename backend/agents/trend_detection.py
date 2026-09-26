"""
Trend Detection Agent - Agent 3 of 8
Identifies statistical patterns with significance testing
Z-score > 2σ flags alerts
"""

import anthropic
import json
import logging
import os
from typing import Dict, List

logger = logging.getLogger(__name__)

class TrendDetectionAgent:
    """Detects trends and patterns in returns"""

    def __init__(self, metrics_collector=None):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.metrics = metrics_collector

    async def detect(self, returns_data: List[Dict]) -> List[Dict]:
        """Identify statistical patterns with Z-score significance"""
        if self.metrics:
            self.metrics.start_timer("agent.trend_detection")

        system_prompt = """You are a statistical analysis expert. Identify meaningful patterns in return data.

For each trend:
1. Calculate return rate and Z-score
2. Flag if Z-score > 2σ (statistically significant)
3. Estimate impact (# orders affected, $ at risk)
4. Identify root causes

Return JSON array of trends sorted by Z-score (highest first).

Each trend should include:
- title: Descriptive title (5-10 words)
- description: 1-2 sentence explanation
- returns_count: Number of returns in pattern
- percentage: % of total returns
- z_score: Statistical significance
- significance: "critical" (>3σ), "high" (2-3σ), "moderate" (1-2σ)
- affected_skus: List of SKU IDs
- estimated_impact_dollars: $ at risk
- evidence_returns: Array of supporting return IDs
- recommended_action: Action to address"""

        aggregated = {
            "total_returns": len(returns_data),
            "top_classifications": self._aggregate_classifications(returns_data),
            "top_products": self._aggregate_products(returns_data),
            "top_suppliers": self._aggregate_suppliers(returns_data),
            "time_period": "last 7 days",
            "sample_returns": returns_data[:10]
        }

        user_prompt = f"""Analyze these return patterns:

{json.dumps(aggregated, indent=2)}

Calculate trends, Z-scores, and significance. Focus on:
1. Product/SKU patterns
2. Supplier patterns
3. Classification patterns
4. Time-based patterns"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            trends = json.loads(response.content[0].text)

            if self.metrics:
                self.metrics.record_metric("trends.detected_count", len(trends) if isinstance(trends, list) else 1)
                self.metrics.end_timer("agent.trend_detection")

            return trends if isinstance(trends, list) else [trends]

        except Exception as e:
            logger.error(f"Trend detection agent error: {str(e)}")
            if self.metrics:
                self.metrics.record_error("agent.trend_detection", str(e))
            raise

    def _aggregate_classifications(self, returns_data):
        """Aggregate by classification"""
        agg = {}
        for ret in returns_data:
            cat = ret.get('classification', 'unknown')
            agg[cat] = agg.get(cat, 0) + 1
        return agg

    def _aggregate_products(self, returns_data):
        """Aggregate by product"""
        agg = {}
        for ret in returns_data:
            sku = ret.get('product_id', 'unknown')
            agg[sku] = agg.get(sku, 0) + 1
        return dict(sorted(agg.items(), key=lambda x: x[1], reverse=True)[:10])

    def _aggregate_suppliers(self, returns_data):
        """Aggregate by supplier"""
        agg = {}
        for ret in returns_data:
            supplier = ret.get('supplier_name', 'unknown')
            agg[supplier] = agg.get(supplier, 0) + 1
        return dict(sorted(agg.items(), key=lambda x: x[1], reverse=True)[:10])
