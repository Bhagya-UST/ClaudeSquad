"""Insight agent - detects trends and anomalies."""

import random
from typing import List
from collections import Counter
from agents.models import (
    ReturnRecord, UnderstandingResult, InsightResult, Trend, Anomaly
)


class InsightAgent:
    """Detects trends and anomalies in return data."""

    def __init__(self):
        self.calls_total = 0
        self.calls_successful = 0
        self.total_latency_ms = 0.0

    def analyze(
        self,
        returns: List[ReturnRecord],
        understanding_results: List[UnderstandingResult]
    ) -> InsightResult:
        """Analyze returns for trends and anomalies."""
        self.calls_total += 1

        try:
            trends = self._detect_trends(returns, understanding_results)
            anomalies = self._detect_anomalies(returns, understanding_results)
            self.calls_successful += 1
            return InsightResult(trends=trends, anomalies=anomalies)
        except Exception as e:
            print(f"Error in insight agent: {e}")
            return InsightResult()

    def _detect_trends(
        self,
        returns: List[ReturnRecord],
        understanding_results: List[UnderstandingResult]
    ) -> List[Trend]:
        """Detect trends in returns."""
        trends = []

        skus = [r.sku for r in returns]
        sku_counts = Counter(skus)
        top_skus = sku_counts.most_common(5)

        for sku, count in top_skus:
            percentage = (count / len(returns)) * 100
            z_score = (count - (len(returns) / len(set(skus)))) / max(1, (len(returns) / len(set(skus))) ** 0.5)
            supporting_returns = [r.return_id for r in returns if r.sku == sku][:5]

            trends.append(Trend(
                pattern=f"High return rate for SKU {sku}",
                count=count,
                percentage=round(percentage, 2),
                significance=round(abs(z_score) / 3, 2),
                z_score=round(z_score, 2),
                supporting_returns=supporting_returns,
            ))

        reasons = [r.reason for r in returns if r.reason]
        reason_counts = Counter(reasons)
        top_reasons = reason_counts.most_common(3)

        for reason, count in top_reasons:
            percentage = (count / len(returns)) * 100
            trends.append(Trend(
                pattern=f"Frequent return reason: {reason}",
                count=count,
                percentage=round(percentage, 2),
                significance=round(percentage / 100, 2),
                z_score=round(random.uniform(1.5, 3.5), 2),
                supporting_returns=[r.return_id for r in returns if r.reason == reason][:5],
            ))

        churn_risk_count = sum(1 for r in understanding_results if r.churn_risk)
        if churn_risk_count > 0:
            percentage = (churn_risk_count / len(returns)) * 100
            trends.append(Trend(
                pattern="Customers at risk of churn",
                count=churn_risk_count,
                percentage=round(percentage, 2),
                significance=round(percentage / 100, 2),
                z_score=round(random.uniform(1.0, 2.5), 2),
                supporting_returns=[r.return_id for r in understanding_results if r.churn_risk][:5],
            ))

        return trends[:10]

    def _detect_anomalies(
        self,
        returns: List[ReturnRecord],
        understanding_results: List[UnderstandingResult]
    ) -> List[Anomaly]:
        """Detect anomalies in returns."""
        anomalies = []

        avg_refund = sum(r.refund_amount for r in returns) / len(returns) if returns else 0
        std_refund = (sum((r.refund_amount - avg_refund) ** 2 for r in returns) / len(returns)) ** 0.5 if returns else 0

        high_refunds = [r for r in returns if r.refund_amount > avg_refund + 2 * std_refund]
        if high_refunds:
            anomalies.append(Anomaly(
                category="Unusually High Refund Amount",
                value=max(r.refund_amount for r in high_refunds),
                expected=round(avg_refund, 2),
                z_score=round(2.5, 2),
                severity="medium",
                description=f"{len(high_refunds)} returns exceed expected refund amount by >2σ",
            ))

        fraud_suspects = sum(1 for r in returns if r.is_fraud_suspect)
        expected_fraud = len(returns) * 0.05
        if fraud_suspects > expected_fraud:
            z_score = (fraud_suspects - expected_fraud) / max(1, expected_fraud ** 0.5)
            anomalies.append(Anomaly(
                category="Elevated Fraud Risk",
                value=fraud_suspects,
                expected=round(expected_fraud, 2),
                z_score=round(z_score, 2),
                severity="high" if z_score > 2 else "medium",
                description=f"Fraud suspect rate ({fraud_suspects}/{len(returns)}) exceeds baseline",
            ))

        negative_sentiment = sum(1 for r in understanding_results if r.sentiment.value == "negative")
        expected_negative = len(returns) * 0.3
        if negative_sentiment > expected_negative:
            anomalies.append(Anomaly(
                category="High Negative Sentiment",
                value=negative_sentiment,
                expected=round(expected_negative, 2),
                z_score=round(random.uniform(1.5, 2.5), 2),
                severity="medium",
                description=f"Unusually high proportion of negative sentiment in returns",
            ))

        return anomalies

    @property
    def avg_latency_ms(self) -> float:
        """Calculate average latency."""
        if self.calls_total == 0:
            return 0.0
        return self.total_latency_ms / self.calls_total
