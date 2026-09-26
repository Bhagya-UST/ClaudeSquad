"""
Request/Response schemas for ReturnIQ API
Provides input validation and API documentation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

# ============================================================================
# Enums
# ============================================================================

class ReturnCategory(str, Enum):
    """Valid return categories"""
    SIZING = "sizing"
    QUALITY = "quality"
    DEFECTIVE = "defective"
    FRAUD = "fraud"
    LOGISTICS = "logistics"
    DUPLICATE = "duplicate"
    CHANGE_MIND = "change_mind"
    DAMAGED = "damaged"
    INCOMPATIBLE = "incompatible"
    OTHER = "other"

class RecommendationType(str, Enum):
    """Valid recommendation types"""
    PRODUCT = "product"
    SUPPLIER = "supplier"
    LOGISTICS = "logistics"
    MARKETING = "marketing"
    CUSTOMER = "customer"
    POLICY = "policy"

class RecommendationStatus(str, Enum):
    """Recommendation approval workflow"""
    PENDING = "pending"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"

# ============================================================================
# Request Schemas
# ============================================================================

class ReturnRequest(BaseModel):
    """Submit a return for analysis"""
    customer_id: str = Field(..., min_length=1, max_length=100)
    product_id: str = Field(..., min_length=1, max_length=100)
    product_name: str = Field(..., min_length=1, max_length=255)
    reason: str = Field(..., min_length=10, max_length=2000)
    customer_message: Optional[str] = Field(None, max_length=5000)

    @validator('customer_id', 'product_id')
    def ids_must_be_alphanumeric(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('must be alphanumeric with underscores and dashes only')
        return v

class ClassifyRequest(BaseModel):
    """Classify a return into categories"""
    return_id: str = Field(..., min_length=1, max_length=100)
    force_rerun: bool = False

class TrendDetectRequest(BaseModel):
    """Detect trends in returns"""
    metric: str = Field(..., min_length=1, max_length=100)
    period_days: int = Field(7, ge=1, le=365)
    threshold_sigma: float = Field(2.0, ge=1.0, le=5.0)

class RecommendationGenerateRequest(BaseModel):
    """Generate recommendations from trends"""
    trend_id: str = Field(..., min_length=1, max_length=100)
    min_confidence: float = Field(0.7, ge=0.0, le=1.0)

class RecommendationApproveRequest(BaseModel):
    """Approve a recommendation"""
    recommendation_id: str = Field(..., min_length=1, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)

class EmotionalIntelligenceRequest(BaseModel):
    """Analyze customer emotional intelligence"""
    return_id: str = Field(..., min_length=1, max_length=100)
    customer_message: str = Field(..., min_length=10, max_length=5000)

class ChatQueryRequest(BaseModel):
    """Customer care chat query"""
    customer_id: str = Field(..., min_length=1, max_length=100)
    query: str = Field(..., min_length=1, max_length=2000)
    conversation_history: Optional[List[Dict]] = None

class DashboardInsightsRequest(BaseModel):
    """Dashboard insights request"""
    customer_id: str = Field(..., min_length=1, max_length=100)
    user_query: str = Field(..., min_length=1, max_length=2000)
    dashboard_metrics: Optional[Dict] = None

# ============================================================================
# Response Schemas
# ============================================================================

class ClassificationResponse(BaseModel):
    """Classification result for a return"""
    return_id: str
    category: ReturnCategory
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    timestamp: datetime

class TrendResponse(BaseModel):
    """Detected trend"""
    trend_id: str
    metric: str
    z_score: float
    percentage_of_total: float
    significance_level: str  # "low", "medium", "high"
    detected_at: datetime

class RecommendationResponse(BaseModel):
    """Generated recommendation"""
    recommendation_id: str
    type: RecommendationType
    title: str
    description: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    status: RecommendationStatus
    estimated_impact: Optional[Dict] = None
    created_at: datetime

class ReturnResponse(BaseModel):
    """Full return analysis"""
    return_id: str
    customer_id: str
    product_id: str
    product_name: str
    classification: Optional[ClassificationResponse] = None
    status: str
    created_at: datetime
    updated_at: datetime

class DashboardMetricsResponse(BaseModel):
    """Dashboard metrics summary"""
    classification: Dict
    returns: Dict
    trends: Dict
    recommendations: Dict
    llm: Dict
    churn: Dict
    guardrails: Dict
    business_impact: Dict

class HealthCheckResponse(BaseModel):
    """Health check status"""
    status: str
    timestamp: datetime
    checks: Dict[str, str]

class ErrorResponse(BaseModel):
    """Standard error response"""
    error_code: str
    message: str
    details: Optional[Dict] = None
    timestamp: datetime

class PaginatedResponse(BaseModel):
    """Paginated list response"""
    items: List
    total: int
    page: int
    page_size: int
    has_more: bool
