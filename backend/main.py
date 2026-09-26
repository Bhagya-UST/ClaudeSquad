"""
ReturnIQ Backend - Main FastAPI Application
Complete 8-Agent Multi-Agent Architecture with Hybrid RAG
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from datetime import datetime, timedelta
import os
from typing import Optional, List
import json
from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address

# Custom imports
from .auth import create_access_token, verify_token, authenticate_user, create_demo_token, User, Token, TokenData
from .schemas import ReturnRequest, ClassifyRequest
from .agents.orchestrator_v2 import AgentOrchestrator
from .agents.customer_care import CustomerCareAgent
from .agents.emotional_intelligence import EmotionalIntelligenceAgent
from .rag.hybrid_rag import HybridRAG
from .observability.metrics import MetricsCollector
from .observability.guardrails import SafetyGuardrails
from .database.models import Return, Classification, Trend, Recommendation, EmotionalIntelligence
from .database.db import Database
from .evaluation.evaluator import EvaluationFramework
from .chat_routes import router as chat_router
from .ei_routes import router as ei_router
from .admin_routes import router as admin_router
from .dependencies import get_current_user, get_current_tenant, get_user_permissions

load_dotenv()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
db = Database()
rag = HybridRAG()
metrics = MetricsCollector()
guardrails = SafetyGuardrails()
orchestrator = AgentOrchestrator(rag, metrics)
evaluator = EvaluationFramework()
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting ReturnIQ Backend...")
    db.connect()
    rag.initialize()
    metrics.start()
    logger.info("All systems initialized")
    yield
    # Shutdown
    logger.info("Shutting down ReturnIQ...")
    db.close()

app = FastAPI(
    title="ReturnIQ API",
    description="AI-Powered Return Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Secure configuration
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    os.getenv("FRONTEND_URL", "http://localhost:3000")
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Rate limiting
app.state.limiter = limiter

# Include specialized routes
app.include_router(chat_router)
app.include_router(ei_router)
app.include_router(admin_router)

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@app.post("/api/auth/login", response_model=Token)
async def login(email: str = None, password: str = None):
    """Authenticate user and return JWT token"""
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password required")

    # Try database authentication first, then demo
    session = db.get_session()
    user_data = authenticate_user(email, password, session)
    session.close()

    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user_data)
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user_data.user_id,
        email=user_data.email,
        role=user_data.role,
        tenant_id=user_data.tenant_id
    )

@app.post("/api/auth/demo-token", response_model=Token)
async def get_demo_token():
    """Get demo token for quick testing (development only)"""
    token = create_demo_token()
    from .auth import DEMO_USERS, DEMO_TENANT_ID
    demo_user = DEMO_USERS["demo"]
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=demo_user["user_id"],
        email=demo_user["email"],
        role=demo_user["role"],
        tenant_id=DEMO_TENANT_ID
    )

@app.get("/api/auth/me")
async def get_me(
    current_user: User = Depends(get_current_user),
    current_tenant = Depends(get_current_tenant)
):
    """Get current authenticated user info with tenant"""
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "role": current_user.role,
        "tenant_id": current_user.tenant_id,
        "tenant_name": current_tenant.name if current_tenant else None
    }

# ============================================================================
# RETURNS ENDPOINTS
# ============================================================================

@app.post("/api/returns")
async def submit_return(
    return_request: ReturnRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    current_tenant = Depends(get_current_tenant),
    permissions: List[str] = Depends(get_user_permissions)
):
    """Submit a new return for analysis"""
    # Check permission
    from .auth_rbac import Permission
    if Permission.CREATE_RETURN.value not in permissions:
        raise HTTPException(status_code=403, detail="Permission denied")

    try:
        metrics.start_timer("api.returns.submit")

        # Store return in database with tenant_id
        return_data = return_request.dict()
        return_data["tenant_id"] = current_tenant.id
        return_id = db.create_return(return_data)
        return_obj = db.get_return(return_id)

        # Trigger async analysis
        background_tasks.add_task(process_return_async, return_id)

        metrics.record_event("returns.submitted", {"return_id": str(return_id), "user_id": current_user.user_id, "tenant_id": str(current_tenant.id)})
        metrics.end_timer("api.returns.submit")

        return {
            "status": "accepted",
            "return_id": str(return_id),
            "message": "Return submitted for analysis"
        }

    except Exception as e:
        metrics.record_error("returns.submit", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/returns/{return_id}")
async def get_return_details(return_id: str):
    """Get complete return analysis with all agent outputs"""
    try:
        metrics.start_timer("api.returns.get")

        return_obj = db.get_return(return_id)
        if not return_obj:
            raise HTTPException(status_code=404, detail="Return not found")

        classification = db.get_classification(return_id)
        emotional_data = db.get_emotional_intelligence(return_id)
        recommendations = db.get_recommendations_for_return(return_id)

        result = {
            "return": return_obj.to_dict(),
            "classification": classification.to_dict() if classification else None,
            "emotional_intelligence": emotional_data.to_dict() if emotional_data else None,
            "recommendations": [r.to_dict() for r in recommendations],
            "analysis_status": "complete" if classification else "pending"
        }

        metrics.end_timer("api.returns.get")
        return result

    except Exception as e:
        metrics.record_error("returns.get", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/returns")
async def list_returns(
    status: Optional[str] = None,
    classification: Optional[str] = None,
    skip: int = Query(0, ge=0, le=10000),
    limit: int = Query(50, ge=1, le=500)
):
    """List returns with filters"""
    try:
        filters = {}
        if status:
            filters['status'] = status
        if classification:
            filters['classification'] = classification

        returns_list = db.list_returns(filters=filters, skip=skip, limit=limit)
        total = db.count_returns(filters=filters)

        return {
            "data": [r.to_dict() for r in returns_list],
            "total": total,
            "skip": skip,
            "limit": limit
        }

    except Exception as e:
        metrics.record_error("returns.list", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CLASSIFICATION ENDPOINTS
# ============================================================================

@app.post("/api/classify")
async def classify_return(return_id: str):
    """Run classification agent on a return"""
    try:
        metrics.start_timer("api.classify")

        return_obj = db.get_return(return_id)
        if not return_obj:
            raise HTTPException(status_code=404, detail="Return not found")

        # Run classification agent
        classification_result = await orchestrator.run_classifier_agent(return_obj)

        # Store result
        classification_id = db.create_classification(
            return_id=return_id,
            category=classification_result['category'],
            confidence=classification_result['confidence'],
            reasoning=classification_result['reasoning']
        )

        # Validate guardrails
        if not guardrails.validate_confidence_threshold(classification_result['confidence']):
            db.flag_for_human_review(classification_id)

        metrics.record_metric("classification.accuracy", classification_result['confidence'])
        metrics.end_timer("api.classify")

        return {
            "classification_id": str(classification_id),
            "category": classification_result['category'],
            "confidence": classification_result['confidence'],
            "reasoning": classification_result['reasoning'],
            "flagged_for_review": classification_result['confidence'] < 0.70
        }

    except Exception as e:
        metrics.record_error("classify", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/classify/{return_id}")
async def get_classification(return_id: str):
    """Get classification result for a return"""
    try:
        classification = db.get_classification(return_id)
        if not classification:
            raise HTTPException(status_code=404, detail="Classification not found")

        return classification.to_dict()

    except Exception as e:
        metrics.record_error("classify.get", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# TRENDS ENDPOINTS
# ============================================================================

@app.post("/api/trends/detect")
async def detect_trends(period: str = "weekly"):
    """Run trend detection on historical returns"""
    try:
        metrics.start_timer("api.trends.detect")

        # Get returns for period
        start_date = datetime.now() - timedelta(days=7 if period == "weekly" else 30)
        returns_data = db.get_returns_since(start_date)

        # Run trend detection agent
        trends = await orchestrator.run_trend_detection_agent(returns_data)

        # Store trends
        stored_trend_ids = []
        for trend in trends:
            trend_id = db.create_trend(
                title=trend['title'],
                description=trend['description'],
                returns_count=trend['returns_count'],
                percentage_of_total=trend['percentage'],
                z_score=trend['z_score'],
                significance_level=trend['significance'],
                evidence=json.dumps(trend['evidence_returns'])
            )
            stored_trend_ids.append(trend_id)

        metrics.record_metric("trends.detected_count", len(trends))
        metrics.end_timer("api.trends.detect")

        return {
            "trends_count": len(trends),
            "trend_ids": [str(tid) for tid in stored_trend_ids],
            "trends": trends
        }

    except Exception as e:
        metrics.record_error("trends.detect", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trends")
async def get_trends(period: str = "weekly", skip: int = Query(0, ge=0, le=10000), limit: int = Query(10, ge=1, le=500)):
    """Get top trends"""
    try:
        trends = db.get_top_trends(limit=limit, skip=skip)

        return {
            "data": [t.to_dict() for t in trends],
            "total": db.count_trends(),
            "period": period
        }

    except Exception as e:
        metrics.record_error("trends.get", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trends/{trend_id}")
async def get_trend_details(trend_id: str):
    """Get detailed trend information with evidence"""
    try:
        trend = db.get_trend(trend_id)
        if not trend:
            raise HTTPException(status_code=404, detail="Trend not found")

        # Get evidence returns
        try:
            evidence_ids = json.loads(trend.evidence) if isinstance(trend.evidence, str) else trend.evidence or []
        except (json.JSONDecodeError, TypeError):
            evidence_ids = []

        evidence_returns = db.get_returns_by_ids(evidence_ids)

        return {
            "trend": trend.to_dict(),
            "evidence_count": len(evidence_returns),
            "sample_evidence": [r.to_dict() for r in evidence_returns[:5]]
        }

    except Exception as e:
        metrics.record_error("trends.get_details", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# RECOMMENDATIONS ENDPOINTS
# ============================================================================

@app.post("/api/recommendations/generate")
async def generate_recommendations(trend_id: Optional[str] = None, return_id: Optional[str] = None):
    """Generate recommendations based on trends or specific returns"""
    try:
        metrics.start_timer("api.recommendations.generate")

        if not trend_id and not return_id:
            raise HTTPException(status_code=400, detail="Either trend_id or return_id is required")

        if trend_id is not None:
            trend = db.get_trend(trend_id)
            if not trend:
                raise HTTPException(status_code=404, detail="Trend not found")
            analysis_context = {"trend": trend.to_dict()}
        else:
            return_obj = db.get_return(return_id)
            if not return_obj:
                raise HTTPException(status_code=404, detail="Return not found")
            analysis_context = {"return": return_obj.to_dict()}

        # Run recommendation engine
        recommendations = await orchestrator.run_recommendation_engine(analysis_context)

        # Validate with guardrails
        validated_recommendations = []
        for rec in recommendations:
            validation = guardrails.validate_recommendation(rec)

            if validation['status'] == 'flagged':
                # Flag for human review
                rec_id = db.create_recommendation(
                    trend_id=trend_id,
                    return_id=return_id,
                    recommendation_text=rec['text'],
                    recommendation_type=rec['type'],
                    estimated_impact=rec['estimated_impact'],
                    confidence=rec['confidence'],
                    evidence=json.dumps(rec['evidence']),
                    validation_status='flagged',
                    status='pending_review'
                )
            else:
                # Approved
                rec_id = db.create_recommendation(
                    trend_id=trend_id,
                    return_id=return_id,
                    recommendation_text=rec['text'],
                    recommendation_type=rec['type'],
                    estimated_impact=rec['estimated_impact'],
                    confidence=rec['confidence'],
                    evidence=json.dumps(rec['evidence']),
                    validation_status='approved',
                    status='pending_approval'
                )

            validated_recommendations.append({
                "recommendation_id": str(rec_id),
                **rec,
                "validation_status": validation['status']
            })

        metrics.record_metric("recommendations.generated", len(validated_recommendations))
        metrics.end_timer("api.recommendations.generate")

        return {
            "recommendations_count": len(validated_recommendations),
            "recommendations": validated_recommendations
        }

    except Exception as e:
        metrics.record_error("recommendations.generate", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recommendations")
async def list_recommendations(status: str = "pending_approval", skip: int = Query(0, ge=0, le=10000), limit: int = Query(20, ge=1, le=500)):
    """List recommendations with filters"""
    try:
        recommendations = db.get_recommendations(status=status, skip=skip, limit=limit)

        return {
            "data": [r.to_dict() for r in recommendations],
            "total": db.count_recommendations(status=status),
            "status": status
        }

    except Exception as e:
        metrics.record_error("recommendations.list", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommendations/{rec_id}/approve")
async def approve_recommendation(rec_id: str):
    """Approve a recommendation for implementation"""
    try:
        db.update_recommendation_status(rec_id, status='approved', approval_date=datetime.now())
        metrics.record_event("recommendations.approved", {"rec_id": rec_id})

        return {"status": "approved", "recommendation_id": rec_id}

    except Exception as e:
        metrics.record_error("recommendations.approve", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/recommendations/{rec_id}/implement")
async def implement_recommendation(rec_id: str, actual_impact: float):
    """Mark recommendation as implemented and record actual impact"""
    try:
        db.update_recommendation_status(
            rec_id,
            status='implemented',
            implementation_date=datetime.now(),
            actual_impact=actual_impact
        )

        metrics.record_event("recommendations.implemented", {
            "rec_id": rec_id,
            "actual_impact": actual_impact
        })

        return {"status": "implemented", "recommendation_id": rec_id, "actual_impact": actual_impact}

    except Exception as e:
        metrics.record_error("recommendations.implement", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# EMOTIONAL INTELLIGENCE ENDPOINTS
# ============================================================================

@app.post("/api/emotional-intelligence/{return_id}")
async def analyze_emotional_intelligence(return_id: str):
    """Analyze customer emotional intelligence from return comments"""
    try:
        metrics.start_timer("api.emotional_intelligence.analyze")

        return_obj = db.get_return(return_id)
        if not return_obj:
            raise HTTPException(status_code=404, detail="Return not found")

        # Run emotional intelligence agent
        eq_analysis = await orchestrator.run_emotional_intelligence_agent(return_obj)

        # Store emotional intelligence data
        eq_id = db.create_emotional_intelligence(
            return_id=return_id,
            sentiment_score=eq_analysis['sentiment_score'],
            emotion=eq_analysis['emotion'],
            intensity=eq_analysis['intensity'],
            churn_risk=eq_analysis['churn_risk'],
            churn_risk_score=eq_analysis['churn_risk_score'],
            lifecycle_stage=eq_analysis['lifecycle_stage']
        )

        # If high churn risk, flag for intervention
        if eq_analysis['churn_risk']:
            db.flag_customer_for_intervention(
                customer_id=return_obj['customer_id'],
                reason="High churn risk detected",
                churn_risk_score=eq_analysis['churn_risk_score']
            )
            metrics.record_event("churn_risk.flagged", {"customer_id": return_obj['customer_id']})

        metrics.end_timer("api.emotional_intelligence.analyze")

        return {
            "eq_id": str(eq_id),
            **eq_analysis,
            "intervention_flag": eq_analysis['churn_risk']
        }

    except Exception as e:
        metrics.record_error("emotional_intelligence.analyze", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}/emotional-profile")
async def get_customer_emotional_profile(customer_id: str):
    """Get customer's emotional profile across all returns"""
    try:
        returns = db.get_customer_returns(customer_id)
        eq_data = [db.get_emotional_intelligence(r.id) for r in returns]
        eq_data = [e for e in eq_data if e]  # Filter None values

        if not eq_data:
            raise HTTPException(status_code=404, detail="No emotional data found for customer")

        # Calculate trends
        avg_sentiment = sum(e.sentiment_score for e in eq_data) / len(eq_data)
        avg_intensity = sum(e.intensity for e in eq_data) / len(eq_data)
        churn_risk_count = sum(1 for e in eq_data if e.churn_risk)

        return {
            "customer_id": customer_id,
            "return_count": len(returns),
            "avg_sentiment_score": avg_sentiment,
            "avg_intensity": avg_intensity,
            "churn_risk_probability": churn_risk_count / len(eq_data),
            "recent_emotional_data": [e.to_dict() for e in eq_data[-5:]],
            "sentiment_trend": "improving" if avg_sentiment > 0 else "declining"
        }

    except Exception as e:
        metrics.record_error("emotional_intelligence.customer_profile", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/at-risk-customers")
async def get_at_risk_customers(threshold: float = -3.0, skip: int = Query(0, ge=0, le=10000), limit: int = Query(50, ge=1, le=500)):
    """Get customers at high churn risk for proactive intervention"""
    try:
        at_risk = db.get_customers_above_churn_risk(threshold, skip=skip, limit=limit)

        return {
            "data": at_risk,
            "total": db.count_at_risk_customers(threshold),
            "threshold": threshold,
            "recommendation": "Prioritize for customer success outreach"
        }

    except Exception as e:
        metrics.record_error("at_risk_customers", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# METRICS & OBSERVABILITY ENDPOINTS
# ============================================================================

@app.get("/api/metrics/timeseries")
async def get_metrics_timeseries(metric_name: str, period: str = "7d"):
    """Get time series data for a specific metric"""
    try:
        # Parse period format (e.g., "7d", "30d")
        if not period.endswith('d'):
            raise ValueError("Period must be in format like '7d', '30d'")

        try:
            days = int(period[:-1])
        except ValueError:
            raise ValueError("Period must be a number followed by 'd'")

        if days <= 0 or days > 365:
            raise ValueError("Period must be between 1 and 365 days")

        data = metrics.get_timeseries(metric_name, days=days)

        return {
            "metric": metric_name,
            "period": period,
            "data": data
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        metrics.record_error("metrics.timeseries", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics/health")
async def get_system_health():
    """Get overall system health status"""
    try:
        health_status = {
            "status": "healthy",
            "database": "connected" if db.is_connected() else "disconnected",
            "rag_system": "ready" if rag.is_initialized() else "initializing",
            "llm_api": "operational" if orchestrator.check_llm_connectivity() else "degraded",
            "last_error": metrics.get_last_error(),
            "uptime_seconds": metrics.get_uptime(),
            "timestamp": datetime.now().isoformat()
        }

        # Determine overall status
        if health_status["database"] != "connected" or health_status["llm_api"] != "operational":
            health_status["status"] = "degraded"

        return health_status

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# EVALUATION & FEEDBACK ENDPOINTS
# ============================================================================

@app.post("/api/evaluations/run-weekly")
async def run_weekly_evaluation(background_tasks: BackgroundTasks):
    """Trigger weekly evaluation framework"""
    try:
        background_tasks.add_task(evaluator.run_full_evaluation_cycle)

        return {
            "status": "evaluation_started",
            "message": "Weekly evaluation running in background"
        }

    except Exception as e:
        metrics.record_error("evaluation.run", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/evaluations/latest")
async def get_latest_evaluation():
    """Get latest evaluation results"""
    try:
        results = evaluator.get_latest_results()

        if not results:
            raise HTTPException(status_code=404, detail="No evaluations found")

        return results

    except Exception as e:
        metrics.record_error("evaluation.get", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# REAL-TIME METRICS ENDPOINTS
# ============================================================================

from .metrics_service import metrics_service

@app.get("/api/metrics/dashboard")
async def get_dashboard_metrics():
    """Get all dashboard metrics in real-time from actual data"""
    try:
        return metrics_service.get_complete_dashboard()
    except Exception as e:
        logger.error(f"Error fetching dashboard metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch metrics")

@app.get("/api/metrics/kpis")
async def get_kpi_metrics():
    """Get core KPIs only"""
    try:
        return metrics_service.get_kpis()
    except Exception as e:
        logger.error(f"Error fetching KPI metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch KPI metrics")

@app.get("/api/metrics/financial")
async def get_financial_metrics():
    """Get financial impact metrics"""
    try:
        return metrics_service.get_financial_metrics()
    except Exception as e:
        logger.error(f"Error fetching financial metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch financial metrics")

@app.get("/api/metrics/performance")
async def get_performance_metrics():
    """Get system performance metrics"""
    try:
        return metrics_service.get_performance_metrics()
    except Exception as e:
        logger.error(f"Error fetching performance metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch performance metrics")

@app.get("/api/metrics/ml")
async def get_ml_metrics():
    """Get ML model performance metrics"""
    try:
        return metrics_service.get_ml_metrics()
    except Exception as e:
        logger.error(f"Error fetching ML metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch ML metrics")

@app.get("/api/metrics/customers")
async def get_customer_metrics():
    """Get customer insight metrics"""
    try:
        return metrics_service.get_customer_insights()
    except Exception as e:
        logger.error(f"Error fetching customer metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch customer metrics")

@app.get("/api/metrics/trends")
async def get_trend_metrics():
    """Get trend analysis metrics"""
    try:
        return metrics_service.get_trends()
    except Exception as e:
        logger.error(f"Error fetching trend metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch trend metrics")

@app.get("/api/metrics/risk")
async def get_risk_metrics():
    """Get risk analysis metrics"""
    try:
        return metrics_service.get_risk_analysis()
    except Exception as e:
        logger.error(f"Error fetching risk metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch risk metrics")

@app.get("/api/metrics/operations")
async def get_operations_metrics():
    """Get operational efficiency metrics"""
    try:
        return metrics_service.get_operations_metrics()
    except Exception as e:
        logger.error(f"Error fetching operations metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch operations metrics")

@app.get("/api/metrics/safety")
async def get_safety_metrics():
    """Get safety and compliance metrics"""
    try:
        return metrics_service.get_safety_metrics()
    except Exception as e:
        logger.error(f"Error fetching safety metrics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch safety metrics")

# ============================================================================
# AUDIT & COMPLIANCE ENDPOINTS
# ============================================================================

@app.get("/api/audit-logs")
async def get_audit_logs(
    action: Optional[str] = None,
    user_id: Optional[str] = None,
    skip: int = Query(0, ge=0, le=10000),
    limit: int = Query(100, ge=1, le=500)
):
    """Get audit trail logs"""
    try:
        filters = {}
        if action:
            filters['action'] = action
        if user_id:
            filters['user_id'] = user_id

        logs = db.get_audit_logs(filters=filters, skip=skip, limit=limit)

        return {
            "data": [log.to_dict() for log in logs],
            "total": db.count_audit_logs(filters=filters),
            "filters": filters
        }

    except Exception as e:
        metrics.record_error("audit_logs", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# BACKGROUND TASKS
# ============================================================================

async def process_return_async(return_id: str):
    """Background task: Process return through all agents"""
    try:
        logger.info(f"Processing return {return_id}")

        return_obj = db.get_return(return_id)

        # 1. Classification
        classification = await orchestrator.run_classifier_agent(return_obj)
        db.create_classification(return_id, **classification)

        # 2. Emotional Intelligence
        eq_data = await orchestrator.run_emotional_intelligence_agent(return_obj)
        db.create_emotional_intelligence(return_id, **eq_data)

        # 3. Root Cause Detection
        root_cause = await orchestrator.run_root_cause_agent(return_obj)
        db.update_return_root_cause(return_id, root_cause)

        # Update status
        db.update_return_status(return_id, "processed")
        logger.info(f"Return {return_id} processing complete")

    except Exception as e:
        logger.error(f"Error processing return {return_id}: {str(e)}")
        metrics.record_error("process_return_async", str(e))

# ============================================================================
# CATCH-ALL ROUTE (Suppress noise from browser extensions)
# ============================================================================

@app.api_route("/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def catch_all(path_name: str):
    """Catch all undefined routes and return 404 silently"""
    # Silently return 404 for noise requests (browser extensions, malware, etc)
    # Don't log these as they pollute the logs with spam
    raise HTTPException(status_code=404, detail="Not found")

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "ok",
        "service": "ReturnIQ API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
