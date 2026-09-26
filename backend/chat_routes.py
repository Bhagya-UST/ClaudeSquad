"""
Chat and Customer Care Agent Routes
WebSocket and REST endpoints for real-time customer support
"""

from fastapi import APIRouter, WebSocket, HTTPException, Query
from fastapi.responses import StreamingResponse
import json
import logging
from datetime import datetime
from typing import Optional
import anthropic
import os
from .schemas import DashboardInsightsRequest

router = APIRouter(prefix="/api/chat", tags=["customer-care"])

logger = logging.getLogger(__name__)

# Initialize Anthropic client
claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ============================================================================
# REST ENDPOINTS FOR CHAT
# ============================================================================

@router.post("/query")
async def submit_chat_query(customer_id: str, query: str, context: Optional[dict] = None):
    """
    Submit a customer query to the Care Agent
    """
    try:
        from agents.customer_care import CustomerCareAgent
        from rag.hybrid_rag import HybridRAG
        from observability.metrics import MetricsCollector

        rag = HybridRAG()
        metrics = MetricsCollector()
        agent = CustomerCareAgent(rag, metrics)

        # Get response
        response = await agent.handle_customer_query(customer_id, query, context)

        return {
            "status": "success",
            "customer_id": customer_id,
            "query": query,
            "response": response["response"],
            "actions": response["actions"],
            "escalation_required": response["escalation_required"],
            "timestamp": response["timestamp"]
        }

    except Exception as e:
        logger.error(f"Chat query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{customer_id}")
async def get_chat_history(customer_id: str, limit: int = Query(50, ge=1, le=100)):
    """
    Get chat conversation history for a customer
    """
    try:
        from database.db import SessionLocal

        db = SessionLocal()
        # In production: fetch from database
        history = {
            "customer_id": customer_id,
            "messages": [
                {
                    "role": "customer",
                    "content": "Why was my order rejected?",
                    "timestamp": "2026-09-26T10:30:00Z"
                },
                {
                    "role": "agent",
                    "content": "I can help! Let me look into that for you...",
                    "timestamp": "2026-09-26T10:30:05Z"
                }
            ],
            "total_messages": 2
        }

        return history

    except Exception as e:
        logger.error(f"History retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear-history/{customer_id}")
async def clear_history(customer_id: str):
    """
    Clear chat history for a customer
    """
    try:
        # Clear in-memory history
        return {
            "status": "success",
            "customer_id": customer_id,
            "message": "Chat history cleared"
        }

    except Exception as e:
        logger.error(f"Clear history error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggest-solutions")
async def get_suggested_solutions(customer_id: str, issue_summary: str):
    """
    Generate suggested solutions for a customer issue
    """
    try:
        from agents.customer_care import CustomerCareAgent
        from rag.hybrid_rag import HybridRAG
        from observability.metrics import MetricsCollector

        rag = HybridRAG()
        metrics = MetricsCollector()
        agent = CustomerCareAgent(rag, metrics)

        solutions = await agent.suggest_solutions(customer_id, issue_summary)

        return {
            "customer_id": customer_id,
            "issue_summary": issue_summary,
            "solutions": solutions,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Solutions error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/escalate/{customer_id}")
async def escalate_to_human(customer_id: str, reason: str, last_message: str):
    """
    Escalate customer issue to human agent
    """
    try:
        escalation = {
            "customer_id": customer_id,
            "escalation_id": f"ESC_{datetime.now().timestamp()}",
            "reason": reason,
            "last_customer_message": last_message,
            "assigned_to": "support_team",
            "status": "pending",
            "priority": "high" if "angry" in reason.lower() else "normal",
            "created_at": datetime.now().isoformat()
        }

        # In production: create ticket in support system
        logger.info(f"Escalation created: {escalation}")

        return {
            "status": "escalated",
            "escalation": escalation,
            "message": "Your issue has been escalated to our support team. A human agent will contact you shortly."
        }

    except Exception as e:
        logger.error(f"Escalation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rag-context/{customer_id}")
async def get_rag_context(customer_id: str, query: str):
    """
    Get RAG context for a customer query (for debugging/transparency)
    """
    try:
        from rag.hybrid_rag import HybridRAG

        rag = HybridRAG()
        rag_context = rag.retrieve_context({
            "return_reason": query,
            "customer_comments": query,
            "customer_id": customer_id
        })

        return {
            "customer_id": customer_id,
            "query": query,
            "retrieved_returns": rag_context.get("retrieved_returns", []),
            "retrieval_stats": rag_context.get("retrieval_stats", {}),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"RAG context error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/insights")
async def get_dashboard_insights(request: DashboardInsightsRequest):
    """
    Use Claude AI to generate intelligent insights about dashboard metrics
    """
    try:
        dashboard_metrics = request.dashboard_metrics or {}
        user_query = request.user_query
        customer_id = request.customer_id

        # Format metrics context for Claude
        metrics_context = ""
        if dashboard_metrics:
            metrics_context = f"""
Dashboard Metrics Context:
- Fraud Rate: {dashboard_metrics.get('kpis', {}).get('fraud_rate', 'N/A')}%
- Total Returns: {dashboard_metrics.get('kpis', {}).get('total_returns', 'N/A'):,}
- Classification Accuracy: {dashboard_metrics.get('kpis', {}).get('classification_accuracy', 'N/A')}%
- ROI Multiple: {dashboard_metrics.get('financial', {}).get('roi_multiplier', 'N/A')}x
- Fraud Prevention Value: ${dashboard_metrics.get('financial', {}).get('estimated_fraud_prevented', 0):,.0f}
- Automation Rate: {dashboard_metrics.get('operations', {}).get('automation_rate', 'N/A')}%
- Customer Satisfaction: {dashboard_metrics.get('customer_insights', {}).get('customer_satisfaction', 'N/A')}%
- Industry Accuracy Benchmark: {dashboard_metrics.get('advantage', {}).get('industry_accuracy_benchmark', 'N/A')}%

Return Category Breakdown:
- Sizing Issues: {dashboard_metrics.get('trends', {}).get('sizing_issues_percent', 'N/A')}%
- Quality Issues: {dashboard_metrics.get('trends', {}).get('quality_issues_percent', 'N/A')}%
- Defective: {dashboard_metrics.get('trends', {}).get('defective_percent', 'N/A')}%
- Fraud: {dashboard_metrics.get('trends', {}).get('fraud_percent', 'N/A')}%
"""

        # Create prompt for Claude
        system_prompt = """You are an expert AI analyst for ReturnIQ, a return management and fraud detection platform.
Your role is to help dashboard users understand their metrics and provide actionable insights.

When users ask questions about their data:
1. Provide clear, data-driven insights
2. Highlight trends and patterns
3. Give actionable recommendations
4. Use the metrics provided to support your analysis
5. Be concise but thorough
6. Use professional but approachable language"""

        user_prompt = f"""User Query: {user_query}

{metrics_context}

Please provide an insightful analysis or answer to the user's query based on the dashboard metrics provided."""

        # Call Claude API
        message = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        insight = message.content[0].text

        return {
            "status": "success",
            "customer_id": customer_id,
            "user_query": user_query,
            "insight": insight,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Insights generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating insights: {str(e)}")

# ============================================================================
# WEBSOCKET ENDPOINT FOR REAL-TIME STREAMING CHAT
# ============================================================================

@router.websocket("/ws/{customer_id}")
async def websocket_chat(websocket: WebSocket, customer_id: str):
    """
    WebSocket endpoint for real-time streaming chat
    """
    await websocket.accept()
    logger.info(f"WebSocket connection established for customer: {customer_id}")

    try:
        from agents.customer_care import CustomerCareAgent
        from rag.hybrid_rag import HybridRAG
        from observability.metrics import MetricsCollector

        rag = HybridRAG()
        metrics = MetricsCollector()
        agent = CustomerCareAgent(rag, metrics)

        while True:
            # Receive message from client
            try:
                data = await websocket.receive_json()
            except Exception as e:
                logger.error(f"WebSocket JSON receive error: {e}")
                await websocket.send_json({
                    "type": "error",
                    "error": "Invalid JSON format",
                    "timestamp": datetime.now().isoformat()
                })
                continue

            if data.get("type") == "message":
                query = data.get("message", "")
                context = data.get("context", {})

                # Stream response back to client
                async for chunk in agent.handle_streaming_query(customer_id, query, context):
                    await websocket.send_json({
                        "type": "stream",
                        "data": chunk,
                        "timestamp": datetime.now().isoformat()
                    })

                # Send completion signal
                await websocket.send_json({
                    "type": "complete",
                    "message": "Response complete",
                    "timestamp": datetime.now().isoformat()
                })

            elif data.get("type") == "clear":
                agent.clear_history(customer_id)
                await websocket.send_json({
                    "type": "cleared",
                    "message": "History cleared"
                })

            elif data.get("type") == "escalate":
                await websocket.send_json({
                    "type": "escalation",
                    "status": "initiated",
                    "message": "Connecting you to a human agent..."
                })

    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })

    finally:
        await websocket.close()
        logger.info(f"WebSocket connection closed for customer: {customer_id}")
