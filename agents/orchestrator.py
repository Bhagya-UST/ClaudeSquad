"""ReturnIQ Orchestrator - coordinates all agents."""

from typing import List, Dict, Tuple
import pandas as pd

from agents.models import (
    ReturnRecord, UnderstandingResult, InsightResult, ActionResult,
    MetricsSnapshot, SystemMetrics
)
from agents.understanding import UnderstandingAgent
from agents.insight import InsightAgent
from agents.action_enhanced import EnhancedActionAgent
from agents.historical_store import HistoricalDataStore
from agents.rag_retriever import RAGRetriever


class ReturnIQOrchestrator:
    """Orchestrates the ReturnIQ analysis pipeline."""

    def __init__(self, mode: str = "demo"):
        self.mode = mode
        self.understanding_agent = UnderstandingAgent()
        self.insight_agent = InsightAgent()
        self.action_agent = EnhancedActionAgent()
        self.system_metrics = SystemMetrics()
        self.history_store = self.action_agent.history_store
        self.rag_retriever = self.action_agent.rag_retriever
        self.review_data = {}

    def process_returns(
        self,
        returns_df: pd.DataFrame
    ) -> Tuple[List[UnderstandingResult], InsightResult, ActionResult]:
        """Process returns through the full pipeline."""

        returns = self._dataframe_to_records(returns_df)

        understanding_results = self.understanding_agent.process_returns(returns)

        insight_result = self.insight_agent.analyze(returns, understanding_results)

        action_result, review_data = self.action_agent.generate_recommendations(
            returns, understanding_results, insight_result
        )

        self.review_data = review_data

        # Store analysis in history
        analysis_data = {
            "total_returns": len(returns),
            "churn_risks": sum(1 for r in understanding_results if r.churn_risk),
            "fraud_suspects": sum(1 for r in returns if r.is_fraud_suspect),
            "trends": [
                {
                    "pattern": t.pattern,
                    "count": t.count,
                    "percentage": t.percentage,
                    "significance": t.significance,
                } for t in insight_result.trends
            ],
            "anomalies": [
                {
                    "category": a.category,
                    "value": a.value,
                    "expected": a.expected,
                    "severity": a.severity,
                } for a in insight_result.anomalies
            ],
        }

        from datetime import datetime
        self.history_store.store_analysis(datetime.now().isoformat(), analysis_data)

        return understanding_results, insight_result, action_result

    def approve_recommendation(self, rec_id: str) -> bool:
        """Approve a recommendation."""
        return self.action_agent.approve_recommendation(rec_id)

    def reject_recommendation(self, rec_id: str) -> bool:
        """Reject a recommendation."""
        return self.action_agent.reject_recommendation(rec_id)

    def get_metrics_snapshot(self, total_returns: int) -> Dict:
        """Get metrics for all agents."""
        return {
            "understanding": MetricsSnapshot(
                calls_total=self.understanding_agent.calls_total,
                calls_successful=self.understanding_agent.calls_successful,
                avg_latency_ms=self.understanding_agent.avg_latency_ms,
            ),
            "insight": MetricsSnapshot(
                calls_total=self.insight_agent.calls_total,
                calls_successful=self.insight_agent.calls_successful,
                avg_latency_ms=self.insight_agent.avg_latency_ms,
            ),
            "action": MetricsSnapshot(
                calls_total=self.action_agent.calls_total,
                calls_successful=self.action_agent.calls_successful,
                avg_latency_ms=self.action_agent.avg_latency_ms,
            ),
            "system": SystemMetrics(
                hallucination_rate=0.0,
                confidence_violations=0,
            ),
        }

    def _dataframe_to_records(self, df: pd.DataFrame) -> List[ReturnRecord]:
        """Convert DataFrame to ReturnRecord objects."""
        records = []
        for _, row in df.iterrows():
            record = ReturnRecord(
                return_id=str(row.get("return_id", "")),
                sku=str(row.get("sku", "")),
                product_name=str(row.get("product_name", "")),
                customer_email=str(row.get("customer_email", "")),
                customer_phone=str(row.get("customer_phone", "")),
                reason=str(row.get("reason", "")),
                refund_amount=float(row.get("refund_amount", 0)),
                return_date=str(row.get("return_date", "")),
                is_fraud_suspect=bool(row.get("is_fraud_suspect", False)),
                sentiment_text=str(row.get("sentiment_text", "")) if "sentiment_text" in row else None,
            )
            records.append(record)
        return records
