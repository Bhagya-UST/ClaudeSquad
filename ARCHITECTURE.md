# ReturnIQ Agent Architecture

## 🤖 Agent Overview

ReturnIQ uses a **3-Agent Pipeline** with supporting systems. Each agent has a specific responsibility.

---

## **AGENT 1: Understanding Agent**
**File:** [`agents/understanding.py`](agents/understanding.py)

### Purpose
Analyzes individual returns to classify and understand customer sentiment.

### Input
- Single return record with: SKU, reason, customer info, refund amount, fraud indicator

### Processing (Deterministic)
```python
1. Classify return reason → ClassificationType
   - Keyword matching on reason text
   - Returns: DEFECTIVE, SIZE_FIT, DAMAGE, QUALITY_ISSUE, WRONG_ITEM, etc.

2. Analyze sentiment → SentimentType
   - Keyword counting (negative/positive words)
   - Returns: POSITIVE, NEUTRAL, NEGATIVE

3. Calculate emotion intensity → Float (0-1)
   - Based on sentiment strength
   
4. Assess churn risk → Boolean
   - Risk factors: fraud, high refund, quality issues
   - Returns: True if customer likely to churn

5. Calculate confidence → Float (0-1)
   - Higher if reason text exists and classification is specific
```

### Output
```json
{
  "return_id": "RET100001",
  "classification": "SIZE_FIT",
  "confidence": 0.92,
  "sentiment": "NEGATIVE",
  "emotion_intensity": 0.72,
  "churn_risk": true,
  "risk_score": 0.85
}
```

### Key Code
```python
understanding_results = understanding_agent.process_returns(returns)
# Returns: List[UnderstandingResult] - one per return record
```

---

## **AGENT 2: Insight Agent**
**File:** [`agents/insight.py`](agents/insight.py)

### Purpose
Aggregates individual analyses to detect patterns and anomalies.

### Input
- All return records
- All understanding results from Agent 1

### Processing (Statistical, Deterministic)
```python
1. Detect Trends:
   - Count SKUs by frequency
   - Count return reasons by frequency
   - Count churn risk customers
   - Calculate: percentage, z-score, significance

2. Detect Anomalies:
   - High refund amounts (>2σ from mean)
   - Elevated fraud rate (vs baseline 5%)
   - High negative sentiment (vs baseline 30%)
   - Calculate: z-score, severity
```

### Output
```json
{
  "trends": [
    {
      "pattern": "High return rate for SKU SKU-101",
      "count": 18,
      "percentage": 12.4,
      "significance": 0.85,
      "z_score": 2.1,
      "supporting_returns": ["RET100001", "RET100005", ...]
    }
  ],
  "anomalies": [
    {
      "category": "Elevated Fraud Risk",
      "value": 9,
      "expected": 7.2,
      "z_score": 2.5,
      "severity": "high",
      "description": "Fraud suspect rate exceeds baseline"
    }
  ]
}
```

### Key Code
```python
insight_result = insight_agent.analyze(returns, understanding_results)
# Returns: InsightResult with trends and anomalies
```

---

## **AGENT 3: Enhanced Action Agent**
**File:** [`agents/action_enhanced.py`](agents/action_enhanced.py)

### Purpose
Generates recommendations with evidence validation and human review routing.

### Input
- All returns, understanding results, and insights
- Historical context (via RAG)

### Processing (Evidence-Based)
```python
1. Validate Evidence:
   ✓ Has statistical significance (z-score > 1.5)
   ✓ Has supporting records (e.g., 5+ return IDs)
   ✓ Not enough evidence → LOW confidence, mark for review

2. Route by Confidence:
   Confidence > 0.85 → "approved" (auto-approved)
   Confidence 0.70-0.85 → "pending_review" (needs human)
   Confidence < 0.50 → "insufficient_data" (manual only)

3. Generate Recommendation:
   - title: Actionable statement
   - description: Evidence + impact
   - supporting_records: Return IDs (PII masked)
   - priority: Based on significance
   - human_review_required: Boolean flag
```

### Output
```json
{
  "recommendation_id": "REC_37290",
  "title": "Address High return rate for SKU SKU-101",
  "priority": "HIGH",
  "confidence": 0.88,
  "status": "pending_review",
  "human_review_required": true,
  "supporting_records": ["RET100001", "RET100005", ...],
  "estimated_impact": "5-15% reduction in returns",
  "required_action": "Review and mitigate quality issues"
}
```

### Key Code
```python
action_result, review_data = action_agent.generate_recommendations(
    returns, understanding_results, insight_result
)
# Returns: (ActionResult with recommendations, review workflow data)
```

---

## **SUPPORTING SYSTEM 1: Chatbot Agent**
**File:** [`agents/chatbot.py`](agents/chatbot.py)

### Purpose
Answers questions using Claude API with current analysis as context.

### Key Features
- ✅ Uses RAG context automatically
- ✅ Explains evidence (doesn't invent it)
- ✅ Conversation history tracking
- ✅ Suggested questions based on trends

### Input
- User question

### Output
- Claude-generated response with evidence citations

### Constraints
- **CRITICAL**: Claude explains the calculated evidence, doesn't invent evidence
- Uses trends/anomalies from Agents 1-3 as ground truth
- Can only answer based on historical/current data

---

## **SUPPORTING SYSTEM 2: Historical Store**
**File:** [`agents/historical_store.py`](agents/historical_store.py)

### Purpose
Stores analysis results for trend analysis and RAG retrieval.

### What It Stores
```
1. analysis_log.jsonl
   - Every analysis run with timestamp
   - Trends, anomalies, churn/fraud counts

2. recommendations.jsonl
   - Every recommendation generated
   - Status, confidence, human review notes

3. patterns.json
   - Recurring patterns across time
```

### Methods
```python
store.store_analysis(timestamp, analysis_data)
store.get_trend_history(pattern)          # Past occurrences of trend
store.get_anomaly_history(category)       # Past anomalies
store.get_similar_recommendations(title)  # Previous similar recs
store.get_historical_context()            # Baseline metrics
```

---

## **SUPPORTING SYSTEM 3: RAG Retriever**
**File:** [`agents/rag_retriever.py`](agents/rag_retriever.py)

### Purpose
Retrieves historical context to enhance Claude's understanding.

### What It Retrieves
1. **Baseline Context**: Average churn risk, fraud rate
2. **Trend History**: Past occurrences of current trends
3. **Anomaly History**: Similar past anomalies
4. **Similar Recommendations**: What worked before

### How It's Used
```python
rag_context = rag_retriever.build_rag_context(trends, anomalies, titles)
# Passed to Claude in chatbot system prompt
# Also used by Action Agent for recommendation enrichment
```

---

## **ORCHESTRATOR: Agent Coordinator**
**File:** [`agents/orchestrator.py`](agents/orchestrator.py)

### Purpose
Coordinates all agents and pipelines.

### Pipeline Flow
```
Returns DataFrame
    ↓
Understanding Agent (classify each return)
    ↓
Insight Agent (aggregate & detect patterns)
    ↓
Enhanced Action Agent (generate verified recommendations)
    ↓
Store in History
    ↓
Chatbot Agent (ready to answer questions)
```

### Code
```python
orchestrator = ReturnIQOrchestrator()
understanding, insight, action = orchestrator.process_returns(df)
```

---

## **Data Models**
**File:** [`agents/models.py`](agents/models.py)

All data structures:
- `ReturnRecord` - Input data
- `UnderstandingResult` - Agent 1 output
- `Trend`, `Anomaly`, `InsightResult` - Agent 2 output
- `Recommendation`, `ActionResult` - Agent 3 output
- `MetricsSnapshot` - Performance metrics

---

## **Visual Architecture**

```
┌─────────────────────────────────────────────────────────┐
│                   Synthetic Return Data                  │
│              (150 returns with SKU, reason, etc)         │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────▼───────────────┐
        │   AGENT 1: Understanding     │
        │   (Classification + Sentiment)│
        │   File: understanding.py     │
        └──────────────┬────────────────┘
                       │
                       ▼ (150 UnderstandingResults)
        ┌──────────────────────────────┐
        │   AGENT 2: Insight           │
        │   (Trends + Anomalies)       │
        │   File: insight.py           │
        └──────────────┬────────────────┘
                       │
                       ▼ (9 Trends, 2 Anomalies)
        ┌──────────────────────────────────────┐
        │  AGENT 3: Enhanced Action            │
        │  (Recommendations + Review Routing)  │
        │  File: action_enhanced.py            │
        └──────────────┬───────────────────────┘
                       │
        ┌──────────────┴──────────────────┐
        │                                 │
        ▼ (6 Recommendations)         ▼ (RAG Context)
    ┌──────────────┐          ┌──────────────────┐
    │  Review      │          │  Historical      │
    │  Workflow    │          │  Store + RAG     │
    └──────────────┘          │  Files: .py      │
        │                     └──────────────────┘
        ▼ (Human approval)          │
    ┌──────────────┐                ▼
    │  Dashboard   │        ┌──────────────────┐
    │  + Chatbot   │◄───────│  Chatbot Agent   │
    │  UI (HTML)   │        │  (Claude API)    │
    └──────────────┘        │  File: chatbot.py│
                            └──────────────────┘
```

---

## **How Many Agents? - Summary**

| Agent | File | Role | Input | Output |
|-------|------|------|-------|--------|
| **1. Understanding** | `understanding.py` | Classify returns | Return records | Classification + sentiment |
| **2. Insight** | `insight.py` | Detect patterns | Classifications | Trends + anomalies |
| **3. Action (Enhanced)** | `action_enhanced.py` | Generate recs | Insights | Recommendations + review status |
| **Chatbot** | `chatbot.py` | Answer questions | User input | Claude response |
| **RAG Retriever** | `rag_retriever.py` | Context lookup | Query | Historical context |
| **History Store** | `historical_store.py` | Persist data | Analyses | File storage |

**Total: 3 Core Analysis Agents + 3 Supporting Systems**

---

## **Understanding the Flow**

### **Example: Analyzing 150 Returns**

1. **AGENT 1 runs 150 times** (once per return)
   - "This size complaint → SIZE_FIT classification"
   - "This damage complaint → DEFECTIVE"
   - Result: 150 UnderstandingResults

2. **AGENT 2 runs once** on all 150
   - Count SKU-101: appears 18 times (12.4%)
   - Z-score: 2.1 (significant!)
   - Result: Trend detected + Anomaly detected

3. **AGENT 3 runs once** on insights
   - Trend significance > 0.8 → "high priority"
   - Has supporting records → "approved"
   - Confidence < 0.85 → "needs human review"
   - Result: 6 recommendations with review flags

4. **Chatbot ready**
   - Claude can now explain the trends
   - User asks: "Why is SKU-101 returning so much?"
   - Claude: "18 returns (12.4%), mostly size issues, z-score 2.1, significantly above baseline"

---

## **Key Design Principle**

> **"Claude explains evidence, doesn't invent it"**

- ✅ Agents 1-2 calculate all evidence (deterministic)
- ✅ Agent 3 validates evidence (threshold checks)
- ✅ Chatbot cites evidence from agents
- ✅ Human review required for decisions

This ensures your hackathon solution is **trustworthy, auditable, and actionable**. 🎯
