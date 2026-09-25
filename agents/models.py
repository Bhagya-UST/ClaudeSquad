"""ReturnIQ data models and schemas."""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class SentimentType(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class ClassificationType(str, Enum):
    DEFECTIVE = "defective"
    WRONG_ITEM = "wrong_item"
    SIZE_FIT = "size_fit"
    DAMAGE = "damage"
    CHANGE_MIND = "change_mind"
    QUALITY_ISSUE = "quality_issue"
    OTHER = "other"


class PriorityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class ReturnRecord:
    """Individual return record."""
    return_id: str
    sku: str
    product_name: str
    customer_email: str
    customer_phone: str
    reason: str
    refund_amount: float
    return_date: str
    is_fraud_suspect: bool = False
    sentiment_text: Optional[str] = None


@dataclass
class UnderstandingResult:
    """Individual return understanding."""
    return_id: str
    classification: ClassificationType
    confidence: float
    sentiment: SentimentType
    emotion_intensity: float
    churn_risk: bool
    risk_score: float = 0.0


@dataclass
class Trend:
    """Detected trend."""
    pattern: str
    count: int
    percentage: float
    significance: float
    z_score: float
    supporting_returns: List[str] = field(default_factory=list)


@dataclass
class Anomaly:
    """Detected anomaly."""
    category: str
    value: float
    expected: float
    z_score: float
    severity: str
    description: str


@dataclass
class InsightResult:
    """Analysis insights."""
    trends: List[Trend] = field(default_factory=list)
    anomalies: List[Anomaly] = field(default_factory=list)


@dataclass
class Recommendation:
    """Action recommendation."""
    recommendation_id: str
    title: str
    description: str
    priority: PriorityLevel
    confidence: float
    estimated_impact: str
    required_action: str
    status: str = "pending"
    human_review_required: bool = False


@dataclass
class ActionResult:
    """Action recommendations."""
    recommendations: List[Recommendation] = field(default_factory=list)


@dataclass
class MetricsSnapshot:
    """Metrics for an agent."""
    calls_total: int = 0
    calls_successful: int = 0
    avg_latency_ms: float = 0.0


@dataclass
class SystemMetrics:
    """System-level metrics."""
    hallucination_rate: float = 0.0
    confidence_violations: int = 0
