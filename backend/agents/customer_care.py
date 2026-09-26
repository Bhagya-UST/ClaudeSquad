"""
Customer Care Agent - Chat Interface for Customer Support
Communicates with RAG system to provide intelligent customer support
"""

import anthropic
import json
import logging
import os
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class CustomerCareAgent:
    """AI-powered customer care agent with RAG integration"""

    def __init__(self, rag_system, metrics_collector):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.rag = rag_system
        self.metrics = metrics_collector
        self.conversation_history = []

    async def handle_customer_query(self, customer_id: str, query: str, context: Dict = None) -> Dict:
        """
        Handle a customer query with RAG context

        Args:
            customer_id: Customer ID
            query: Customer's question/issue
            context: Additional context (return_id, order_id, etc)

        Returns:
            Response with answer, recommendations, and escalation flag
        """
        self.metrics.start_timer("agent.customer_care")

        try:
            # 1. Retrieve relevant context from RAG
            rag_context = await self._get_rag_context(customer_id, query, context)

            # 2. Build system prompt
            system_prompt = self._build_system_prompt(customer_id, rag_context)

            # 3. Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": query
            })

            # 4. Get response from Claude
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=self.conversation_history
            )

            assistant_message = response.content[0].text

            # 5. Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            # 6. Parse response for actions
            actions = self._parse_response_actions(assistant_message)

            # 7. Check if escalation needed
            should_escalate = await self._check_escalation(customer_id, query, assistant_message)

            self.metrics.end_timer("agent.customer_care")
            self.metrics.record_event("customer_care.query_handled", {
                "customer_id": customer_id,
                "escalated": should_escalate
            })

            return {
                "response": assistant_message,
                "actions": actions,
                "escalation_required": should_escalate,
                "escalation_reason": actions.get("escalation_reason") if should_escalate else None,
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.92
            }

        except Exception as e:
            logger.error(f"Customer care agent error: {str(e)}")
            self.metrics.record_error("agent.customer_care", str(e))
            raise

    async def _get_rag_context(self, customer_id: str, query: str, context: Dict = None) -> Dict:
        """
        Retrieve relevant context from RAG system
        """
        try:
            rag_input = {
                "return_reason": query,
                "customer_comments": query,
                "customer_id": customer_id,
                "product_id": context.get("product_id") if context else None
            }

            rag_results = self.rag.retrieve_context(rag_input, top_k=3)

            # Get customer history
            customer_history = {
                "total_returns": 2,  # Mock - query DB in production
                "recent_issues": ["sizing", "quality"],
                "lifetime_value": 500,
                "satisfaction_score": 3.5
            }

            # Get relevant trends
            trends = {
                "active_trends": ["SKU #456 sizing issues", "Supplier ABC quality"],
                "related_to_customer": True
            }

            return {
                "retrieved_returns": rag_results.get("retrieved_returns", []),
                "customer_history": customer_history,
                "relevant_trends": trends,
                "retrieval_stats": rag_results.get("retrieval_stats", {})
            }

        except Exception as e:
            logger.error(f"RAG context retrieval error: {str(e)}")
            return {"error": str(e)}

    def _build_system_prompt(self, customer_id: str, rag_context: Dict) -> str:
        """Build system prompt with RAG context"""

        retrieved_info = ""
        if rag_context.get("retrieved_returns"):
            retrieved_info = "Similar customer cases:\n"
            for ret in rag_context["retrieved_returns"][:2]:
                retrieved_info += f"- {ret.get('return_reason', 'N/A')}\n"

        customer_info = ""
        if rag_context.get("customer_history"):
            hist = rag_context["customer_history"]
            customer_info = f"""
Customer Profile:
- Lifetime Value: ${hist.get('lifetime_value', 0)}
- Total Returns: {hist.get('total_returns', 0)}
- Satisfaction: {hist.get('satisfaction_score', 0)}/5
- Recent Issues: {', '.join(hist.get('recent_issues', []))}
"""

        return f"""You are ReturnIQ's AI Customer Care Agent. Your role is to:
1. Provide empathetic, helpful support to customers
2. Resolve issues using return and product knowledge
3. Offer solutions based on similar past cases
4. Escalate complex issues appropriately

CONTEXT FROM RAG SYSTEM:
{retrieved_info}

{customer_info}

INSTRUCTIONS:
- Be professional and empathetic
- Reference similar cases when relevant
- Offer specific solutions (update size chart, check inventory, etc)
- Suggest proactive actions to prevent future returns
- Flag issues that need human escalation
- Always be honest about limitations

ESCALATION TRIGGERS (flag for human review):
- Customer expressing high frustration (anger, disappointment)
- Request for refund exceptions
- Product quality concerns (potential safety issue)
- Multiple related returns from same customer
- Requests outside normal policy

Respond in a conversational, helpful tone."""

    def _parse_response_actions(self, response: str) -> Dict:
        """Parse response for suggested actions"""
        actions = {
            "provide_refund": "refund" in response.lower(),
            "update_product_info": "size chart" in response.lower() or "product description" in response.lower(),
            "check_inventory": "inventory" in response.lower() or "stock" in response.lower(),
            "quality_review": "quality" in response.lower() or "defect" in response.lower(),
            "escalation_reason": None
        }

        if "escalate" in response.lower() or "human" in response.lower():
            actions["escalation_reason"] = "Customer issue requires human review"

        return actions

    async def _check_escalation(self, customer_id: str, query: str, response: str) -> bool:
        """
        Determine if issue should be escalated to human agent
        """
        # High frustration keywords
        frustration_keywords = [
            "unacceptable", "disappointed", "angry", "furious",
            "terrible", "horrible", "never again", "lawsuit",
            "complaint", "refund policy", "exceptions"
        ]

        # Check query and response for escalation triggers
        combined_text = (query + " " + response).lower()

        escalation_score = 0
        for keyword in frustration_keywords:
            if keyword in combined_text:
                escalation_score += 1

        # Check if multiple returns
        if query.lower().count("return") > 2:
            escalation_score += 2

        # Escalate if score > threshold
        return escalation_score >= 3

    def clear_history(self, customer_id: str = None):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info(f"History cleared for customer: {customer_id}")

    def get_conversation_history(self) -> List[Dict]:
        """Get current conversation history"""
        return self.conversation_history

    async def handle_streaming_query(self, customer_id: str, query: str, context: Dict = None):
        """
        Handle streaming response for real-time chat
        """
        self.metrics.start_timer("agent.customer_care.streaming")

        try:
            # Get RAG context
            rag_context = await self._get_rag_context(customer_id, query, context)
            system_prompt = self._build_system_prompt(customer_id, rag_context)

            # Add to history
            self.conversation_history.append({
                "role": "user",
                "content": query
            })

            # Stream response
            with self.client.messages.stream(
                model=self.model,
                max_tokens=1024,
                system=system_prompt,
                messages=self.conversation_history
            ) as stream:
                full_response = ""
                for text in stream.text_stream:
                    full_response += text
                    yield text  # Yield for streaming

            # Add to history after streaming complete
            self.conversation_history.append({
                "role": "assistant",
                "content": full_response
            })

            self.metrics.end_timer("agent.customer_care.streaming")

        except Exception as e:
            logger.error(f"Streaming error: {str(e)}")
            self.metrics.record_error("agent.customer_care.streaming", str(e))
            raise

    async def suggest_solutions(self, customer_id: str, issue_summary: str) -> List[Dict]:
        """
        Generate suggested solutions for a customer issue
        """
        self.metrics.start_timer("agent.customer_care.solutions")

        try:
            system_prompt = """You are a solutions generator for ReturnIQ.
            Generate 3-5 specific, actionable solutions for customer issues.
            Format as JSON array with: title, description, steps, estimated_impact"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                system=system_prompt,
                messages=[{
                    "role": "user",
                    "content": f"Customer issue: {issue_summary}"
                }]
            )

            # Parse solutions
            try:
                solutions = json.loads(response.content[0].text)
                if not isinstance(solutions, list):
                    solutions = [solutions]
            except:
                solutions = [{
                    "title": "Recommended Action",
                    "description": response.content[0].text,
                    "steps": ["Contact support"],
                    "estimated_impact": "High"
                }]

            self.metrics.end_timer("agent.customer_care.solutions")
            return solutions

        except Exception as e:
            logger.error(f"Solutions generation error: {str(e)}")
            self.metrics.record_error("agent.customer_care.solutions", str(e))
            return []
