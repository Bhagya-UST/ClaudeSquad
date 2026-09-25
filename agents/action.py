"""Action agent - generates recommendations."""

import random
from typing import List
from agents.models import (
    ReturnRecord, UnderstandingResult, InsightResult, ActionResult,
    Recommendation, PriorityLevel
)


class ActionAgent:
    """Generates actionable recommendations from analysis."""

    def __init__(self):
        self.calls_total = 0
        self.calls_successful = 0
        self.total_latency_ms = 0.0
        self.approved_recommendations = set()
        self.rejected_recommendations = set()

    def generate_recommendations(
        self,
        returns: List[ReturnRecord],
        understanding_results: List[UnderstandingResult],
        insight_result: InsightResult
    ) -> ActionResult:
        """Generate recommendations."""
        self.calls_total += 1

        try:
            recommendations = []

            for trend in insight_result.trends[:3]:
                rec = self._create_trend_recommendation(trend)
                recommendations.append(rec)

            for anomaly in insight_result.anomalies:
                rec = self._create_anomaly_recommendation(anomaly)
                recommendations.append(rec)

            churn_risks = [r for r in understanding_results if r.churn_risk]
            if churn_risks:
                rec = self._create_churn_prevention_recommendation(churn_risks)
                recommendations.append(rec)

            fraud_suspects = [r for r in returns if r.is_fraud_suspect]
            if fraud_suspects:
                rec = self._create_fraud_prevention_recommendation(fraud_suspects)
                recommendations.append(rec)

            self.calls_successful += 1
            return ActionResult(recommendations=recommendations[:10])
        except Exception as e:
            print(f"Error in action agent: {e}")
            return ActionResult()

    def _create_trend_recommendation(self, trend) -> Recommendation:
        """Create recommendation for a trend."""
        rec_id = f"REC_{random.randint(1000, 9999)}"
        return Recommendation(
            recommendation_id=rec_id,
            title=f"Address {trend.pattern}",
            description=f"Pattern detected in {trend.count} returns ({trend.percentage}% of total). "
                        f"Significance score: {trend.significance}. Investigate root cause and implement mitigation.",
            priority=PriorityLevel.HIGH if trend.significance > 0.5 else PriorityLevel.MEDIUM,
            confidence=min(trend.significance, 0.99),
            estimated_impact="5-15% reduction in returns",
            required_action="Review affected products and implement quality improvements or process changes",
            status="pending",
            human_review_required=trend.significance > 0.7,
        )

    def _create_anomaly_recommendation(self, anomaly) -> Recommendation:
        """Create recommendation for an anomaly."""
        rec_id = f"REC_{random.randint(1000, 9999)}"
        severity_priority = {
            "high": PriorityLevel.CRITICAL,
            "medium": PriorityLevel.HIGH,
            "low": PriorityLevel.MEDIUM,
        }
        return Recommendation(
            recommendation_id=rec_id,
            title=f"Investigate {anomaly.category}",
            description=f"Anomaly detected: {anomaly.description}. "
                        f"Current value: {anomaly.value}, Expected: {anomaly.expected}. "
                        f"Z-score: {anomaly.z_score}",
            priority=severity_priority.get(anomaly.severity, PriorityLevel.MEDIUM),
            confidence=abs(anomaly.z_score) / 3.5,
            estimated_impact="Prevent $10K-50K in losses" if anomaly.severity == "high" else "Prevent $1K-10K in losses",
            required_action="Conduct investigation and implement corrective action",
            status="pending",
            human_review_required=anomaly.severity in ["high", "medium"],
        )

    def _create_churn_prevention_recommendation(self, churn_risks) -> Recommendation:
        """Create recommendation for churn prevention."""
        rec_id = f"REC_{random.randint(1000, 9999)}"
        return Recommendation(
            recommendation_id=rec_id,
            title="Implement Churn Prevention Program",
            description=f"Identified {len(churn_risks)} customers at high churn risk based on return patterns. "
                        f"Recommend proactive outreach and retention offers.",
            priority=PriorityLevel.HIGH,
            confidence=0.85,
            estimated_impact="Retain 20-30% of at-risk customers",
            required_action="Launch targeted retention campaign with personalized offers",
            status="pending",
            human_review_required=True,
        )

    def _create_fraud_prevention_recommendation(self, fraud_suspects) -> Recommendation:
        """Create recommendation for fraud prevention."""
        rec_id = f"REC_{random.randint(1000, 9999)}"
        return Recommendation(
            recommendation_id=rec_id,
            title="Escalate Fraud Investigation",
            description=f"Flagged {len(fraud_suspects)} returns as potential fraud. "
                        f"Recommend review and possible action.",
            priority=PriorityLevel.CRITICAL,
            confidence=0.80,
            estimated_impact="Prevent $5K-20K in fraud losses",
            required_action="Manual review and potential account suspension",
            status="pending",
            human_review_required=True,
        )

    def approve_recommendation(self, rec_id: str) -> bool:
        """Approve a recommendation."""
        self.approved_recommendations.add(rec_id)
        return True

    def reject_recommendation(self, rec_id: str) -> bool:
        """Reject a recommendation."""
        self.rejected_recommendations.add(rec_id)
        return True

    @property
    def avg_latency_ms(self) -> float:
        """Calculate average latency."""
        if self.calls_total == 0:
            return 0.0
        return self.total_latency_ms / self.calls_total
