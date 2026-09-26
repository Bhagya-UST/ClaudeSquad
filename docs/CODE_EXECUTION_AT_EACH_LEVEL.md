# ReturnIQ - Code Execution at Each Processing Level

**Actual Code Snippets Showing How Data Flows Through System**

---

## Level 1: API Endpoint (FastAPI)

```python
# From backend/main.py - API receives return
@app.post("/api/returns")
async def submit_return(
    return_data: dict,
    background_tasks: BackgroundTasks
):
    """Submit a new return for analysis"""
    try:
        metrics.start_timer("api.returns.submit")
        
        # 1. Store in database
        return_id = db.create_return(return_data)
        
        # 2. Trigger async processing
        background_tasks.add_task(process_return_async, return_id)
        
        metrics.record_event("returns.submitted", {"return_id": str(return_id)})
        return {
            "status": "accepted",
            "return_id": str(return_id),
            "message": "Return submitted for analysis"
        }
    except Exception as e:
        metrics.record_error("returns.submit", str(e))
        raise HTTPException(status_code=500, detail=str(e))

# INPUT:
# {
#   "customer_id": "CUST001",
#   "product_id": "PROD123",
#   "return_reason": "Defective",
#   "customer_comments": "Button stopped working after 2 weeks",
#   "refund_amount": 49.99
# }

# OUTPUT:
# {
#   "status": "accepted",
#   "return_id": "550e8400-e29b-41d4-a716-446655440000"
# }
```

---

## Level 2: Background Task Processing

```python
# From backend/main.py - Process return through agents
async def process_return_async(return_id: str):
    """Background task: Process return through all agents"""
    try:
        logger.info(f"Processing return {return_id}")
        return_obj = db.get_return(return_id)
        
        # 1. Classification
        classification = await orchestrator.run_classifier_agent(return_obj)
        db.create_classification(
            return_id,
            category=classification['category'],
            confidence=classification['confidence'],
            reasoning=classification['reasoning']
        )
        
        # 2. Emotional Intelligence
        eq_data = await orchestrator.run_emotional_intelligence_agent(return_obj)
        db.create_emotional_intelligence(
            return_id,
            sentiment_score=eq_data['sentiment_score'],
            churn_risk=eq_data['churn_risk']
        )
        
        # 3. Root Cause
        root_cause = await orchestrator.run_root_cause_agent(return_obj)
        db.update_return_root_cause(return_id, root_cause)
        
        # Update status
        db.update_return_status(return_id, "processed")
        
    except Exception as e:
        logger.error(f"Error processing return {return_id}: {str(e)}")
        metrics.record_error("process_return_async", str(e))
```

---

## Level 3: Agent Orchestrator

```python
# From backend/agents/orchestrator_v2.py
class AgentOrchestrator:
    def __init__(self, rag, metrics):
        self.rag = rag
        self.metrics = metrics
        self.classifier_agent = ClassifierAgent()
        self.ei_agent = EmotionalIntelligenceAgent()
        # ... other agents
    
    async def run_classifier_agent(self, return_obj: dict):
        """Route return to Classifier agent"""
        try:
            metrics_timer = self.metrics.start_timer("agent.classifier")
            
            # Prepare context
            context = {
                "return_reason": return_obj['return_reason'],
                "customer_comments": return_obj['customer_comments'],
                "product_info": return_obj  # Full object for context
            }
            
            # Call agent
            result = await self.classifier_agent.classify(context)
            
            self.metrics.end_timer(metrics_timer)
            self.metrics.record_metric("classifier.confidence", result['confidence'])
            
            return result
            
        except Exception as e:
            self.metrics.record_error("classifier", str(e))
            raise
```

---

## Level 4: Individual Agents

### Classifier Agent

```python
# From backend/agents/classifier.py
class ClassifierAgent:
    def __init__(self):
        self.client = Anthropic()  # Claude API
    
    async def classify(self, context: dict):
        """Classify return into category"""
        
        prompt = f"""
        Analyze this return and classify it.
        
        Return Reason: {context['return_reason']}
        Customer Comments: {context['customer_comments']}
        
        Categories: Defective, Wrong Size, Wrong Item, Damaged, Other
        
        Respond in JSON format:
        {{
            "category": "<category>",
            "confidence": <0.0-1.0>,
            "reasoning": "<explanation>"
        }}
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Parse response
        import json
        result = json.loads(response.content[0].text)
        return result

# INPUT:
# {
#   "return_reason": "Defective",
#   "customer_comments": "Button stopped working after 2 weeks"
# }

# OUTPUT:
# {
#   "category": "Defective Product",
#   "confidence": 0.95,
#   "reasoning": "Clear indication of manufacturing defect..."
# }
```

### Emotional Intelligence Agent

```python
# From backend/agents/emotional_intelligence.py
class EmotionalIntelligenceAgent:
    def __init__(self):
        self.client = Anthropic()
    
    async def analyze(self, context: dict):
        """Analyze customer sentiment and churn risk"""
        
        prompt = f"""
        Analyze customer emotional state and churn risk.
        
        Customer Comments: {context['customer_comments']}
        Return History: {context.get('return_count', 1)} returns
        Lifecycle: {context.get('lifecycle', 'unknown')}
        
        Respond in JSON:
        {{
            "sentiment_score": <-5 to 5>,
            "emotion": "<emotion>",
            "intensity": <1-10>,
            "churn_risk": <true/false>,
            "churn_risk_score": <-5 to 5>
        }}
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return json.loads(response.content[0].text)

# INPUT:
# {
#   "customer_comments": "Very disappointed. Third defect in 6 months.",
#   "return_count": 3
# }

# OUTPUT:
# {
#   "sentiment_score": -4.2,
#   "emotion": "frustrated",
#   "intensity": 9,
#   "churn_risk": true,
#   "churn_risk_score": -4.2
# }
```

### Root Cause Agent

```python
# From backend/agents/root_cause.py
class RootCauseAgent:
    async def detect(self, context: dict):
        """Identify root cause of return"""
        
        # Could query manufacturing data, quality control logs, etc.
        prompt = f"""
        What is the root cause of this return?
        
        Category: {context['category']}
        Comments: {context['customer_comments']}
        Product: {context['product_id']}
        Serial Range: {context.get('serial_number', 'unknown')}
        
        Respond in JSON:
        {{
            "root_cause": "<root cause>",
            "probability": <0.0-1.0>,
            "recommendation": "<action>"
        }}
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return json.loads(response.content[0].text)

# OUTPUT:
# {
#   "root_cause": "Manufacturing defect in batch Q3-2024-001",
#   "probability": 0.88,
#   "recommendation": "Halt production, inspect warehouse stock"
# }
```

---

## Level 5: Validation & Guardrails

```python
# From backend/observability/guardrails.py
class SafetyGuardrails:
    def validate_confidence_threshold(self, confidence: float) -> bool:
        """Check if confidence is above minimum threshold"""
        MIN_CONFIDENCE = 0.70
        return confidence >= MIN_CONFIDENCE
    
    def validate_recommendation(self, recommendation: dict) -> dict:
        """Validate recommendation before implementation"""
        
        checks = {
            'has_evidence': bool(recommendation.get('evidence')),
            'confidence_sufficient': recommendation.get('confidence', 0) > 0.7,
            'impact_reasonable': recommendation.get('estimated_impact', 0) > 0,
            'no_conflicts': not self._check_conflicts(recommendation)
        }
        
        if all(checks.values()):
            return {'status': 'approved', 'checks': checks}
        else:
            return {'status': 'flagged', 'checks': checks}
    
    def _check_conflicts(self, rec: dict) -> bool:
        """Check for conflicting recommendations"""
        # Logic to check against existing recommendations
        return False

# INPUT:
# {
#   "text": "Stop production batch Q3-2024-001",
#   "confidence": 0.92,
#   "evidence": ["Defect rate 15%", "Customer complaints 3x"]
# }

# OUTPUT:
# {
#   "status": "approved",
#   "checks": {
#     "has_evidence": true,
#     "confidence_sufficient": true,
#     "impact_reasonable": true,
#     "no_conflicts": true
#   }
# }
```

---

## Level 6: Database Storage

```python
# From backend/database/db.py
class Database:
    def create_classification(self, return_id, category, confidence, reasoning):
        """Store classification in database"""
        
        classification = Classification(
            return_id=return_id,
            category=category,
            confidence=confidence,
            reasoning=reasoning,
            agent_version="2.0.1",
            created_at=datetime.utcnow()
        )
        
        session.add(classification)
        session.commit()
        
        return classification.id
    
    def create_emotional_intelligence(self, return_id, sentiment_score, 
                                      emotion, intensity, churn_risk):
        """Store EI analysis"""
        
        eq = EmotionalIntelligence(
            return_id=return_id,
            sentiment_score=sentiment_score,
            emotion=emotion,
            intensity=intensity,
            churn_risk=churn_risk,
            created_at=datetime.utcnow()
        )
        
        session.add(eq)
        session.commit()
        
        # If high churn risk, flag for intervention
        if churn_risk and sentiment_score < -3:
            self.flag_customer_for_intervention(
                customer_id=self.get_return(return_id)['customer_id'],
                reason="High churn risk detected"
            )
        
        return eq.id

# SQL Generated:
# INSERT INTO classifications (return_id, category, confidence, reasoning, ...)
# VALUES ('550e8400...', 'Defective Product', 0.95, 'Clear indication...', ...)
#
# INSERT INTO emotional_intelligence (return_id, sentiment_score, emotion, ...)
# VALUES ('550e8400...', -2.5, 'frustrated', ...)
```

---

## Level 7: Frontend API Call

```typescript
// From frontend/src/components/ReturnSubmission.tsx
async function submitReturn(formData) {
  const token = localStorage.getItem('auth_token');
  
  const response = await fetch('http://localhost:8000/api/returns', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      customer_id: formData.customerId,
      product_id: formData.productId,
      return_reason: formData.reason,
      customer_comments: formData.comments,
      product_condition: formData.condition,
      refund_amount: parseFloat(formData.amount)
    })
  });
  
  const result = await response.json();
  
  if (response.ok) {
    setReturnId(result.return_id);
    showSuccessToast('Return submitted successfully');
    
    // Poll for results
    pollReturnStatus(result.return_id);
  } else {
    showErrorToast('Failed to submit return');
  }
}

async function pollReturnStatus(returnId) {
  const timer = setInterval(async () => {
    const response = await fetch(
      `http://localhost:8000/api/returns/${returnId}`,
      { headers: { 'Authorization': `Bearer ${token}` } }
    );
    
    const data = await response.json();
    
    if (data.analysis_status === 'complete') {
      clearInterval(timer);
      displayAnalysis(data);
    }
  }, 2000); // Poll every 2 seconds
}
```

---

## Level 8: Dashboard Metrics

```python
# From backend/metrics_service.py
class MetricsService:
    def get_complete_dashboard(self):
        """Get all metrics for dashboard"""
        
        returns_data = self.db.query(Return).all()
        classifications = self.db.query(Classification).all()
        ei_data = self.db.query(EmotionalIntelligence).all()
        
        return {
            'kpis': {
                'total_returns': len(returns_data),
                'return_rate': len(returns_data) / total_orders * 100,
                'avg_refund': sum(r.refund_amount for r in returns_data) / len(returns_data),
                'customer_satisfaction': self._calc_satisfaction(ei_data)
            },
            'financial': {
                'total_refunds': sum(r.refund_amount for r in returns_data),
                'cost_per_return': self._calc_processing_cost(),
                'lifetime_value_impact': self._calc_ltv_impact()
            },
            'performance': {
                'avg_processing_time': self._calc_avg_time(),
                'p95_response_time': self._calc_p95_time(),
                'agent_accuracy': self._calc_accuracy(classifications)
            }
        }

# OUTPUT (sent to frontend):
# {
#   "kpis": {
#     "total_returns": 245,
#     "return_rate": 2.3,
#     "avg_refund": 54.32,
#     "customer_satisfaction": 68.5
#   },
#   "financial": {
#     "total_refunds": 13308.40,
#     "cost_per_return": 12.50,
#     "lifetime_value_impact": -2450.00
#   },
#   "performance": {
#     "avg_processing_time": 2.3,
#     "p95_response_time": 4.1,
#     "agent_accuracy": 0.94
#   }
# }
```

---

## Complete Data Flow Example

```
CUSTOMER RETURN SUBMITTED
│
├─ Input Data:
│  {
│    "customer_id": "CUST001",
│    "product_id": "PROD123",
│    "return_reason": "Defective",
│    "customer_comments": "Button stopped after 2 weeks",
│    "refund_amount": 49.99
│  }
│
▼ (API Endpoint - Level 1)
API stores in database, queues background task
│
├─ Database saved:
│  returns table: ID = "550e8400...", status = "pending"
│
▼ (Background Processing - Level 2)
Orchestrator routes to agents
│
▼ (Agent Execution - Level 4)
3 agents run in parallel:
├─ Classifier: "Defective Product" (confidence: 0.95)
├─ EI Agent: sentiment -2.5, churn_risk: false
└─ Root Cause: "Manufacturing defect batch Q3"
│
▼ (Validation - Level 5)
Guardrails validate all outputs
│ - All confidence > 0.70 ✓
│ - No conflicts detected ✓
│ - Evidence present ✓
│
▼ (Database Storage - Level 6)
Results stored in database
├─ classifications table
├─ emotional_intelligence table
└─ update returns table: status = "processed"
│
▼ (Frontend Query - Level 7)
Frontend polls API for results
│
▼ (Dashboard Display - Level 8)
Shows:
├─ Classification: Defective (95% confident)
├─ Sentiment: Slightly Negative (-2.5)
├─ Root Cause: Manufacturing defect
├─ Recommendation: Inspect batch Q3
└─ Churn Risk: Low

[Complete]
```

---

**Version**: 1.0.0
**Last Updated**: September 26, 2024
