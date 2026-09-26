"""Database wrapper for ReturnIQ"""

from . import SessionLocal, engine, Base
from .models import Return, Classification, Trend, Recommendation, EmotionalIntelligence, AuditLog
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    """Database wrapper for ReturnIQ"""

    def __init__(self):
        self.session = SessionLocal()

    def connect(self):
        """Initialize database connection"""
        try:
            # Create tables if they don't exist
            Base.metadata.create_all(bind=engine)
            logger.info("Database connected and tables created")
        except Exception as e:
            logger.warning(f"Database connection not available (this is OK for testing): {type(e).__name__}")
            # Don't raise - allow app to start in demo mode

    def close(self):
        """Close database connection"""
        if self.session:
            self.session.close()

    def create_return(self, data: dict) -> str:
        """Create a new return"""
        try:
            return_obj = Return(**data)
            self.session.add(return_obj)
            self.session.commit()
            return str(return_obj.id)
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating return: {e}")
            raise

    def get_return(self, return_id: str):
        """Get a return by ID"""
        return self.session.query(Return).filter(Return.id == return_id).first()

    def list_returns(self, filters: dict = None, skip: int = 0, limit: int = 50):
        """List returns with optional filters"""
        query = self.session.query(Return)
        if filters:
            if 'status' in filters:
                query = query.filter(Return.status == filters['status'])
        return query.offset(skip).limit(limit).all()

    def count_returns(self, filters: dict = None) -> int:
        """Count returns matching filters"""
        query = self.session.query(Return)
        if filters:
            if 'status' in filters:
                query = query.filter(Return.status == filters['status'])
        return query.count()

    def create_classification(self, return_id: str, category: str, confidence: float, reasoning: str) -> str:
        """Create a classification"""
        try:
            classification = Classification(
                return_id=return_id,
                category=category,
                confidence=confidence,
                reasoning=reasoning
            )
            self.session.add(classification)
            self.session.commit()
            return str(classification.id)
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating classification: {e}")
            raise

    def get_classification(self, return_id: str):
        """Get classification for a return"""
        return self.session.query(Classification).filter(Classification.return_id == return_id).first()

    def get_emotional_intelligence(self, return_id: str):
        """Get emotional intelligence data for a return"""
        return self.session.query(EmotionalIntelligence).filter(EmotionalIntelligence.return_id == return_id).first()

    def get_recommendations_for_return(self, return_id: str):
        """Get recommendations for a return"""
        return self.session.query(Recommendation).filter(Recommendation.return_id == return_id).all()

    def flag_for_human_review(self, classification_id: str):
        """Flag a classification for human review"""
        classification = self.session.query(Classification).filter(Classification.id == classification_id).first()
        if classification:
            classification.flagged_for_review = True
            self.session.commit()

    def get_returns_since(self, start_date):
        """Get returns since a given date"""
        return self.session.query(Return).filter(Return.return_date >= start_date).all()

    def create_trend(self, title: str, description: str, returns_count: int, percentage_of_total: float, z_score: float, significance_level: str, evidence: str) -> str:
        """Create a trend"""
        try:
            trend = Trend(
                title=title,
                description=description,
                returns_count=returns_count,
                percentage_of_total=percentage_of_total,
                z_score=z_score,
                significance_level=significance_level,
                evidence=evidence
            )
            self.session.add(trend)
            self.session.commit()
            return str(trend.id)
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating trend: {e}")
            raise

    def get_top_trends(self, limit: int = 10, skip: int = 0):
        """Get top trends"""
        return self.session.query(Trend).order_by(Trend.z_score.desc()).offset(skip).limit(limit).all()

    def count_trends(self) -> int:
        """Count all trends"""
        return self.session.query(Trend).count()

    def get_trend(self, trend_id: str):
        """Get a trend by ID"""
        return self.session.query(Trend).filter(Trend.id == trend_id).first()

    def get_returns_by_ids(self, return_ids: list):
        """Get returns by a list of IDs"""
        if not return_ids:
            return []
        return self.session.query(Return).filter(Return.id.in_(return_ids)).all()

    def create_recommendation(self, trend_id: str = None, return_id: str = None, recommendation_text: str = None, recommendation_type: str = None, estimated_impact: float = None, confidence: float = None, evidence: str = None, validation_status: str = None, status: str = None) -> str:
        """Create a recommendation"""
        try:
            recommendation = Recommendation(
                trend_id=trend_id,
                return_id=return_id,
                recommendation_text=recommendation_text,
                recommendation_type=recommendation_type,
                estimated_impact=estimated_impact,
                confidence=confidence,
                evidence=evidence,
                validation_status=validation_status,
                status=status
            )
            self.session.add(recommendation)
            self.session.commit()
            return str(recommendation.id)
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating recommendation: {e}")
            raise

    def get_recommendations(self, status: str = None, skip: int = 0, limit: int = 20):
        """Get recommendations with optional status filter"""
        query = self.session.query(Recommendation)
        if status:
            query = query.filter(Recommendation.status == status)
        return query.offset(skip).limit(limit).all()

    def count_recommendations(self, status: str = None) -> int:
        """Count recommendations with optional status filter"""
        query = self.session.query(Recommendation)
        if status:
            query = query.filter(Recommendation.status == status)
        return query.count()

    def update_recommendation_status(self, rec_id: str, status: str = None, approval_date = None, implementation_date = None, actual_impact: float = None):
        """Update recommendation status"""
        recommendation = self.session.query(Recommendation).filter(Recommendation.id == rec_id).first()
        if recommendation:
            if status:
                recommendation.status = status
            if approval_date:
                recommendation.approval_date = approval_date
            if implementation_date:
                recommendation.implementation_date = implementation_date
            if actual_impact is not None:
                recommendation.actual_impact = actual_impact
            self.session.commit()

    def create_emotional_intelligence(self, return_id: str, sentiment_score: float = None, emotion: str = None, intensity: int = None, churn_risk: bool = False, churn_risk_score: float = None, lifecycle_stage: str = None) -> str:
        """Create emotional intelligence data"""
        try:
            ei = EmotionalIntelligence(
                return_id=return_id,
                sentiment_score=sentiment_score,
                emotion=emotion,
                intensity=intensity,
                churn_risk=churn_risk,
                churn_risk_score=churn_risk_score,
                lifecycle_stage=lifecycle_stage
            )
            self.session.add(ei)
            self.session.commit()
            return str(ei.id)
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error creating emotional intelligence: {e}")
            raise

    def flag_customer_for_intervention(self, customer_id: str, reason: str = None, churn_risk_score: float = None):
        """Flag a customer for intervention"""
        pass

    def get_customer_returns(self, customer_id: str):
        """Get all returns for a customer"""
        return self.session.query(Return).filter(Return.customer_id == customer_id).all()

    def get_customers_above_churn_risk(self, threshold: float, skip: int = 0, limit: int = 50):
        """Get customers above churn risk threshold"""
        results = self.session.query(Return.customer_id).join(
            EmotionalIntelligence, Return.id == EmotionalIntelligence.return_id
        ).filter(EmotionalIntelligence.churn_risk_score >= threshold).distinct().offset(skip).limit(limit).all()
        return [r[0] for r in results]

    def count_at_risk_customers(self, threshold: float) -> int:
        """Count customers above churn risk threshold"""
        return self.session.query(Return.customer_id).join(
            EmotionalIntelligence, Return.id == EmotionalIntelligence.return_id
        ).filter(EmotionalIntelligence.churn_risk_score >= threshold).distinct().count()

    def is_connected(self) -> bool:
        """Check if database is connected"""
        try:
            self.session.execute("SELECT 1")
            return True
        except Exception:
            return False

    def update_return_root_cause(self, return_id: str, root_cause: str):
        """Update return root cause"""
        return_obj = self.session.query(Return).filter(Return.id == return_id).first()
        if return_obj:
            return_obj.root_cause = root_cause
            self.session.commit()

    def update_return_status(self, return_id: str, status: str):
        """Update return status"""
        return_obj = self.session.query(Return).filter(Return.id == return_id).first()
        if return_obj:
            return_obj.status = status
            self.session.commit()

    def get_audit_logs(self, filters: dict = None, skip: int = 0, limit: int = 100):
        """Get audit logs with optional filters"""
        return []

    def count_audit_logs(self, filters: dict = None) -> int:
        """Count audit logs with optional filters"""
        return 0
