"""
ReturnIQ Agent Orchestrator - 8 Specialized Agents
"""

import anthropic
import json
import asyncio
import os
from typing import Dict, List, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """Orchestrates 8 specialized Claude agents for return analysis"""

    def __init__(self, rag_system, metrics_collector):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.rag = rag_system
        self.metrics = metrics_collector

    # =========================================================================
    # AGENT 1: CLASSIFICATION AGENT
    # =========================================================================

    async def run_classifier_agent(self, return_data: Dict) -> Dict:
        """
        Classify return into categories (sizing, quality, fraud, etc.)
        Target accuracy: 96.2%
        """
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
            # Retrieve context from RAG
            rag_context = self.rag.retrieve_context(return_data)
            user_prompt += f"\n\nSimilar Past Returns for Context:\n{json.dumps(rag_context, indent=2)}"

            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            result = json.loads(response.content[0].text)

            self.metrics.record_metric("classification.confidence", result['confidence'])
            self.metrics.end_timer("agent.classifier")

            return {
                "category": result['category'],
                "confidence": result['confidence'],
                "reasoning": result['reasoning'],
                "key_indicators": result.get('key_indicators', []),
                "agent_version": "1.0"
            }

        except Exception as e:
            logger.error(f"Classifier agent error: {str(e)}")
            self.metrics.record_error("agent.classifier", str(e))
            raise

    # =========================================================================
    # AGENT 2: ROOT CAUSE AGENT
    # =========================================================================

    async def run_root_cause_agent(self, return_data: Dict) -> Dict:
        """
        Trace issues to origin (product, supplier, logistics, customer)
        """
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

Analyze the return and identify:
1. Primary root cause
2. Contributing factors
3. Historical evidence (similar returns with same cause)
4. Affected SKUs or products
5. Estimated number of similar returns
6. Recommended fixes

Return JSON response."""

        user_prompt = f"""
Analyze root cause for this return:

Classification: {return_data.get('classification', {})}
Return Reason: {return_data.get('return_reason', '')}
Customer Comments: {return_data.get('customer_comments', '')}
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

            result = json.loads(response.content[0].text)

            self.metrics.end_timer("agent.root_cause")
            return result

        except Exception as e:
            logger.error(f"Root cause agent error: {str(e)}")
            self.metrics.record_error("agent.root_cause", str(e))
            raise

    # =========================================================================
    # AGENT 3: TREND DETECTION AGENT
    # =========================================================================

    async def run_trend_detection_agent(self, returns_data: List[Dict]) -> List[Dict]:
        """
        Identify statistical patterns with significance testing
        Z-score > 2σ flags alerts
        """
        self.metrics.start_timer("agent.trend_detection")

        system_prompt = """You are a statistical analysis expert for retail returns. Identify meaningful patterns and trends in return data.

For each trend:
1. Calculate return rate: returns_count / total_orders
2. Calculate Z-score: (observed_rate - baseline_rate) / std_dev
3. Flag if Z-score > 2σ (statistically significant)
4. Estimate impact (# orders affected, $ at risk)
5. Identify root causes

Return a JSON array of trends sorted by Z-score (highest first).

Each trend should include:
- title: Descriptive title (5-10 words)
- description: 1-2 sentence explanation
- returns_count: Number of returns in this pattern
- percentage: % of total returns
- z_score: Statistical significance score
- significance: "critical" (>3σ), "high" (2-3σ), "moderate" (1-2σ)
- affected_skus: List of SKU IDs
- estimated_impact_dollars: $ at risk
- evidence_returns: Array of 5-10 return IDs supporting this trend
- recommended_action: Brief action to address trend"""

        # Aggregate return data
        aggregated = {
            "total_returns": len(returns_data),
            "top_classifications": self._aggregate_classifications(returns_data),
            "top_products": self._aggregate_products(returns_data),
            "top_suppliers": self._aggregate_suppliers(returns_data),
            "time_period": "last 7 days",
            "sample_returns": returns_data[:10]
        }

        user_prompt = f"""
Analyze these return patterns:

{json.dumps(aggregated, indent=2)}

Calculate trends, Z-scores, and significance. Focus on:
1. Product/SKU patterns
2. Supplier patterns
3. Classification patterns
4. Time-based patterns (if timestamps available)
5. Geographic patterns (if location data available)
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            trends = json.loads(response.content[0].text)

            self.metrics.record_metric("trends.detected_count", len(trends))
            self.metrics.end_timer("agent.trend_detection")

            return trends if isinstance(trends, list) else [trends]

        except Exception as e:
            logger.error(f"Trend detection agent error: {str(e)}")
            self.metrics.record_error("agent.trend_detection", str(e))
            raise

    # =========================================================================
    # AGENT 4: ANOMALY DETECTION AGENT
    # =========================================================================

    async def run_anomaly_detection_agent(self, current_metrics: Dict, baseline_metrics: Dict) -> Dict:
        """
        Flag unusual spikes in real-time
        Z-score > 2σ triggers alerts
        """
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

        user_prompt = f"""
Current Metrics (today):
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

            self.metrics.record_metric("anomalies.detected_count", result.get('total_anomalies', 0))
            self.metrics.end_timer("agent.anomaly_detection")

            return result

        except Exception as e:
            logger.error(f"Anomaly detection agent error: {str(e)}")
            self.metrics.record_error("agent.anomaly_detection", str(e))
            raise

    # =========================================================================
    # AGENT 5: FRAUD DETECTION AGENT
    # =========================================================================

    async def run_fraud_detection_agent(self, return_data: Dict) -> Dict:
        """
        Detect wardrobing, return-and-resell patterns
        """
        self.metrics.start_timer("agent.fraud_detection")

        system_prompt = """You are a fraud detection specialist for e-commerce returns. Identify suspicious patterns:

Red flags:
- Same customer, same product, multiple returns in 7 days
- Product returned "never worn" but customer has 10+ previous returns
- High-value items returned within 2 hours of purchase
- Product returned in different condition than purchased
- Serial number/tags removed but claimed "never opened"
- Returns from wholesale/dropship accounts for personal use items
- Coordinated returns from multiple accounts (same IP, card)

Return JSON with:
- fraud_risk_score: 0.0-1.0 (0=clean, 1.0=certain fraud)
- red_flags: Array of detected red flags
- risk_level: "low", "medium", "high"
- recommended_action: "approve", "investigate", "reject"
- confidence: Confidence in assessment"""

        user_prompt = f"""
Analyze fraud risk for this return:

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

            result = json.loads(response.content[0].text)

            if result.get('fraud_risk_score', 0) > 0.7:
                self.metrics.record_event("fraud.detected", {"risk_score": result['fraud_risk_score']})

            self.metrics.end_timer("agent.fraud_detection")
            return result

        except Exception as e:
            logger.error(f"Fraud detection agent error: {str(e)}")
            self.metrics.record_error("agent.fraud_detection", str(e))
            raise

    # =========================================================================
    # AGENT 6: RECOMMENDATION ENGINE
    # =========================================================================

    async def run_recommendation_engine(self, analysis_context: Dict) -> List[Dict]:
        """
        Generate 5-10 specific, actionable prevention recommendations
        """
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
1. Type: PRODUCT, SUPPLIER, LOGISTICS, MARKETING, CUSTOMER, or POLICY
2. Specific action (exact steps to implement)
3. Estimated impact (% return reduction)
4. Cost to implement ($)
5. ROI (return value / cost)
6. Timeline (days to implement)
7. Owner (which team)
8. Success metrics (how to measure)

Return JSON array of 5-10 recommendations sorted by impact."""

        user_prompt = f"""
Generate prevention recommendations based on this analysis:

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

            self.metrics.record_metric("recommendations.generated_count", len(recommendations) if isinstance(recommendations, list) else 1)
            self.metrics.end_timer("agent.recommendations")

            return recommendations if isinstance(recommendations, list) else [recommendations]

        except Exception as e:
            logger.error(f"Recommendation engine error: {str(e)}")
            self.metrics.record_error("agent.recommendations", str(e))
            raise

    # =========================================================================
    # AGENT 7: VALIDATION AGENT
    # =========================================================================

    async def run_validation_agent(self, recommendation: Dict) -> Dict:
        """
        Quality-gate recommendations before display
        Checks: confidence, evidence, no harmful output, factuality, fairness
        """
        self.metrics.start_timer("agent.validation")

        system_prompt = """You are a quality assurance specialist for AI recommendations. Validate before display.

Validation criteria:
1. Confidence: > 70%?
2. Evidence: Backed by supporting data (returns, metrics)?
3. Harmfulness: No recommendations that could harm customers/business?
4. Factuality: Statistics accurate? Sources real?
5. Fairness: Doesn't disproportionately impact one demographic?

Return JSON with:
- status: "approved" or "flagged"
- reasons: Array of validation reasons
- confidence_score: 0.0-1.0
- concerns: Array of any concerns
- recommended_human_review: boolean
- approval_summary: 1-2 sentence summary"""

        user_prompt = f"""
Validate this recommendation:

{json.dumps(recommendation, indent=2)}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=600,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )

            result = json.loads(response.content[0].text)

            self.metrics.end_timer("agent.validation")
            return result

        except Exception as e:
            logger.error(f"Validation agent error: {str(e)}")
            self.metrics.record_error("agent.validation", str(e))
            raise

    # =========================================================================
    # AGENT 8: EMOTIONAL INTELLIGENCE AGENT
    # =========================================================================

    async def run_emotional_intelligence_agent(self, return_data: Dict) -> Dict:
        """
        Analyze sentiment and emotional intensity
        EQ scoring: -5 to +5, intensity 1-5
        Churn risk: EQ < -3.0 triggers intervention
        """
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
- emotion: Emotion category
- intensity: 1-5
- churn_risk: boolean
- churn_risk_score: 0.0-1.0
- lifecycle_stage: pre-purchase, purchase, return, post-return
- intervention_needed: boolean
- suggested_intervention: Action to retain customer
- confidence: Confidence in assessment"""

        user_prompt = f"""
Analyze emotional intelligence from this return:

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

            result = json.loads(response.content[0].text)

            if result.get('churn_risk', False):
                self.metrics.record_event("churn_risk.detected", {"score": result.get('churn_risk_score', 0)})

            self.metrics.end_timer("agent.emotional_intelligence")
            return result

        except Exception as e:
            logger.error(f"Emotional intelligence agent error: {str(e)}")
            self.metrics.record_error("agent.emotional_intelligence", str(e))
            raise

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    def _aggregate_classifications(self, returns_data: List[Dict]) -> Dict:
        """Aggregate returns by classification"""
        agg = {}
        for ret in returns_data:
            cat = ret.get('classification', 'unknown')
            agg[cat] = agg.get(cat, 0) + 1
        return agg

    def _aggregate_products(self, returns_data: List[Dict]) -> Dict:
        """Aggregate returns by product"""
        agg = {}
        for ret in returns_data:
            sku = ret.get('product_id', 'unknown')
            agg[sku] = agg.get(sku, 0) + 1
        # Return top 10
        return dict(sorted(agg.items(), key=lambda x: x[1], reverse=True)[:10])

    def _aggregate_suppliers(self, returns_data: List[Dict]) -> Dict:
        """Aggregate returns by supplier"""
        agg = {}
        for ret in returns_data:
            supplier = ret.get('supplier_name', 'unknown')
            agg[supplier] = agg.get(supplier, 0) + 1
        return dict(sorted(agg.items(), key=lambda x: x[1], reverse=True)[:10])

    def check_llm_connectivity(self) -> bool:
        """Test LLM API connectivity"""
        try:
            self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "ping"}]
            )
            return True
        except:
            return False
