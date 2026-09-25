"""ReturnIQ Chatbot - Claude-powered assistant."""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime


class ReturnIQChatbot:
    """Claude-powered chatbot for ReturnIQ insights."""

    def __init__(self, rag_retriever=None):
        self.conversation_history = []
        self.analysis_context = None
        self.rag_retriever = rag_retriever

    def set_analysis_context(self, understanding, insight, action, returns_df):
        """Set the current analysis results as context for the chatbot."""
        self.analysis_context = {
            "understanding": understanding,
            "insight": insight,
            "action": action,
            "returns_df": returns_df,
            "timestamp": datetime.now().isoformat(),
        }

    def get_system_prompt(self) -> str:
        """Build system prompt with current analysis context and RAG."""
        if not self.analysis_context:
            return "You are ReturnIQ, an AI assistant for retail returns intelligence."

        understanding = self.analysis_context["understanding"]
        insight = self.analysis_context["insight"]
        action = self.analysis_context["action"]
        returns_df = self.analysis_context["returns_df"]

        churn_risks = sum(1 for r in understanding if r.churn_risk)
        fraud_suspects = sum(1 for r in returns_df if r.is_fraud_suspect) if hasattr(returns_df, '__iter__') else 0

        trends_summary = "\n".join([
            f"- {t.pattern} ({t.count} returns, {t.percentage}%, significance: {t.significance})"
            for t in insight.trends[:5]
        ]) if insight.trends else "No significant trends detected"

        anomalies_summary = "\n".join([
            f"- {a.category} (severity: {a.severity}, z-score: {a.z_score}): {a.description}"
            for a in insight.anomalies[:5]
        ]) if insight.anomalies else "No anomalies detected"

        # Add RAG context if available
        rag_context = ""
        if self.rag_retriever:
            try:
                rag_context = "\n\n" + self.rag_retriever.retrieve_baseline_context()
            except:
                pass

        system_prompt = f"""You are ReturnIQ, an AI assistant specialized in retail returns intelligence and analysis.

CURRENT ANALYSIS SNAPSHOT:
- Total Returns: {len(returns_df)}
- Returns Analyzed: {len(understanding)}
- Churn Risks Detected: {churn_risks}
- Fraud Suspects: {fraud_suspects}
- Trends Found: {len(insight.trends)}
- Anomalies: {len(insight.anomalies)}
- Recommendations: {len(action.recommendations)}

TOP TRENDS:
{trends_summary}

KEY ANOMALIES:
{anomalies_summary}

RECOMMENDATIONS:
{json.dumps([{{"title": r.title, "priority": r.priority.value, "confidence": r.confidence, "requires_review": r.human_review_required}} for r in action.recommendations[:3]], indent=2)}{rag_context}

IMPORTANT GUIDELINES:
1. Always cite evidence: reference specific metrics, return counts, or z-scores
2. Distinguish between current data and historical patterns
3. Note which recommendations require human review
4. Explain confidence levels - higher confidence (>0.85) is more reliable
5. For high-priority items, emphasize the business impact
6. Support the human review process - highlight evidence that needs reviewer attention
7. Be transparent about uncertainty in the data

Your role:
1. Answer questions about return patterns, trends, and anomalies
2. Explain why certain items have high return rates with supporting evidence
3. Provide insights on customer churn risks
4. Suggest actions to reduce returns
5. Help interpret the data and recommendations
6. Highlight items that need human review
7. Use both current and historical context
8. Be concise but thorough

Format your responses clearly with bullet points when appropriate."""

        return system_prompt

    def chat(self, user_message: str) -> str:
        """Send a message to Claude and get a response."""
        try:
            from anthropic import Anthropic
        except ImportError:
            return (
                "Chatbot requires Anthropic SDK. "
                "Install with: pip install anthropic"
            )

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return (
                "ANTHROPIC_API_KEY environment variable not set. "
                "Please set it to use the chatbot."
            )

        client = Anthropic()

        self.conversation_history.append({
            "role": "user",
            "content": user_message,
        })

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=self.get_system_prompt(),
            messages=self.conversation_history,
        )

        assistant_message = response.content[0].text

        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message,
        })

        return assistant_message

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

    def get_suggested_questions(self) -> List[str]:
        """Get suggested questions based on current analysis."""
        if not self.analysis_context:
            return [
                "What trends are visible in the returns data?",
                "Which products have the highest return rates?",
                "What are the main recommendations?",
            ]

        return [
            "What are the top return reasons?",
            "Which SKUs should we focus on?",
            "How can we reduce churn risk?",
            "What's causing the anomalies?",
            "Which recommendations should we prioritize?",
            "Are there any fraud patterns?",
        ]
