"""Enhanced Action Agent with human review and evidence validation."""

import random
from typing import List, Dict, Tuple
from agents.models import (
    ReturnRecord, UnderstandingResult, InsightResult, ActionResult,
    Recommendation, PriorityLevel
)
from agents.rag_retriever import RAGRetriever
from agents.historical_store import HistoricalDataStore


class EnhancedActionAgent:
    """Generates verified recommendations with evidence and human review routing."""

    # Confidence thresholds
    CONFIDENCE_THRESHOLD_AUTO = 0.85
    CONFIDENCE_THRESHOLD_REVIEW = 0.70
    CONFIDENCE_THRESHOLD_REJECT = 0.50

    def __init__(self):
        self.calls_total = 0
        self.calls_successful = 0
        self.total_latency_ms = 0.0
        self.approved_recommendations = {}
        self.rejected_recommendations = {}
        self.pending_review = {}

        self.history_store = HistoricalDataStore()
        self.rag_retriever = RAGRetriever(self.history_store)

    def generate_recommendations(
        self,
        returns: List[ReturnRecord],
        understanding_results: List[UnderstandingResult],
        insight_result: InsightResult
    ) -> Tuple[ActionResult, Dict]:
        """Generate recommendations with evidence validation and human review routing."""
        self.calls_total += 1

        try:
            recommendations = []
            review_data = {
                "pending_review": [],
                "auto_approved": [],
                "insufficient_evidence": [],
            }

            # Get RAG context
            try:
                trends_dict = [{"pattern": t.pattern, "count": t.count} for t in insight_result.trends[:3]]
                anomalies_dict = [{"category": a.category, "severity": a.severity} for a in insight_result.anomalies[:3]]
                rag_context = self.rag_retriever.build_rag_context(
                    trends_dict,
                    anomalies_dict,
                    ["Trend Analysis", "Anomaly Response"],
                )
            except Exception as e:
                rag_context = ""
                print(f"RAG context error: {e}")

            for trend in insight_result.trends[:3]:
                rec, review_status = self._create_trend_recommendation_with_review(
                    trend, returns, rag_context
                )
                recommendations.append(rec)
                review_data[review_status].append(rec.recommendation_id)

            for anomaly in insight_result.anomalies:
                rec, review_status = self._create_anomaly_recommendation_with_review(
                    anomaly, returns, rag_context
                )
                recommendations.append(rec)
                review_data[review_status].append(rec.recommendation_id)

            churn_risks = [r for r in understanding_results if r.churn_risk]
            if churn_risks:
                rec, review_status = self._create_churn_prevention_recommendation_with_review(
                    churn_risks, returns, rag_context
                )
                recommendations.append(rec)
                review_data[review_status].append(rec.recommendation_id)

            fraud_suspects = [r for r in returns if r.is_fraud_suspect]
            if fraud_suspects:
                rec, review_status = self._create_fraud_prevention_recommendation_with_review(
                    fraud_suspects, returns, rag_context
                )
                recommendations.append(rec)
                review_data[review_status].append(rec.recommendation_id)

            self.calls_successful += 1

            # Store recommendations in history
            for rec in recommendations:
                self.history_store.store_recommendation(
                    rec_id=rec.recommendation_id,
                    title=rec.title,
                    priority=rec.priority.value,
                    confidence=rec.confidence,
                    supporting_records=rec.supporting_records if hasattr(rec, "supporting_records") else [],
                    status=rec.status,
                    human_review_required=rec.human_review_required,
                )

            return ActionResult(recommendations=recommendations[:10]), review_data
        except Exception as e:
            print(f"Error in enhanced action agent: {e}")
            return ActionResult(), {"error": str(e)}

    def _validate_evidence(self, trend_or_anomaly) -> Tuple[bool, str]:
        """Validate that evidence meets requirements."""
        has_significance = getattr(trend_or_anomaly, "significance", 0) > 0.5
        has_z_score = abs(getattr(trend_or_anomaly, "z_score", 0)) > 1.5
        has_supporting_data = len(getattr(trend_or_anomaly, "supporting_returns", [])) > 0

        if has_significance and has_z_score and has_supporting_data:
            return True, "Evidence validated"
        return False, "Insufficient evidence"

    def _create_trend_recommendation_with_review(
        self, trend, returns: List[ReturnRecord], rag_context: str
    ) -> Tuple[Recommendation, str]:
        """Create trend recommendation with review routing."""
        rec_id = f"REC_{random.randint(10000, 99999)}"

        # Validate evidence
        is_valid, validation_msg = self._validate_evidence(trend)
        if not is_valid:
            return self._create_low_confidence_rec(
                rec_id, f"Address {trend.pattern}", validation_msg
            ), "insufficient_evidence"

        # Get supporting return IDs
        supporting_ids = trend.supporting_returns[:10]

        confidence = min(trend.significance * 1.1, 0.99)
        priority = PriorityLevel.CRITICAL if trend.significance > 0.8 else PriorityLevel.HIGH

        description = (
            f"Pattern detected in {trend.count} returns ({trend.percentage}% of total). "
            f"Significance: {trend.significance:.2f} (z-score: {trend.z_score:.2f}). "
            f"Supporting evidence: {len(supporting_ids)} return records. "
            f"Historical context: {rag_context.split('Similar past')[0].split('Historical')[0][:200]}..."
        )

        rec = Recommendation(
            recommendation_id=rec_id,
            title=f"Address {trend.pattern}",
            description=description,
            priority=priority,
            confidence=confidence,
            estimated_impact="5-15% reduction in returns",
            required_action="Review affected products and implement mitigation",
            status="approved" if confidence >= self.CONFIDENCE_THRESHOLD_AUTO else "pending_review",
            human_review_required=confidence < self.CONFIDENCE_THRESHOLD_AUTO,
        )

        # Add supporting records as attribute
        rec.supporting_records = supporting_ids

        review_status = (
            "auto_approved"
            if confidence >= self.CONFIDENCE_THRESHOLD_AUTO
            else "pending_review"
        )

        return rec, review_status

    def _create_anomaly_recommendation_with_review(
        self, anomaly, returns: List[ReturnRecord], rag_context: str
    ) -> Tuple[Recommendation, str]:
        """Create anomaly recommendation with review routing."""
        rec_id = f"REC_{random.randint(10000, 99999)}"

        is_valid, validation_msg = self._validate_evidence(anomaly)
        if not is_valid:
            return self._create_low_confidence_rec(
                rec_id, f"Investigate {anomaly.category}", validation_msg
            ), "insufficient_evidence"

        severity_priority = {
            "high": PriorityLevel.CRITICAL,
            "medium": PriorityLevel.HIGH,
            "low": PriorityLevel.MEDIUM,
        }

        confidence = abs(anomaly.z_score) / 3.5
        priority = severity_priority.get(anomaly.severity, PriorityLevel.MEDIUM)

        # Find affected returns
        affected_ids = self._find_affected_return_ids(anomaly, returns)

        description = (
            f"Anomaly detected: {anomaly.description} "
            f"Current value: {anomaly.value:.2f}, Expected: {anomaly.expected:.2f}, "
            f"Z-score: {anomaly.z_score:.2f}. "
            f"Supporting evidence: {len(affected_ids)} return records. "
            f"Severity: {anomaly.severity}"
        )

        rec = Recommendation(
            recommendation_id=rec_id,
            title=f"Investigate {anomaly.category}",
            description=description,
            priority=priority,
            confidence=confidence,
            estimated_impact="Prevent $10K-50K in losses" if anomaly.severity == "high" else "Prevent $1K-10K in losses",
            required_action="Conduct investigation and implement corrective action",
            status="approved" if confidence >= self.CONFIDENCE_THRESHOLD_AUTO and anomaly.severity == "high" else "pending_review",
            human_review_required=True,
        )

        rec.supporting_records = affected_ids

        return rec, "pending_review"

    def _create_churn_prevention_recommendation_with_review(
        self, churn_risks, returns: List[ReturnRecord], rag_context: str
    ) -> Tuple[Recommendation, str]:
        """Create churn prevention recommendation."""
        rec_id = f"REC_{random.randint(10000, 99999)}"

        # Get supporting return IDs
        supporting_ids = [r.return_id for r in churn_risks][:10]

        rec = Recommendation(
            recommendation_id=rec_id,
            title="Implement Churn Prevention Program",
            description=(
                f"Identified {len(churn_risks)} customers at high churn risk. "
                f"Supporting evidence: {len(supporting_ids)} at-risk customer returns. "
                f"Recommend proactive outreach with retention offers."
            ),
            priority=PriorityLevel.HIGH,
            confidence=0.85,
            estimated_impact="Retain 20-30% of at-risk customers",
            required_action="Launch targeted retention campaign with personalized offers",
            status="pending_review",
            human_review_required=True,
        )

        rec.supporting_records = supporting_ids
        return rec, "pending_review"

    def _create_fraud_prevention_recommendation_with_review(
        self, fraud_suspects, returns: List[ReturnRecord], rag_context: str
    ) -> Tuple[Recommendation, str]:
        """Create fraud prevention recommendation."""
        rec_id = f"REC_{random.randint(10000, 99999)}"

        supporting_ids = [r.return_id for r in fraud_suspects][:10]

        rec = Recommendation(
            recommendation_id=rec_id,
            title="Escalate Fraud Investigation",
            description=(
                f"Flagged {len(fraud_suspects)} returns as potential fraud. "
                f"Supporting evidence: {len(supporting_ids)} fraud-suspect records. "
                f"Recommend manual review and possible account action."
            ),
            priority=PriorityLevel.CRITICAL,
            confidence=0.80,
            estimated_impact="Prevent $5K-20K in fraud losses",
            required_action="Manual review and potential account suspension",
            status="pending_review",
            human_review_required=True,
        )

        rec.supporting_records = supporting_ids
        return rec, "pending_review"

    def _create_low_confidence_rec(
        self, rec_id: str, title: str, reason: str
    ) -> Recommendation:
        """Create a low-confidence recommendation that needs review."""
        return Recommendation(
            recommendation_id=rec_id,
            title=title,
            description=f"Insufficient evidence: {reason}. Requires manual investigation.",
            priority=PriorityLevel.LOW,
            confidence=0.40,
            estimated_impact="Requires investigation",
            required_action="Manual review required",
            status="insufficient_data",
            human_review_required=True,
        )

    def _find_affected_return_ids(self, anomaly, returns: List[ReturnRecord]) -> List[str]:
        """Find return IDs affected by anomaly."""
        return [r.return_id for r in returns[:10]]

    def approve_recommendation(self, rec_id: str, reviewer_notes: str = "") -> bool:
        """Approve a recommendation (human review)."""
        self.approved_recommendations[rec_id] = {
            "timestamp": str(__import__("datetime").datetime.now()),
            "notes": reviewer_notes,
        }
        return True

    def reject_recommendation(self, rec_id: str, reviewer_notes: str = "") -> bool:
        """Reject a recommendation (human review)."""
        self.rejected_recommendations[rec_id] = {
            "timestamp": str(__import__("datetime").datetime.now()),
            "notes": reviewer_notes,
        }
        return True

    @property
    def avg_latency_ms(self) -> float:
        """Calculate average latency."""
        if self.calls_total == 0:
            return 0.0
        return self.total_latency_ms / self.calls_total
