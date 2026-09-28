"""
Human Review Agent - Agent 8 of 8
Handles escalation and user feedback
"""

import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class HumanReviewAgent:
    """Manages human review and escalation"""

    def __init__(self, metrics_collector=None):
        self.metrics = metrics_collector
        self.escalations = []

    async def escalate(self, item_id: str, reason: str, priority: str = "medium") -> Dict:
        """Escalate item for human review"""
        if self.metrics:
            self.metrics.start_timer("agent.human_review")

        escalation = {
            "escalation_id": f"ESC_{datetime.now().timestamp()}",
            "item_id": item_id,
            "reason": reason,
            "priority": priority,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "assigned_to": None,
            "reviewed_at": None,
            "reviewer_notes": None
        }

        self.escalations.append(escalation)

        if self.metrics:
            self.metrics.record_event("escalation.created", {
                "escalation_id": escalation["escalation_id"],
                "priority": priority
            })
            self.metrics.end_timer("agent.human_review")

        logger.info(f"Escalation created: {escalation['escalation_id']} - {reason}")
        return escalation

    async def record_review(self, escalation_id: str, notes: str, approved: bool, reviewer_id: str) -> Dict:
        """Record human review decision"""
        escalation = next((e for e in self.escalations if e["escalation_id"] == escalation_id), None)

        if not escalation:
            raise ValueError(f"Escalation {escalation_id} not found")

        escalation["status"] = "approved" if approved else "rejected"
        escalation["reviewed_at"] = datetime.now().isoformat()
        escalation["reviewer_notes"] = notes
        escalation["assigned_to"] = reviewer_id

        if self.metrics:
            self.metrics.record_event("review.completed", {
                "escalation_id": escalation_id,
                "approved": approved
            })

        logger.info(f"Review completed for {escalation_id}: {approved}")
        return escalation

    def get_pending_escalations(self) -> list:
        """Get all pending escalations"""
        return [e for e in self.escalations if e["status"] == "pending"]

    def get_escalation(self, escalation_id: str) -> Optional[Dict]:
        """Get specific escalation"""
        return next((e for e in self.escalations if e["escalation_id"] == escalation_id), None)
