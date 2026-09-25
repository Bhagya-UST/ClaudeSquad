"""RAG Retriever - retrieves historical context for Claude."""

from typing import List, Dict, Optional
from agents.historical_store import HistoricalDataStore


class RAGRetriever:
    """Retrieves historical context for RAG-enhanced analysis."""

    def __init__(self, store: HistoricalDataStore):
        self.store = store

    def retrieve_context_for_trend(self, trend_pattern: str) -> str:
        """Retrieve historical context for a trend."""
        history = self.store.get_trend_history(trend_pattern)

        if not history:
            return f"No historical data found for pattern: {trend_pattern}"

        context_lines = [f"Historical occurrences of '{trend_pattern}':"]
        for i, record in enumerate(history[:5], 1):
            context_lines.append(
                f"{i}. {record['timestamp']}: {record['count']} returns "
                f"({record['percentage']}%, significance: {record['significance']})"
            )

        return "\n".join(context_lines)

    def retrieve_context_for_anomaly(self, anomaly_category: str) -> str:
        """Retrieve historical context for an anomaly."""
        history = self.store.get_anomaly_history(anomaly_category)

        if not history:
            return f"No historical data found for anomaly: {anomaly_category}"

        context_lines = [f"Historical occurrences of '{anomaly_category}':"]
        for i, record in enumerate(history[:5], 1):
            context_lines.append(
                f"{i}. {record['timestamp']}: value={record['value']}, "
                f"expected={record['expected']}, severity={record['severity']}"
            )

        return "\n".join(context_lines)

    def retrieve_similar_recommendations(self, recommendation_title: str) -> str:
        """Retrieve similar past recommendations."""
        similar = self.store.get_similar_recommendations(recommendation_title)

        if not similar:
            return "No similar past recommendations found."

        context_lines = ["Similar past recommendations:"]
        for rec in similar[:3]:
            status_emoji = "✅" if rec["status"] == "approved" else "⏳"
            context_lines.append(
                f"{status_emoji} {rec['title']} (Status: {rec['status']}, "
                f"Confidence: {rec['confidence']:.2f})"
            )
            if rec.get("reviewer_notes"):
                context_lines.append(f"   Notes: {rec['reviewer_notes']}")

        return "\n".join(context_lines)

    def retrieve_baseline_context(self) -> str:
        """Retrieve baseline metrics for comparison."""
        context = self.store.get_historical_context()

        lines = ["Historical Baseline Context:"]

        if context["total_analyses"] > 0:
            lines.append(f"- Analyzed {context['total_analyses']} datasets historically")
            lines.append(f"- Average churn risk rate: {context['avg_churn_risk']:.1f} customers")
            lines.append(f"- Average fraud suspects: {context['avg_fraud_suspects']:.1f} per analysis")

        if context["recurring_patterns"]:
            lines.append("\nRecurring patterns:")
            for pattern_info in context["recurring_patterns"][:3]:
                lines.append(
                    f"- '{pattern_info['pattern']}': "
                    f"occurred {pattern_info['occurrences']} times"
                )

        if context["critical_anomalies"]:
            lines.append("\nPast critical anomalies:")
            for anomaly in context["critical_anomalies"][:2]:
                lines.append(f"- {anomaly['category']} (value: {anomaly['value']})")

        return "\n".join(lines)

    def build_rag_context(
        self,
        trends: List[Dict],
        anomalies: List[Dict],
        recommendation_titles: List[str],
    ) -> str:
        """Build comprehensive RAG context for Claude."""
        context_parts = [
            "=== RAG CONTEXT FROM HISTORICAL DATA ===\n",
            self.retrieve_baseline_context(),
            "\n",
        ]

        for trend in trends[:2]:
            context_parts.append(
                "\n" + self.retrieve_context_for_trend(trend["pattern"])
            )

        for anomaly in anomalies[:2]:
            context_parts.append(
                "\n" + self.retrieve_context_for_anomaly(anomaly["category"])
            )

        for title in recommendation_titles[:2]:
            context_parts.append(
                "\n" + self.retrieve_similar_recommendations(title)
            )

        return "".join(context_parts)
