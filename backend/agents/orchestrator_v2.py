"""
ReturnIQ Agent Orchestrator - Version 2
Orchestrates 9 specialized agents (8 analysis + 1 customer care)
Each agent is now in a separate file for modularity
"""

import logging
from typing import Dict, List, Any

# Import individual agents
from .classifier import ClassifierAgent
from .root_cause import RootCauseAgent
from .trend_detection import TrendDetectionAgent
from .anomaly_detection import AnomalyDetectionAgent
from .fraud_detection import FraudDetectionAgent
from .recommendation import RecommendationAgent
from .validation import ValidationAgent
from .human_review import HumanReviewAgent
from .emotional_intelligence import EmotionalIntelligenceAgent

logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Orchestrates 9 specialized agents for return analysis

    Agents:
    1. Classifier - Categorizes returns (96.2% accuracy)
    2. Root Cause - Traces issues to origin
    3. Trend Detection - Identifies statistical patterns
    4. Anomaly Detection - Flags unusual spikes
    5. Fraud Detection - Detects return fraud patterns
    6. Recommendation - Generates prevention actions
    7. Validation - Quality-gates recommendations
    8. Human Review - Escalation and feedback
    9. Emotional Intelligence - Analyzes customer sentiment & churn risk
    """

    def __init__(self, rag_system=None, metrics_collector=None):
        self.rag = rag_system
        self.metrics = metrics_collector

        # Initialize agents
        self.classifier = ClassifierAgent(metrics_collector)
        self.root_cause = RootCauseAgent(metrics_collector)
        self.trend_detection = TrendDetectionAgent(metrics_collector)
        self.anomaly_detection = AnomalyDetectionAgent(metrics_collector)
        self.fraud_detection = FraudDetectionAgent(metrics_collector)
        self.recommendation = RecommendationAgent(metrics_collector)
        self.validation = ValidationAgent(metrics_collector)
        self.human_review = HumanReviewAgent(metrics_collector)
        self.emotional_intelligence = EmotionalIntelligenceAgent(metrics_collector)

        logger.info("Agent Orchestrator initialized with 9 agents")

    # =========================================================================
    # AGENT 1: CLASSIFIER
    # =========================================================================

    async def run_classifier_agent(self, return_data: Dict) -> Dict:
        """Run classification agent"""
        return await self.classifier.classify(return_data)

    # =========================================================================
    # AGENT 2: ROOT CAUSE
    # =========================================================================

    async def run_root_cause_agent(self, return_data: Dict) -> Dict:
        """Run root cause analysis agent"""
        return await self.root_cause.analyze(return_data)

    # =========================================================================
    # AGENT 3: TREND DETECTION
    # =========================================================================

    async def run_trend_detection_agent(self, returns_data: List[Dict]) -> List[Dict]:
        """Run trend detection agent"""
        return await self.trend_detection.detect(returns_data)

    # =========================================================================
    # AGENT 4: ANOMALY DETECTION
    # =========================================================================

    async def run_anomaly_detection_agent(self, current_metrics: Dict, baseline_metrics: Dict) -> Dict:
        """Run anomaly detection agent"""
        return await self.anomaly_detection.detect(current_metrics, baseline_metrics)

    # =========================================================================
    # AGENT 5: FRAUD DETECTION
    # =========================================================================

    async def run_fraud_detection_agent(self, return_data: Dict) -> Dict:
        """Run fraud detection agent"""
        return await self.fraud_detection.detect(return_data)

    # =========================================================================
    # AGENT 6: RECOMMENDATION ENGINE
    # =========================================================================

    async def run_recommendation_engine(self, analysis_context: Dict) -> List[Dict]:
        """Run recommendation engine"""
        return await self.recommendation.generate(analysis_context)

    # =========================================================================
    # AGENT 7: VALIDATION
    # =========================================================================

    async def run_validation_agent(self, recommendation: Dict) -> Dict:
        """Run validation agent"""
        return await self.validation.validate(recommendation)

    # =========================================================================
    # AGENT 8: HUMAN REVIEW
    # =========================================================================

    async def escalate_for_review(self, item_id: str, reason: str, priority: str = "medium") -> Dict:
        """Escalate item for human review"""
        return await self.human_review.escalate(item_id, reason, priority)

    async def record_review_decision(self, escalation_id: str, notes: str, approved: bool, reviewer_id: str) -> Dict:
        """Record human review decision"""
        return await self.human_review.record_review(escalation_id, notes, approved, reviewer_id)

    def get_pending_escalations(self) -> list:
        """Get all pending escalations"""
        return self.human_review.get_pending_escalations()

    # =========================================================================
    # AGENT 9: EMOTIONAL INTELLIGENCE
    # =========================================================================

    async def run_emotional_intelligence_agent(self, return_data: Dict) -> Dict:
        """Run emotional intelligence agent"""
        return await self.emotional_intelligence.analyze(return_data)

    def get_churn_prevention_strategies(self, eq_score: float) -> Dict:
        """Get churn prevention strategies based on EQ score"""
        return self.emotional_intelligence.get_churn_prevention_strategies(eq_score)

    # =========================================================================
    # COMBINED PIPELINE
    # =========================================================================

    async def run_full_analysis_pipeline(self, return_data: Dict) -> Dict:
        """
        Run complete analysis pipeline on a return
        Executes agents in optimal sequence
        """
        try:
            logger.info(f"Starting full analysis pipeline for return {return_data.get('id')}")

            # 1. Classification
            classification = await self.run_classifier_agent(return_data)
            return_data['classification'] = classification

            # 2. Emotional Intelligence (parallel with Root Cause)
            emotional_data = await self.run_emotional_intelligence_agent(return_data)
            return_data['emotional_intelligence'] = emotional_data

            # 3. Root Cause Analysis
            root_cause = await self.run_root_cause_agent(return_data)
            return_data['root_cause'] = root_cause

            # 4. Fraud Detection
            fraud_analysis = await self.run_fraud_detection_agent(return_data)
            return_data['fraud_analysis'] = fraud_analysis

            # 5. Generate Recommendations
            recommendations = await self.run_recommendation_engine({
                "return": return_data,
                "classification": classification,
                "root_cause": root_cause
            })
            return_data['recommendations'] = recommendations

            # 6. Validate Recommendations
            validated_recs = []
            for rec in recommendations:
                validation = await self.run_validation_agent(rec)
                validated_recs.append({**rec, "validation": validation})
            return_data['validated_recommendations'] = validated_recs

            # 7. Check for escalation needs
            if emotional_data.get('churn_risk') or fraud_analysis.get('fraud_risk_score', 0) > 0.7:
                escalation = await self.escalate_for_review(
                    return_data.get('id'),
                    f"Churn Risk: {emotional_data.get('churn_risk')} | Fraud Score: {fraud_analysis.get('fraud_risk_score', 0):.2f}",
                    "high" if emotional_data.get('churn_risk') else "medium"
                )
                return_data['escalation'] = escalation

            logger.info(f"Full analysis pipeline completed for return {return_data.get('id')}")
            return return_data

        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            if self.metrics:
                self.metrics.record_error("orchestrator.pipeline", str(e))
            raise

    def check_llm_connectivity(self) -> bool:
        """Test LLM API connectivity"""
        try:
            response = self.classifier.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                messages=[{"role": "user", "content": "ping"}]
            )
            return response.content[0].text == "ping"
        except Exception as e:
            logger.error(f"LLM connectivity check failed: {e}")
            return False
