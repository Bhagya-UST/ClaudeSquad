"""Database models for ReturnIQ - Multi-tenant SaaS"""

from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, JSON, Text, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from . import Base

# ============================================================================
# TENANT & USER MANAGEMENT
# ============================================================================

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    tenant_metadata = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    email = Column(String(255), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(50), default="analyst")
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_tenant_user_email"),)

class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    role = Column(String(50), nullable=False)
    permissions = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

# ============================================================================
# RETURN MANAGEMENT (Multi-tenant scoped)
# ============================================================================

class Return(Base):
    __tablename__ = "returns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    customer_id = Column(String(255), index=True)
    product_id = Column(String(255), index=True)
    order_date = Column(DateTime)
    return_date = Column(DateTime, index=True, default=datetime.utcnow)
    return_reason = Column(Text)
    customer_comments = Column(Text)
    product_condition = Column(String(50))
    refund_amount = Column(Float)
    status = Column(String(50), default="pending", index=True)
    root_cause = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (Index("ix_returns_tenant_date", "tenant_id", "return_date"),)

class Classification(Base):
    __tablename__ = "classifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    return_id = Column(UUID(as_uuid=True), ForeignKey("returns.id"), index=True)
    category = Column(String(100))
    confidence = Column(Float)
    reasoning = Column(Text)
    alternative_classifications = Column(JSON)
    confidence_factors = Column(JSON)
    agent_version = Column(String(50))
    flagged_for_review = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Trend(Base):
    __tablename__ = "trends"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    title = Column(String(255))
    description = Column(Text)
    returns_count = Column(Integer)
    percentage_of_total = Column(Float)
    z_score = Column(Float)
    significance_level = Column(String(20))
    evidence = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (Index("ix_trends_tenant_created", "tenant_id", "created_at"),)

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    return_id = Column(UUID(as_uuid=True), ForeignKey("returns.id"))
    trend_id = Column(UUID(as_uuid=True), ForeignKey("trends.id"))
    recommendation_text = Column(Text)
    recommendation_type = Column(String(100))
    estimated_impact = Column(Float)
    confidence = Column(Float)
    evidence = Column(JSON)
    roi_estimate = Column(Float)
    cost_estimate = Column(Float)
    status = Column(String(50), default="pending", index=True)
    validation_status = Column(String(50))
    approval_date = Column(DateTime)
    implementation_date = Column(DateTime)
    actual_impact = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (Index("ix_recommendations_tenant_status", "tenant_id", "status"),)

class RecommendationApproval(Base):
    __tablename__ = "recommendation_approvals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    recommendation_id = Column(UUID(as_uuid=True), ForeignKey("recommendations.id"), nullable=False)
    approved_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    status = Column(String(50), default="pending")
    reason = Column(String(500))
    notes = Column(Text)
    implementation_date = Column(DateTime)
    assigned_to_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class EmotionalIntelligence(Base):
    __tablename__ = "emotional_intelligence"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    return_id = Column(UUID(as_uuid=True), ForeignKey("returns.id"), index=True)
    customer_id = Column(String(255), index=True)
    sentiment_score = Column(Float)
    emotion = Column(String(50))
    intensity = Column(Integer)
    churn_risk = Column(Boolean, default=False)
    churn_risk_score = Column(Float)
    lifecycle_stage = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (Index("ix_ei_tenant_churn_risk", "tenant_id", "churn_risk_score"),)

class InterventionLog(Base):
    __tablename__ = "intervention_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    customer_id = Column(String(255), index=True)
    ei_analysis_id = Column(UUID(as_uuid=True), ForeignKey("emotional_intelligence.id"))
    intervention_type = Column(String(100))
    assigned_to_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    planned_date = Column(DateTime)
    executed_date = Column(DateTime)
    notes = Column(Text)
    outcome = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class MetricsLog(Base):
    __tablename__ = "metrics_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    metric_name = Column(String(255), index=True)
    metric_value = Column(Float)
    metric_type = Column(String(50))
    tags = Column(JSON)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)
    __table_args__ = (Index("ix_metrics_tenant_name_time", "tenant_id", "metric_name", "timestamp"),)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    action = Column(String(255), index=True)
    resource_type = Column(String(100))
    resource_id = Column(UUID(as_uuid=True))
    old_values = Column(JSON)
    new_values = Column(JSON)
    reason = Column(String(500))
    changes = Column(JSON)
    status = Column(String(50))
    error_message = Column(Text)
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    __table_args__ = (Index("ix_audit_tenant_timestamp", "tenant_id", "timestamp"),)
