# ReturnIQ Agent Guide - Quick Reference

## 🎯 The 3-Agent Pipeline Explained

### **FLOW DIAGRAM**

```
                          ┌─────────────────────────┐
                          │   150 Return Records    │
                          │  (SKU, Reason, Refund)  │
                          └────────────┬────────────┘
                                       │
                    ┌──────────────────▼──────────────────┐
                    │                                      │
                    │  AGENT 1: UNDERSTANDING             │
                    │  File: agents/understanding.py      │
                    │  Runs: 150 times (one per return)   │
                    │                                      │
                    │  For each return:                    │
                    │  1. Classify reason                 │
                    │  2. Detect sentiment                │
                    │  3. Calculate emotion intensity     │
                    │  4. Assess churn risk               │
                    │  5. Score confidence                │
                    │                                      │
                    │  Output: UnderstandingResult        │
                    └──────────────────┬──────────────────┘
                                       │
                   ┌───────────────────▼────────────────────┐
                   │ 150 UnderstandingResults               │
                   │ [classification, sentiment, churn...]  │
                   └───────────────────┬────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────┐
                    │                                      │
                    │  AGENT 2: INSIGHT                   │
                    │  File: agents/insight.py            │
                    │  Runs: 1 time (aggregates all)      │
                    │                                      │
                    │  Analyzes all 150 results:          │
                    │  1. Count SKU frequency             │
                    │  2. Count reason frequency          │
                    │  3. Calculate z-scores              │
                    │  4. Find anomalies                  │
                    │  5. Detect patterns                 │
                    │                                      │
                    │  Output: InsightResult              │
                    └──────────────────┬──────────────────┘
                                       │
                      ┌────────────────▼──────────────────┐
                      │ InsightResult:                     │
                      │ - 9 Trends (patterns detected)    │
                      │ - 2 Anomalies (statistical)       │
                      │ - z-scores and significance       │
                      └────────────────┬──────────────────┘
                                       │
                    ┌──────────────────▼──────────────────┐
                    │                                      │
                    │  AGENT 3: ENHANCED ACTION           │
                    │  File: agents/action_enhanced.py    │
                    │  Runs: 1 time (generates recs)      │
                    │                                      │
                    │  For each trend/anomaly:            │
                    │  1. Validate evidence               │
                    │  2. Calculate confidence            │
                    │  3. Determine review routing        │
                    │  4. Add supporting records          │
                    │  5. Generate recommendation         │
                    │                                      │
                    │  Output: ActionResult               │
                    └──────────────────┬──────────────────┘
                                       │
                ┌──────────────────────▼─────────────────────┐
                │ ActionResult:                              │
                │ - 6 Recommendations                        │
                │ - With supporting return IDs               │
                │ - Priority levels                          │
                │ - Confidence scores                        │
                │ - Review requirements                      │
                └──────────────────────┬─────────────────────┘
                                       │
                    ┌──────────────────▼──────────────────┐
                    │                                      │
                    │  CHATBOT AGENT (Optional)           │
                    │  File: agents/chatbot.py            │
                    │  Uses: Claude API + RAG context     │
                    │                                      │
                    │  User asks question:                │
                    │  "Why is SKU-101 high return?"      │
                    │                                      │
                    │  Claude responds with:              │
                    │  - Evidence from Agent 2            │
                    │  - Historical patterns              │
                    │  - Actionable insights              │
                    │                                      │
                    └──────────────────┬──────────────────┘
                                       │
                         ┌─────────────▼──────────────┐
                         │   Dashboard UI             │
                         │   + Human Review Buttons   │
                         └────────────────────────────┘
```

---

## 📊 Agent 1: Understanding

**File**: `agents/understanding.py`

**What It Does**: Analyzes ONE return record and generates a classification

**Example Walkthrough**:

```
INPUT:
{
  "return_id": "RET100001",
  "sku": "SKU-101",
  "reason": "Item arrived damaged",
  "refund_amount": 89.99,
  "is_fraud_suspect": false
}

AGENT 1 PROCESSING:
1. Keyword Analysis
   - Reason: "Item arrived damaged"
   - Contains: "damaged" → DAMAGE classification

2. Sentiment Analysis  
   - "damaged" is a negative word
   - Sentiment: NEGATIVE

3. Emotion Intensity
   - Based on sentiment strength
   - Intensity: 0.85 (high emotion)

4. Churn Risk Assessment
   - Risk factors: damage (1 point), high refund (1 point)
   - Total: 2 factors → High risk
   - Churn Risk: TRUE

5. Confidence Calculation
   - Has reason text: +0.3
   - Specific classification (DAMAGE, not OTHER): +0.2
   - Total confidence: 0.92

OUTPUT:
{
  "return_id": "RET100001",
  "classification": "DAMAGE",
  "confidence": 0.92,
  "sentiment": "NEGATIVE",
  "emotion_intensity": 0.85,
  "churn_risk": true,
  "risk_score": 0.85
}
```

**Key Points**:
- Runs independently for each return (150 times in parallel-like fashion)
- Purely deterministic (same input = same output)
- No randomness, no AI guessing
- Pure Python keyword matching + math

---

## 🔍 Agent 2: Insight

**File**: `agents/insight.py`

**What It Does**: Aggregates Agent 1 outputs to detect patterns

**Example Walkthrough**:

```
INPUT:
150 UnderstandingResults from Agent 1
[
  {classification: "DAMAGE", ...},
  {classification: "SIZE_FIT", ...},
  {classification: "DAMAGE", ...},
  {classification: "DAMAGE", ...},
  {classification: "SIZE_FIT", ...},
  ...
]

AGENT 2 PROCESSING:

Step 1: Count Classifications
  DAMAGE: 45 returns
  SIZE_FIT: 32 returns
  QUALITY_ISSUE: 15 returns
  ... etc

Step 2: Detect Trends
  Trend 1: "Customers at risk of churn"
    - Count: 28 customers
    - Percentage: 28/150 = 18.67%
    - Z-score: 1.85
    - Significance: 0.78

Step 3: Detect Anomalies
  Anomaly 1: "Elevated Fraud Risk"
    - Expected fraud: 7.5% (baseline)
    - Actual fraud: 11 returns (7.33%)
    - Deviation: +3.5 returns
    - Z-score: 2.1
    - Severity: HIGH

OUTPUT:
{
  "trends": [
    {
      "pattern": "High damage returns",
      "count": 45,
      "percentage": 30.0,
      "z_score": 2.45,
      "significance": 0.92,
      "supporting_returns": ["RET100001", "RET100005", ...]
    },
    ...
  ],
  "anomalies": [
    {
      "category": "Elevated Fraud Risk",
      "value": 11,
      "expected": 7.5,
      "z_score": 2.1,
      "severity": "high",
      "description": "Fraud rate exceeds baseline..."
    }
  ]
}
```

**Key Points**:
- Runs once after Agent 1 completes
- Uses statistics (mean, std dev, z-scores)
- All math is deterministic
- No invented data, just aggregation

---

## 💡 Agent 3: Enhanced Action

**File**: `agents/action_enhanced.py`

**What It Does**: Converts insights into actionable recommendations

**Example Walkthrough**:

```
INPUT:
From Agent 2:
{
  "pattern": "Customers at risk of churn",
  "count": 28,
  "percentage": 18.67,
  "z_score": 1.85,
  "significance": 0.78,
  "supporting_returns": ["RET100001", "RET100005", ...]
}

AGENT 3 PROCESSING:

Step 1: Validate Evidence
  ✓ Has significance > 0.5 (has 0.78)
  ✓ Has supporting records (has 28)
  ✓ Has z-score (has 1.85)
  Evidence Status: VALID

Step 2: Calculate Confidence
  Confidence = significance * 1.1
  Confidence = 0.78 * 1.1 = 0.86

Step 3: Determine Review Status
  if Confidence > 0.85:
    Status = "approved" ← AUTO-APPROVE
  elif Confidence > 0.70:
    Status = "pending_review" ← NEEDS HUMAN
  else:
    Status = "insufficient_data" ← MANUAL ONLY

  Result: 0.86 > 0.85 → "approved"

Step 4: Generate Recommendation
  - Title: "Implement Churn Prevention Program"
  - Priority: HIGH (significance > 0.7)
  - Description: Evidence + context
  - Supporting Records: 28 return IDs
  - Human Review: FALSE (high confidence)
  - Impact: "Retain 20-30% of at-risk customers"

OUTPUT:
{
  "recommendation_id": "REC_12345",
  "title": "Implement Churn Prevention Program",
  "priority": "HIGH",
  "confidence": 0.86,
  "status": "approved",
  "human_review_required": false,
  "supporting_records": ["RET100001", "RET100005", ...],
  "description": "Identified 28 customers at high churn risk...",
  "estimated_impact": "Retain 20-30% of at-risk customers",
  "required_action": "Launch targeted retention campaign..."
}
```

**Review Status Decision Tree**:
```
Confidence Score?
│
├─ > 0.85 ──→ AUTO-APPROVED (high evidence)
│
├─ 0.70-0.85 ──→ PENDING REVIEW (human decides)
│
└─ < 0.50 ──→ INSUFFICIENT DATA (manual only)
```

**Key Points**:
- Evidence must be validated before recommendation
- Confidence threshold determines review routing
- All recommendations include supporting return IDs (PII masked)
- Human review required for medium confidence

---

## 🤖 Chatbot Agent (Bonus)

**File**: `agents/chatbot.py`

**What It Does**: Answers questions using Claude API with analysis context

```
USER INTERACTION:

User: "Which SKU has the worst return rate?"

Chatbot System Prompt includes:
1. Current data from Agents 1-3
2. Historical context from RAG
3. Constraints: "Only cite calculated evidence"

Claude Response:
"SKU-101 has the highest return rate at 22 returns (14.67% of total).
This is statistically significant (z-score: 2.1).

Looking at historical data, SKU-101 has appeared in 3 previous analyses
with consistently high return rates, primarily for sizing issues.

Recommended action: Review sizing guide and consider product improvements.
This recommendation requires human approval before implementation."
```

**Key Points**:
- Uses evidence from Agents 1-3
- Adds historical context via RAG
- Claude explains, doesn't invent
- Helps humans understand the data

---

## 📈 All 6 Supporting Files

| File | Purpose | Used By |
|------|---------|---------|
| `models.py` | Data structure definitions | All agents |
| `understanding.py` | Agent 1 logic | Orchestrator |
| `insight.py` | Agent 2 logic | Orchestrator |
| `action_enhanced.py` | Agent 3 logic | Orchestrator |
| `orchestrator.py` | Coordinates agents 1-3 | API |
| `chatbot.py` | Claude-powered Q&A | API |
| `historical_store.py` | Persistence layer | Agent 3 + RAG |
| `rag_retriever.py` | Historical context lookup | Chatbot + Agent 3 |

---

## 🎯 Key Insight: Evidence Trail

Every recommendation has a traceable evidence path:

```
Recommendation Created ◄── Agent 3
   │
   ├─ Why? ◄── Agent 2 (Trend/Anomaly data)
   │   │
   │   └─ From where? ◄── Agent 1 (Classifications)
   │       │
   │       └─ Based on what? ◄── Return records (SKU, reason, refund)
   │
   └─ Supporting records? ◄── Return IDs (RET100001, RET100005, ...)
```

This means every recommendation is auditable and explainable!

---

## 🔄 Typical Execution Time

```
Agent 1 (150 returns):    ~0.5 seconds
Agent 2 (aggregation):    ~0.2 seconds  
Agent 3 (recommendations):~0.3 seconds
Total:                    ~1 second

All in memory, no external API calls needed
(except Chatbot, which uses Claude API on demand)
```

---

## 💻 Running Agents Directly

### Test Agent 1 Only
```python
from agents.understanding import UnderstandingAgent
from agents.models import ReturnRecord

agent = UnderstandingAgent()
return_record = ReturnRecord(
    return_id="RET001",
    sku="SKU-101", 
    reason="Too small",
    # ...
)
result = agent._analyze_return(return_record)
print(result.classification)  # SIZE_FIT
```

### Test Agent 2 Only
```python
from agents.insight import InsightAgent

agent = InsightAgent()
insight_result = agent.analyze(returns, understanding_results)
for trend in insight_result.trends:
    print(f"{trend.pattern}: {trend.count} returns")
```

### Test Agent 3 Only
```python
from agents.action_enhanced import EnhancedActionAgent

agent = EnhancedActionAgent()
action_result, review_data = agent.generate_recommendations(
    returns, understanding_results, insight_result
)
for rec in action_result.recommendations:
    print(f"{rec.title}: {rec.status}")
```

---

## 🎓 Common Questions

**Q: Why 3 agents?**
A: Separation of concerns - each handles one task (classify, aggregate, recommend)

**Q: Why not just use Claude for everything?**
A: We need deterministic, auditable evidence. Claude explains the evidence, doesn't invent it.

**Q: How does RAG help?**
A: It gives Claude historical context to make better explanations without inventing data.

**Q: What if confidence is low?**
A: Recommendation is flagged for human review. Humans have final say.

**Q: Can I change the confidence thresholds?**
A: Yes! Edit `CONFIDENCE_THRESHOLD_AUTO` in `action_enhanced.py`

**Q: How do I add more return reasons?**
A: Edit keyword lists in `understanding.py` classification methods

---

**For more details, see [ARCHITECTURE.md](ARCHITECTURE.md)**
