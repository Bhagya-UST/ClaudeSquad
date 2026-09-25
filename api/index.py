"""ReturnIQ API for Vercel - Flask Backend"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.orchestrator import ReturnIQOrchestrator
from agents.chatbot import ReturnIQChatbot
from synthetic_returns import generate_returns_csv

# Configure Flask to serve static files from 'public' directory
public_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'public')
app = Flask(__name__, static_folder=public_dir, static_url_path='')
CORS(app)

# Global state
_orchestrator = None
_returns_df = None
_analysis_results = None
_chatbot = None

def init_app():
    """Initialize app and generate data."""
    global _orchestrator, _returns_df, _analysis_results, _chatbot

    if _orchestrator is None:
        # Generate synthetic data
        try:
            csv_path = "/tmp/synthetic_returns.csv"
            if not os.path.exists(csv_path):
                generate_returns_csv(num_returns=150, output_path=csv_path)
            _returns_df = pd.read_csv(csv_path)

            # Initialize orchestrator
            _orchestrator = ReturnIQOrchestrator(mode="demo")

            # Run analysis
            understanding, insight, action = _orchestrator.process_returns(_returns_df)
            _analysis_results = {
                "understanding": understanding,
                "insight": insight,
                "action": action,
            }

            # Initialize chatbot with RAG
            _chatbot = ReturnIQChatbot(rag_retriever=_orchestrator.rag_retriever)
            _chatbot.set_analysis_context(understanding, insight, action, _returns_df)

            # Generate sample historical data if this is first run
            if _orchestrator.history_store.get_historical_context()["total_analyses"] == 0:
                _orchestrator.history_store.generate_sample_history()
        except Exception as e:
            print(f"Error initializing app: {e}")
            return False

    return True


# ===== HEALTH CHECK =====
@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "mode": "demo", "data": "synthetic"})


# ===== DATA ENDPOINTS =====
@app.route("/api/data/returns", methods=["GET"])
def get_returns():
    """Get all returns."""
    if not init_app() or _returns_df is None:
        return jsonify({"error": "Failed to initialize"}), 500
    
    # Mask PII
    df = _returns_df.copy()
    df["customer_email"] = "***@example.com"
    df["customer_phone"] = "***-****"
    
    return jsonify(df.to_dict("records"))


@app.route("/api/data/search", methods=["GET"])
def search_returns():
    """Search returns by SKU."""
    if not init_app() or _returns_df is None:
        return jsonify({"error": "Failed to initialize"}), 500
    
    sku = request.args.get("sku", "").upper()
    reason = request.args.get("reason", "")
    
    df = _returns_df.copy()
    
    if sku:
        df = df[df["sku"].str.contains(sku, case=False)]
    if reason and reason != "all":
        df = df[df["reason"] == reason]
    
    # Mask PII
    df["customer_email"] = "***@example.com"
    df["customer_phone"] = "***-****"
    
    return jsonify(df.to_dict("records"))


# ===== ANALYSIS ENDPOINTS =====
@app.route("/api/analysis/overview", methods=["GET"])
def overview():
    """Get executive overview."""
    if not init_app():
        return jsonify({"error": "Failed to initialize"}), 500

    understanding = _analysis_results["understanding"]
    insight = _analysis_results["insight"]
    action = _analysis_results["action"]

    # Calculate metrics
    churn_risks = sum(1 for r in understanding if r.churn_risk)
    fraud_suspects = int(_returns_df["is_fraud_suspect"].sum())
    avg_confidence = sum(r.confidence for r in understanding) / len(understanding)

    # Classification distribution
    classifications = {}
    for r in understanding:
        key = r.classification.value
        classifications[key] = classifications.get(key, 0) + 1

    return jsonify({
        "total_returns": int(len(_returns_df)),
        "analyzed": int(len(understanding)),
        "trends_detected": int(len(insight.trends)),
        "recommendations": int(len(action.recommendations)),
        "churn_risks": int(churn_risks),
        "fraud_suspects": int(fraud_suspects),
        "avg_confidence": round(float(avg_confidence), 3),
        "classifications": classifications,
    })


@app.route("/api/analysis/trends", methods=["GET"])
def get_trends():
    """Get detected trends."""
    if not init_app():
        return jsonify({"error": "Failed to initialize"}), 500

    insight = _analysis_results["insight"]

    trends = []
    for t in insight.trends[:10]:
        trends.append({
            "pattern": t.pattern,
            "count": int(t.count),
            "percentage": float(t.percentage),
            "significance": float(t.significance),
            "z_score": float(t.z_score),
            "supporting_returns": t.supporting_returns[:5],
        })

    return jsonify({"trends": trends})


@app.route("/api/analysis/anomalies", methods=["GET"])
def get_anomalies():
    """Get detected anomalies."""
    if not init_app():
        return jsonify({"error": "Failed to initialize"}), 500

    insight = _analysis_results["insight"]

    anomalies = []
    for a in insight.anomalies:
        anomalies.append({
            "category": a.category,
            "value": float(a.value),
            "expected": float(a.expected),
            "z_score": float(a.z_score),
            "severity": a.severity,
            "description": a.description,
        })

    return jsonify({"anomalies": anomalies})


@app.route("/api/analysis/recommendations", methods=["GET"])
def get_recommendations():
    """Get recommendations."""
    if not init_app():
        return jsonify({"error": "Failed to initialize"}), 500

    action = _analysis_results["action"]

    recs = []
    for r in action.recommendations:
        recs.append({
            "id": r.recommendation_id,
            "title": r.title,
            "description": r.description,
            "priority": r.priority.value,
            "confidence": float(r.confidence),
            "impact": r.estimated_impact,
            "action": r.required_action,
            "status": r.status,
            "requires_review": r.human_review_required,
            "supporting_records": getattr(r, "supporting_records", [])[:10],
        })

    return jsonify({"recommendations": recs})


@app.route("/api/analysis/sentiment", methods=["GET"])
def get_sentiment():
    """Get sentiment distribution."""
    if not init_app():
        return jsonify({"error": "Failed to initialize"}), 500

    understanding = _analysis_results["understanding"]

    sentiments = {}
    emotions = []
    for r in understanding:
        key = r.sentiment.value
        sentiments[key] = sentiments.get(key, 0) + 1
        emotions.append(float(r.emotion_intensity))

    return jsonify({
        "sentiments": sentiments,
        "avg_intensity": float(sum(emotions) / len(emotions)) if emotions else 0.0,
        "churn_risk_count": int(sum(1 for r in understanding if r.churn_risk)),
    })


@app.route("/api/analysis/metrics", methods=["GET"])
def get_metrics():
    """Get observability metrics."""
    if not init_app():
        return jsonify({"error": "Failed to initialize"}), 500
    
    metrics = _orchestrator.get_metrics_snapshot(len(_returns_df))
    
    return jsonify({
        "understanding": {
            "calls": metrics["understanding"].calls_total,
            "successful": metrics["understanding"].calls_successful,
            "latency_ms": metrics["understanding"].avg_latency_ms,
        },
        "insight": {
            "calls": metrics["insight"].calls_total,
            "successful": metrics["insight"].calls_successful,
            "latency_ms": metrics["insight"].avg_latency_ms,
        },
        "action": {
            "calls": metrics["action"].calls_total,
            "successful": metrics["action"].calls_successful,
            "latency_ms": metrics["action"].avg_latency_ms,
        },
        "system": {
            "hallucination_rate": metrics["system"].hallucination_rate,
            "confidence_violations": metrics["system"].confidence_violations,
        },
    })


# ===== APPROVAL ENDPOINTS =====
@app.route("/api/recommendation/approve", methods=["POST"])
def approve_rec():
    """Approve a recommendation."""
    if not init_app():
        return jsonify({"error": "Failed to initialize"}), 500
    
    data = request.json
    rec_id = data.get("id")
    
    if _orchestrator.approve_recommendation(rec_id):
        return jsonify({"status": "approved", "id": rec_id})
    else:
        return jsonify({"error": "Recommendation not found"}), 404


@app.route("/api/recommendation/reject", methods=["POST"])
def reject_rec():
    """Reject a recommendation."""
    if not init_app():
        return jsonify({"error": "Failed to initialize"}), 500
    
    data = request.json
    rec_id = data.get("id")
    
    if _orchestrator.reject_recommendation(rec_id):
        return jsonify({"status": "rejected", "id": rec_id})
    else:
        return jsonify({"error": "Recommendation not found"}), 404


# ===== REVIEW WORKFLOW ENDPOINTS =====
@app.route("/api/review/pending", methods=["GET"])
def get_pending_reviews():
    """Get recommendations pending human review."""
    if not init_app():
        return jsonify({"error": "Failed to initialize"}), 500

    review_data = _orchestrator.review_data
    return jsonify({
        "pending_review": review_data.get("pending_review", []),
        "auto_approved": review_data.get("auto_approved", []),
        "insufficient_evidence": review_data.get("insufficient_evidence", []),
    })


@app.route("/api/review/approve", methods=["POST"])
def approve_with_notes():
    """Approve recommendation with reviewer notes."""
    if not init_app():
        return jsonify({"error": "Failed to initialize"}), 500

    data = request.json
    rec_id = data.get("id")
    notes = data.get("notes", "")

    if _orchestrator.action_agent.approve_recommendation(rec_id, notes):
        return jsonify({"status": "approved", "id": rec_id, "notes": notes})
    else:
        return jsonify({"error": "Recommendation not found"}), 404


@app.route("/api/review/reject", methods=["POST"])
def reject_with_notes():
    """Reject recommendation with reviewer notes."""
    if not init_app():
        return jsonify({"error": "Failed to initialize"}), 500

    data = request.json
    rec_id = data.get("id")
    notes = data.get("notes", "")

    if _orchestrator.action_agent.reject_recommendation(rec_id, notes):
        return jsonify({"status": "rejected", "id": rec_id, "notes": notes})
    else:
        return jsonify({"error": "Recommendation not found"}), 404


# ===== RAG & HISTORICAL DATA ENDPOINTS =====
@app.route("/api/historical/context", methods=["GET"])
def get_historical_context():
    """Get historical baseline context."""
    if not init_app():
        return jsonify({"error": "Failed to initialize"}), 500

    context = _orchestrator.history_store.get_historical_context()
    return jsonify({
        "total_analyses": int(context["total_analyses"]),
        "avg_churn_risk": float(context["avg_churn_risk"]),
        "avg_fraud_suspects": float(context["avg_fraud_suspects"]),
        "recurring_patterns": [
            {"pattern": p["pattern"], "occurrences": p["occurrences"]}
            for p in context["recurring_patterns"]
        ],
        "critical_anomalies": context["critical_anomalies"],
    })


@app.route("/api/historical/trends", methods=["GET"])
def get_trend_history():
    """Get historical trend data."""
    if not init_app():
        return jsonify({"error": "Failed to initialize"}), 500

    pattern = request.args.get("pattern", "")
    if not pattern:
        return jsonify({"error": "Pattern parameter required"}), 400

    history = _orchestrator.history_store.get_trend_history(pattern)
    return jsonify({"trends": history})


@app.route("/api/historical/anomalies", methods=["GET"])
def get_anomaly_history():
    """Get historical anomaly data."""
    if not init_app():
        return jsonify({"error": "Failed to initialize"}), 500

    category = request.args.get("category", "")
    if not category:
        return jsonify({"error": "Category parameter required"}), 400

    history = _orchestrator.history_store.get_anomaly_history(category)
    return jsonify({"anomalies": history})


@app.route("/api/rag/context", methods=["POST"])
def get_rag_context():
    """Get RAG context for a specific analysis."""
    if not init_app():
        return jsonify({"error": "Failed to initialize"}), 500

    data = request.json
    trends = data.get("trends", [])
    anomalies = data.get("anomalies", [])
    recommendation_titles = data.get("recommendation_titles", [])

    context = _orchestrator.rag_retriever.build_rag_context(
        trends, anomalies, recommendation_titles
    )

    return jsonify({"rag_context": context})


# ===== CHATBOT ENDPOINTS =====
@app.route("/api/chat", methods=["POST"])
def chat():
    """Chat with ReturnIQ assistant."""
    if not init_app():
        return jsonify({"error": "Failed to initialize"}), 500

    data = request.json
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "Message cannot be empty"}), 400

    try:
        response = _chatbot.chat(message)
        return jsonify({
            "message": response,
            "suggested_questions": _chatbot.get_suggested_questions(),
        })
    except Exception as e:
        return jsonify({"error": f"Chat error: {str(e)}"}), 500


@app.route("/api/chat/suggestions", methods=["GET"])
def chat_suggestions():
    """Get suggested questions for the chatbot."""
    if not init_app():
        return jsonify({"error": "Failed to initialize"}), 500

    return jsonify({
        "suggestions": _chatbot.get_suggested_questions(),
    })


@app.route("/api/chat/reset", methods=["POST"])
def chat_reset():
    """Reset chatbot conversation history."""
    if not init_app():
        return jsonify({"error": "Failed to initialize"}), 500

    _chatbot.clear_history()
    return jsonify({"status": "reset", "message": "Conversation history cleared"})


# ===== MAIN ENTRY POINT =====
@app.route("/", methods=["GET"])
def index():
    """Serve index.html"""
    return send_from_directory(public_dir, "index.html")


@app.route("/api", methods=["GET"])
def api_root():
    """API root endpoint."""
    return jsonify({
        "app": "ReturnIQ MVP",
        "version": "1.0",
        "mode": "demo",
        "endpoints": {
            "health": "/api/health",
            "data": "/api/data/returns",
            "search": "/api/data/search?sku=SKU-456&reason=sizing",
            "overview": "/api/analysis/overview",
            "trends": "/api/analysis/trends",
            "anomalies": "/api/analysis/anomalies",
            "recommendations": "/api/analysis/recommendations",
            "sentiment": "/api/analysis/sentiment",
            "metrics": "/api/analysis/metrics",
        }
    })


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))