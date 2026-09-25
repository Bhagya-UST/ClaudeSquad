"""Historical data storage and retrieval for trend analysis."""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class HistoricalDataStore:
    """Stores and retrieves historical analysis results for RAG."""

    def __init__(self, storage_dir: str = "/tmp/returniq_history"):
        self.storage_dir = storage_dir
        Path(storage_dir).mkdir(parents=True, exist_ok=True)
        self.analysis_log = os.path.join(storage_dir, "analysis_log.jsonl")
        self.patterns_db = os.path.join(storage_dir, "patterns.json")
        self.recommendations_log = os.path.join(storage_dir, "recommendations.jsonl")

    def store_analysis(self, timestamp: str, analysis_data: Dict) -> None:
        """Store a complete analysis result."""
        entry = {
            "timestamp": timestamp,
            "total_returns": analysis_data.get("total_returns", 0),
            "churn_risks": analysis_data.get("churn_risks", 0),
            "fraud_suspects": analysis_data.get("fraud_suspects", 0),
            "trends": analysis_data.get("trends", []),
            "anomalies": analysis_data.get("anomalies", []),
        }

        with open(self.analysis_log, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def store_recommendation(
        self,
        rec_id: str,
        title: str,
        priority: str,
        confidence: float,
        supporting_records: List[str],
        status: str = "pending",
        human_review_required: bool = False,
        reviewer_notes: Optional[str] = None,
    ) -> None:
        """Store recommendation for audit trail."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "rec_id": rec_id,
            "title": title,
            "priority": priority,
            "confidence": confidence,
            "supporting_records": supporting_records,
            "status": status,
            "human_review_required": human_review_required,
            "reviewer_notes": reviewer_notes,
        }

        with open(self.recommendations_log, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def get_trend_history(self, pattern: str, days: int = 30) -> List[Dict]:
        """Retrieve historical occurrences of a trend pattern."""
        trends = []

        if not os.path.exists(self.analysis_log):
            return trends

        with open(self.analysis_log, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    for trend in entry.get("trends", []):
                        if pattern.lower() in trend.get("pattern", "").lower():
                            trends.append({
                                "timestamp": entry["timestamp"],
                                "pattern": trend["pattern"],
                                "count": trend.get("count", 0),
                                "percentage": trend.get("percentage", 0),
                                "significance": trend.get("significance", 0),
                            })
                except json.JSONDecodeError:
                    continue

        return sorted(trends, key=lambda x: x["timestamp"], reverse=True)[:10]

    def get_anomaly_history(self, category: str) -> List[Dict]:
        """Retrieve historical anomalies by category."""
        anomalies = []

        if not os.path.exists(self.analysis_log):
            return anomalies

        with open(self.analysis_log, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    for anomaly in entry.get("anomalies", []):
                        if category.lower() in anomaly.get("category", "").lower():
                            anomalies.append({
                                "timestamp": entry["timestamp"],
                                "category": anomaly["category"],
                                "value": anomaly.get("value", 0),
                                "expected": anomaly.get("expected", 0),
                                "severity": anomaly.get("severity", "low"),
                            })
                except json.JSONDecodeError:
                    continue

        return sorted(anomalies, key=lambda x: x["timestamp"], reverse=True)[:10]

    def get_similar_recommendations(self, title: str, limit: int = 5) -> List[Dict]:
        """Retrieve similar past recommendations."""
        similar = []

        if not os.path.exists(self.recommendations_log):
            return similar

        with open(self.recommendations_log, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if any(word in entry["title"].lower() for word in title.lower().split()):
                        similar.append(entry)
                except json.JSONDecodeError:
                    continue

        return sorted(similar, key=lambda x: x["timestamp"], reverse=True)[:limit]

    def get_historical_context(self) -> Dict:
        """Get comprehensive historical context for RAG."""
        context = {
            "total_analyses": 0,
            "avg_churn_risk": 0,
            "avg_fraud_suspects": 0,
            "recurring_patterns": [],
            "critical_anomalies": [],
        }

        if not os.path.exists(self.analysis_log):
            return context

        analyses = []
        all_patterns = {}
        critical_anomalies = []

        with open(self.analysis_log, "r") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    analyses.append(entry)

                    for trend in entry.get("trends", []):
                        pattern = trend["pattern"]
                        if pattern not in all_patterns:
                            all_patterns[pattern] = []
                        all_patterns[pattern].append(trend)

                    for anomaly in entry.get("anomalies", []):
                        if anomaly.get("severity") == "high":
                            critical_anomalies.append(anomaly)
                except json.JSONDecodeError:
                    continue

        if analyses:
            context["total_analyses"] = len(analyses)
            churn_risks = [a.get("churn_risks", 0) for a in analyses]
            fraud_suspects = [a.get("fraud_suspects", 0) for a in analyses]
            context["avg_churn_risk"] = sum(churn_risks) / len(churn_risks)
            context["avg_fraud_suspects"] = sum(fraud_suspects) / len(fraud_suspects)

        context["recurring_patterns"] = [
            {"pattern": p, "occurrences": len(v)} for p, v in all_patterns.items()
        ]

        context["critical_anomalies"] = critical_anomalies[-5:]

        return context

    def generate_sample_history(self) -> None:
        """Generate sample historical data for demo."""
        sample_analyses = [
            {
                "timestamp": "2026-09-20T10:00:00",
                "total_returns": 145,
                "churn_risks": 22,
                "fraud_suspects": 9,
                "trends": [
                    {
                        "pattern": "High return rate for SKU SKU-101",
                        "count": 18,
                        "percentage": 12.4,
                        "significance": 0.85,
                    },
                    {
                        "pattern": "Frequent return reason: Size too large",
                        "count": 32,
                        "percentage": 22.1,
                        "significance": 0.92,
                    },
                ],
                "anomalies": [
                    {
                        "category": "Elevated Fraud Risk",
                        "value": 9,
                        "expected": 7.2,
                        "severity": "high",
                    }
                ],
            },
            {
                "timestamp": "2026-09-22T14:30:00",
                "total_returns": 158,
                "churn_risks": 28,
                "fraud_suspects": 12,
                "trends": [
                    {
                        "pattern": "High return rate for SKU SKU-101",
                        "count": 21,
                        "percentage": 13.3,
                        "significance": 0.88,
                    },
                    {
                        "pattern": "Customers at risk of churn",
                        "count": 28,
                        "percentage": 17.7,
                        "significance": 0.79,
                    },
                ],
                "anomalies": [
                    {
                        "category": "High Negative Sentiment",
                        "value": 52,
                        "expected": 47,
                        "severity": "medium",
                    }
                ],
            },
        ]

        for analysis in sample_analyses:
            self.store_analysis(analysis["timestamp"], analysis)

        sample_recs = [
            (
                "REC_2026_001",
                "Address High return rate for SKU SKU-101",
                "high",
                0.88,
                ["RET100000", "RET100001", "RET100002"],
                "approved",
                False,
                "Approved - Quality investigation initiated",
            ),
            (
                "REC_2026_002",
                "Implement Churn Prevention Program",
                "high",
                0.85,
                ["RET100010", "RET100015", "RET100020"],
                "pending_review",
                True,
                None,
            ),
        ]

        for rec in sample_recs:
            self.store_recommendation(*rec)
