"""
Emotional Intelligence Routes
API endpoints for emotional intelligence analysis and churn risk management
"""

from fastapi import APIRouter, HTTPException, Query
import logging
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/api/emotional-intelligence", tags=["emotional-intelligence"])

logger = logging.getLogger(__name__)

# ============================================================================
# EMOTIONAL INTELLIGENCE ENDPOINTS
# ============================================================================

@router.post("/analyze/{return_id}")
async def analyze_emotional_intelligence(return_id: str):
    """
    Analyze customer emotional intelligence from return comments
    """
    try:
        from agents.emotional_intelligence import EmotionalIntelligenceAgent
        from observability.metrics import MetricsCollector

        metrics = MetricsCollector()
        agent = EmotionalIntelligenceAgent(metrics)

        # Get return data from database
        from database.db import SessionLocal
        db = SessionLocal()

        # Mock return data (in production: query database)
        return_data = {
            "id": return_id,
            "return_reason": "Product damaged",
            "customer_comments": "Very disappointed with the quality. This is unacceptable!",
            "customer_return_count": 2,
            "customer_tenure_days": 365,
            "previous_complaint_count": 1,
            "customer_ltv": 500
        }

        # Run analysis
        eq_analysis = await agent.analyze(return_data)

        # Flag for intervention if high churn risk
        if eq_analysis.get('churn_risk'):
            # In production: create intervention ticket
            logger.warning(f"High churn risk for customer {return_id}")

        return {
            "return_id": return_id,
            "analysis": eq_analysis,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Emotional intelligence analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/customer/{customer_id}/profile")
async def get_customer_emotional_profile(customer_id: str):
    """
    Get customer's emotional profile across all returns
    """
    try:
        # Mock data (in production: aggregate from database)
        profile = {
            "customer_id": customer_id,
            "return_count": 2,
            "avg_sentiment_score": -2.5,
            "avg_intensity": 3,
            "churn_risk_probability": 0.45,
            "emotional_trend": "improving",
            "sentiment_timeline": [
                {"date": "2026-09-20", "score": -4.2, "emotion": "angry"},
                {"date": "2026-09-24", "score": -2.0, "emotion": "frustrated"},
                {"date": "2026-09-26", "score": -1.5, "emotion": "neutral"}
            ],
            "recommended_actions": [
                "Regular follow-up calls",
                "Loyalty program enrollment",
                "Personalized discount offer"
            ]
        }

        return profile

    except Exception as e:
        logger.error(f"Profile retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/at-risk-customers")
async def get_at_risk_customers(threshold: float = Query(-3.0), skip: int = 0, limit: int = 50):
    """
    Get customers at high churn risk for proactive intervention
    """
    try:
        # Mock data (in production: query database for customers with EQ < threshold)
        at_risk_customers = [
            {
                "customer_id": "CUST_001",
                "eq_score": -4.2,
                "churn_probability": 0.85,
                "ltv": 2500,
                "last_return": "2026-09-26",
                "return_count": 3,
                "recommended_intervention": "Executive outreach"
            },
            {
                "customer_id": "CUST_002",
                "eq_score": -3.8,
                "churn_probability": 0.72,
                "ltv": 1800,
                "last_return": "2026-09-25",
                "return_count": 2,
                "recommended_intervention": "Personal apology + discount"
            },
            {
                "customer_id": "CUST_003",
                "eq_score": -3.5,
                "churn_probability": 0.65,
                "ltv": 3200,
                "last_return": "2026-09-24",
                "return_count": 2,
                "recommended_intervention": "Senior support call"
            }
        ]

        return {
            "at_risk_customers": at_risk_customers[skip:skip+limit],
            "total": len(at_risk_customers),
            "threshold": threshold,
            "skip": skip,
            "limit": limit,
            "message": f"{len(at_risk_customers)} customers at high churn risk"
        }

    except Exception as e:
        logger.error(f"At-risk customers error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interventions/{customer_id}")
async def create_intervention(customer_id: str, intervention_type: str, notes: str):
    """
    Create intervention for at-risk customer
    """
    try:
        intervention = {
            "intervention_id": f"INT_{datetime.now().timestamp()}",
            "customer_id": customer_id,
            "type": intervention_type,  # executive_outreach, discount_offer, loyalty_enrollment, etc
            "notes": notes,
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            "assigned_to": None,
            "completed_at": None
        }

        # In production: save to database
        logger.info(f"Intervention created: {intervention['intervention_id']} for {customer_id}")

        return {
            "status": "created",
            "intervention": intervention
        }

    except Exception as e:
        logger.error(f"Intervention creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sentiment-trends/{customer_id}")
async def get_sentiment_trends(customer_id: str, days: int = Query(30, ge=7, le=365)):
    """
    Get sentiment trend over time for a customer
    """
    try:
        # Mock data (in production: query from database)
        trends = {
            "customer_id": customer_id,
            "period_days": days,
            "trend_direction": "improving",
            "avg_score_start": -3.8,
            "avg_score_end": -1.5,
            "improvement": 60,  # percentage
            "sentiment_history": [
                {"date": "2026-08-27", "score": -3.8, "emotion": "angry", "return_count": 1},
                {"date": "2026-09-03", "score": -3.2, "emotion": "frustrated", "return_count": 0},
                {"date": "2026-09-10", "score": -2.8, "emotion": "frustrated", "return_count": 1},
                {"date": "2026-09-17", "score": -2.1, "emotion": "neutral", "return_count": 0},
                {"date": "2026-09-24", "score": -1.5, "emotion": "neutral", "return_count": 1},
                {"date": "2026-09-26", "score": -1.2, "emotion": "satisfied", "return_count": 0},
            ]
        }

        return trends

    except Exception as e:
        logger.error(f"Sentiment trends error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/churn-prevention-strategies/{eq_score}")
async def get_churn_prevention_strategies(eq_score: float):
    """
    Get recommended strategies based on EQ score
    """
    try:
        from agents.emotional_intelligence import EmotionalIntelligenceAgent
        from observability.metrics import MetricsCollector

        metrics = MetricsCollector()
        agent = EmotionalIntelligenceAgent(metrics_collector=metrics)
        strategies = agent.get_churn_prevention_strategies(eq_score)

        return {
            "eq_score": eq_score,
            "strategies": strategies,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Strategies error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard-summary")
async def get_emotional_intelligence_dashboard_summary():
    """
    Get summary stats for emotional intelligence dashboard
    """
    try:
        summary = {
            "total_customers_analyzed": 1523,
            "high_churn_risk": 47,
            "medium_churn_risk": 132,
            "low_churn_risk": 1344,
            "avg_sentiment_score": -0.8,
            "sentiment_distribution": {
                "very_angry": 5,
                "angry": 12,
                "frustrated": 47,
                "neutral": 598,
                "satisfied": 732,
                "delighted": 129
            },
            "interventions_in_progress": 23,
            "interventions_completed": 156,
            "intervention_success_rate": 0.78,
            "churn_rate": 0.031,
            "prevention_rate": 0.40  # 40% of at-risk customers retained
        }

        return {
            "summary": summary,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Dashboard summary error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
