"""Understanding agent - analyzes individual returns."""

import random
from typing import List
from agents.models import (
    ReturnRecord, UnderstandingResult, SentimentType, ClassificationType
)


class UnderstandingAgent:
    """Analyzes individual returns for classification and insights."""

    def __init__(self):
        self.calls_total = 0
        self.calls_successful = 0
        self.total_latency_ms = 0.0

    def process_returns(self, returns: List[ReturnRecord]) -> List[UnderstandingResult]:
        """Analyze returns for understanding."""
        results = []
        self.calls_total += 1

        try:
            for ret in returns:
                result = self._analyze_return(ret)
                results.append(result)
            self.calls_successful += 1
        except Exception as e:
            print(f"Error in understanding agent: {e}")

        return results

    def _analyze_return(self, ret: ReturnRecord) -> UnderstandingResult:
        """Analyze a single return."""
        classification = self._classify_return(ret.reason)
        sentiment = self._analyze_sentiment(ret.reason)
        emotion_intensity = self._calculate_emotion(sentiment)
        churn_risk = self._assess_churn_risk(ret)
        confidence = self._calculate_confidence(ret.reason, classification)

        return UnderstandingResult(
            return_id=ret.return_id,
            classification=classification,
            confidence=confidence,
            sentiment=sentiment,
            emotion_intensity=emotion_intensity,
            churn_risk=churn_risk,
            risk_score=0.85 if churn_risk else 0.15,
        )

    def _classify_return(self, reason: str) -> ClassificationType:
        """Classify return reason."""
        reason_lower = reason.lower()

        if any(word in reason_lower for word in ["size", "fit", "too small", "too large"]):
            return ClassificationType.SIZE_FIT
        elif any(word in reason_lower for word in ["defect", "broken", "not work"]):
            return ClassificationType.DEFECTIVE
        elif any(word in reason_lower for word in ["wrong", "different", "mistake"]):
            return ClassificationType.WRONG_ITEM
        elif any(word in reason_lower for word in ["damage", "damaged", "torn", "ripped"]):
            return ClassificationType.DAMAGE
        elif any(word in reason_lower for word in ["quality", "poor", "bad"]):
            return ClassificationType.QUALITY_ISSUE
        elif any(word in reason_lower for word in ["changed", "mind", "don't", "don't want"]):
            return ClassificationType.CHANGE_MIND
        else:
            return ClassificationType.OTHER

    def _analyze_sentiment(self, reason: str) -> SentimentType:
        """Analyze sentiment from reason text."""
        negative_words = ["bad", "poor", "terrible", "awful", "hate", "broken", "defect", "damage"]
        positive_words = ["good", "great", "excellent", "love", "perfect"]

        reason_lower = reason.lower()
        negative_count = sum(1 for word in negative_words if word in reason_lower)
        positive_count = sum(1 for word in positive_words if word in reason_lower)

        if negative_count > positive_count:
            return SentimentType.NEGATIVE
        elif positive_count > negative_count:
            return SentimentType.POSITIVE
        else:
            return SentimentType.NEUTRAL

    def _calculate_emotion(self, sentiment: SentimentType) -> float:
        """Calculate emotion intensity (0-1)."""
        if sentiment == SentimentType.NEGATIVE:
            return random.uniform(0.6, 0.95)
        elif sentiment == SentimentType.POSITIVE:
            return random.uniform(0.3, 0.6)
        else:
            return random.uniform(0.2, 0.4)

    def _assess_churn_risk(self, ret: ReturnRecord) -> bool:
        """Assess if customer is at risk of churning."""
        risk_factors = 0

        if ret.is_fraud_suspect:
            risk_factors += 1

        if ret.refund_amount > 100:
            risk_factors += 1

        reason_lower = ret.reason.lower()
        if any(word in reason_lower for word in ["damage", "defect", "poor quality"]):
            risk_factors += 1

        return risk_factors >= 2 or random.random() < 0.15

    def _calculate_confidence(self, reason: str, classification: ClassificationType) -> float:
        """Calculate confidence score (0-1)."""
        confidence = 0.5

        if reason:
            confidence += 0.3

        if classification != ClassificationType.OTHER:
            confidence += 0.2

        return min(confidence, 0.99)

    @property
    def avg_latency_ms(self) -> float:
        """Calculate average latency."""
        if self.calls_total == 0:
            return 0.0
        return self.total_latency_ms / self.calls_total
