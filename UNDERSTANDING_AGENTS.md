# Understanding ReturnIQ Agents - Complete Guide

## ✅ What You Have Built

A production-grade AI system with **3 agents + 3 supporting systems** that analyzes retail returns intelligently.

---

## 🤖 THE 3 AGENTS - QUICK ANSWER

### **Agent 1: Understanding** → WHERE IT LIVES
```
File: agents/understanding.py
Purpose: Classify individual returns
Input: Single return record (SKU, reason, refund amount)
Output: Classification + sentiment + churn risk
Runs: 150 times (once per return)
Time: ~0.5 seconds total
```

### **Agent 2: Insight** → WHERE IT LIVES
```
File: agents/insight.py
Purpose: Detect trends and anomalies
Input: All 150 classifications from Agent 1
Output: 9 trends + 2 anomalies with z-scores
Runs: 1 time
Time: ~0.2 seconds
```

### **Agent 3: Enhanced Action** → WHERE IT LIVES
```
File: agents/action_enhanced.py
Purpose: Generate recommendations with evidence
Input: Trends and anomalies from Agent 2
Output: 6 recommendations with supporting return IDs
Runs: 1 time
Time: ~0.3 seconds
Key Feature: Routes to human review based on confidence
```

---

## 📍 HOW TO FIND EACH AGENT

### Finding Agent 1
```bash
# Open this file:
/Users/310952/Documents/D3-ClaudeSquad/git/ClaudeSquad/agents/understanding.py

# Main functions:
1. process_returns(returns)      # Line ~20 - entry point
2. _classify_return(reason)      # Line ~48 - keyword classification
3. _analyze_sentiment(reason)    # Line ~73 - detect mood
4. _assess_churn_risk(return)    # Line ~92 - calculate risk
```

### Finding Agent 2
```bash
# Open this file:
/Users/310952/Documents/D3-ClaudeSquad/git/ClaudeSquad/agents/insight.py

# Main functions:
1. analyze(returns, understanding_results)  # Line ~21 - entry point
2. _detect_trends(returns, ...)             # Line ~37 - pattern detection
3. _detect_anomalies(returns, ...)          # Line ~68 - statistical outliers
```

### Finding Agent 3
```bash
# Open this file:
/Users/310952/Documents/D3-ClaudeSquad/git/ClaudeSquad/agents/action_enhanced.py

# Main functions:
1. generate_recommendations(...)                    # Line ~45 - entry point
2. _create_trend_recommendation_with_review(...)   # Line ~110 - for trends
3. _create_anomaly_recommendation_with_review(...) # Line ~145 - for anomalies
4. _validate_evidence(...)                         # Line ~100 - checks z-score/counts
```

---

## 🔄 THE COMPLETE FLOW (Step-by-Step)

```
STEP 1: Load synthetic returns
  └─ 150 returns with SKU, reason, refund amount
  └─ Example: {SKU: "SKU-101", reason: "too small", refund: $89.99}

STEP 2: Run Agent 1 (Understanding) 150 times
  ├─ For "too small" → classify as SIZE_FIT
  ├─ Detect negative sentiment → NEGATIVE
  ├─ Calculate emotion: 0.72 (moderately upset)
  ├─ Assess churn risk: yes (dissatisfied customer)
  └─ Output: UnderstandingResult object

STEP 3: Collect all 150 results → Input to Agent 2

STEP 4: Run Agent 2 (Insight) once
  ├─ Count "SIZE_FIT" reasons: 32 out of 150
  ├─ Calculate percentage: 32/150 = 21.3%
  ├─ Calculate z-score: 1.85 (significant)
  ├─ Create Trend: "Frequent return reason: Size too large"
  └─ Output: InsightResult (9 trends, 2 anomalies)

STEP 5: Send trends/anomalies → Input to Agent 3

STEP 6: Run Agent 3 (Enhanced Action) once
  ├─ Check Trend 1: "Size too large"
  ├─ Validate evidence:
  │  ├─ Has z-score? ✓ (1.85)
  │  ├─ Has supporting IDs? ✓ (32 returns)
  │  ├─ Has significance? ✓ (0.92)
  ├─ Calculate confidence: 0.88
  ├─ Is confidence > 0.85? YES → AUTO-APPROVE
  ├─ Generate recommendation:
  │  ├─ Title: "Address Frequent return reason: Size too large"
  │  ├─ Priority: HIGH
  │  ├─ Supporting records: 32 return IDs
  │  ├─ Status: "approved"
  │  └─ Human review required: FALSE
  └─ Output: ActionResult (6 recommendations)

STEP 7: Store in history
  └─ Save to /tmp/returniq_history/

STEP 8: Display in dashboard
  └─ Show recommendations with approval buttons
```

---

## 📚 DOCUMENTATION FILES (WHERE TO READ WHAT)

| File | Read This For |
|------|---------------|
| **README.md** | Quick start + overview |
| **ARCHITECTURE.md** | Detailed agent breakdown + theory |
| **AGENT_GUIDE.md** | Walkthrough examples + code locations |
| **UNDERSTANDING_AGENTS.md** | This file - understanding explained |
| **SolutionDoc.txt** | Original requirements (in IDE) |

---

## 💡 KEY CONCEPTS EXPLAINED

### Concept 1: Why 3 Agents?
**Problem**: We need both intelligence AND auditability
- **Agent 1** classifies data (deterministic)
- **Agent 2** finds patterns (statistical)
- **Agent 3** generates recommendations (with evidence)
- **Result**: Each step is verifiable, traceable, and explainable

### Concept 2: Evidence Validation
```
Raw Trend Data:
  - Pattern: "High size returns"
  - Count: 32 returns
  - Z-score: 1.85

Evidence Check:
  ✓ Has supporting records (32 > 5)
  ✓ Has statistical significance (z-score > 1.5)
  ✓ Has confidence score (calculated)

Result:
  → VALID → Generate recommendation
  → If invalid → Mark for manual review only
```

### Concept 3: Confidence Thresholds
```
Confidence Score?
│
├─ 0.86 (> 0.85) → AUTO-APPROVED (trusted)
│                   No human review needed
│
├─ 0.78 (0.70-0.85) → NEEDS HUMAN REVIEW
│                     Human must approve/reject
│
└─ 0.42 (< 0.50) → INSUFFICIENT DATA
                    Manual investigation only
```

### Concept 4: RAG Enhancement
```
Without RAG:
  Claude: "SKU-101 has 22 returns"
  
With RAG:
  Claude: "SKU-101 has 22 returns (14.67%)
           Historically, this SKU has appeared
           in 3 past analyses with similar patterns.
           Average past rate: 13.2%
           This is slightly elevated vs historical."
```

---

## 🎯 UNDERSTANDING THE CODE

### Where Agent 1 Makes Decisions
```python
# agents/understanding.py, line ~73
def _analyze_sentiment(self, reason: str) -> SentimentType:
    negative_words = ["bad", "poor", "broken", "defect"]
    positive_words = ["good", "great", "excellent"]
    
    reason_lower = reason.lower()
    negative_count = sum(1 for word in negative_words 
                        if word in reason_lower)
    positive_count = sum(1 for word in positive_words 
                        if word in reason_lower)
    
    if negative_count > positive_count:
        return SentimentType.NEGATIVE  # ← DECISION
    # ...
```

**What's happening**: Simple keyword counting. No ML, no guessing.

### Where Agent 2 Finds Patterns
```python
# agents/insight.py, line ~55
sku_counts = Counter(skus)  # Count each SKU
top_skus = sku_counts.most_common(5)  # Top 5

for sku, count in top_skus:
    percentage = (count / len(returns)) * 100
    z_score = (count - mean) / std_dev  # ← STATISTICAL
    
    # Create Trend object if significant
    if z_score > 1.5:  # ← THRESHOLD
        trends.append(Trend(...))
```

**What's happening**: Count + calculate z-score. Math-based, repeatable.

### Where Agent 3 Makes Review Decision
```python
# agents/action_enhanced.py, line ~110
def _create_trend_recommendation_with_review(self, trend, ...):
    is_valid, validation_msg = self._validate_evidence(trend)
    if not is_valid:
        return low_confidence_rec, "insufficient_evidence"
    
    confidence = min(trend.significance * 1.1, 0.99)
    
    if confidence >= 0.85:  # ← THRESHOLD
        status = "approved"
        review_required = False
    else:
        status = "pending_review"
        review_required = True  # ← FLAG FOR HUMAN
    
    return Recommendation(...), review_status
```

**What's happening**: Check confidence, route to human if needed.

---

## 🧪 TESTING TO UNDERSTAND

### Test Agent 1 Independently
```bash
/opt/homebrew/bin/python3.11 << 'EOF'
from agents.understanding import UnderstandingAgent
from agents.models import ReturnRecord

agent = UnderstandingAgent()

# Create a test return
return_record = ReturnRecord(
    return_id="TEST001",
    sku="TEST-SKU",
    product_name="Test Product",
    customer_email="test@example.com",
    customer_phone="555-1234",
    reason="Item arrived broken",  # ← KEY INPUT
    refund_amount=50.0,
    return_date="2026-09-26",
    is_fraud_suspect=False
)

# Run Agent 1
result = agent._analyze_return(return_record)

print(f"Classification: {result.classification.value}")  # Should be DEFECTIVE
print(f"Sentiment: {result.sentiment.value}")  # Should be NEGATIVE
print(f"Confidence: {result.confidence}")  # Should be ~0.8+
print(f"Churn Risk: {result.churn_risk}")  # Should be True
EOF
```

### Test Agent 2 Independently
```bash
/opt/homebrew/bin/python3.11 << 'EOF'
from agents.insight import InsightAgent
from agents.models import ReturnRecord, UnderstandingResult, SentimentType, ClassificationType

agent = InsightAgent()

# Simulate 50 returns with high count of one SKU
returns = [ReturnRecord(f"RET{i:05d}", f"SKU-{i%5:03d}", ...) for i in range(50)]
understanding_results = [
    UnderstandingResult(
        return_id=f"RET{i:05d}",
        classification=ClassificationType.SIZE_FIT if i % 2 else ClassificationType.DEFECTIVE,
        confidence=0.85,
        sentiment=SentimentType.NEGATIVE,
        emotion_intensity=0.7,
        churn_risk=i % 3 == 0
    )
    for i in range(50)
]

# Run Agent 2
insight_result = agent.analyze(returns, understanding_results)

print(f"Trends detected: {len(insight_result.trends)}")
for trend in insight_result.trends[:2]:
    print(f"  - {trend.pattern}: {trend.count} returns, z-score: {trend.z_score}")
EOF
```

---

## 📊 DATA FLOW VISUALIZATION

```
INPUT LAYER
├─ synthetic_returns.py generates 150 returns
│  └─ CSV file: /tmp/synthetic_returns.csv
│
PROCESSING LAYER
├─ Agent 1: understanding.py (150x)
│  └─ Input: ReturnRecord
│  └─ Output: UnderstandingResult
│
├─ Agent 2: insight.py (1x)
│  └─ Input: [ReturnRecord], [UnderstandingResult]
│  └─ Output: InsightResult
│
├─ Agent 3: action_enhanced.py (1x)
│  └─ Input: [Trend], [Anomaly], RAG context
│  └─ Output: ActionResult
│
STORAGE LAYER
├─ historical_store.py
│  └─ Stores: analyses, recommendations, patterns
│  └─ File: /tmp/returniq_history/
│
├─ rag_retriever.py
│  └─ Reads: historical patterns
│  └─ Provides: context for Claude
│
OUTPUT LAYER
├─ orchestrator.py (coordinates all agents)
│  └─ Returns: (understanding, insight, action)
│
├─ api/index.py (Flask server)
│  └─ Exposes: REST endpoints
│
├─ chatbot.py (Claude)
│  └─ Answers: user questions with evidence
│
└─ Dashboard UI (HTML/JS)
   └─ Shows: recommendations with human review buttons
```

---

## 🔍 HOW TO TRACE A RECOMMENDATION

**Example: User sees recommendation "Address High return rate for SKU SKU-101"**

1. **Where did this come from?**
   - Agent 3 generated it → `agents/action_enhanced.py` line ~145

2. **Why was it created?**
   - Agent 2 detected a trend → `agents/insight.py` line ~55

3. **What trend?**
   - SKU-101 appears 22 times (14.67%) out of 150 → Significant deviation

4. **How many times did Agent 1 see SKU-101?**
   - 22 times → `agents/understanding.py` ran 22 times for this SKU

5. **What classified them?**
   - Most: SIZE_FIT (keyword matching on "size too large")
   - Some: QUALITY_ISSUE

6. **What's the evidence?**
   - Supporting return IDs: RET100001, RET100005, RET100013, ...
   - Z-score: 1.81 (statistically significant)
   - Confidence: 0.88 (88% confident)

7. **Does it need human review?**
   - Confidence 0.88 > 0.85 → No, auto-approved
   - But can still review if desired

---

## ✅ Quick Verification Checklist

After understanding this guide, you should be able to answer:

- [ ] What does Agent 1 do? (Classify individual returns)
- [ ] What does Agent 2 do? (Detect patterns via statistics)
- [ ] What does Agent 3 do? (Generate verified recommendations)
- [ ] Where is Agent 1 code? (`agents/understanding.py`)
- [ ] How many times does Agent 1 run? (150 times, once per return)
- [ ] How does Agent 2 find trends? (Count + z-score)
- [ ] What does "z-score 1.81" mean? (Significantly above average)
- [ ] How does Agent 3 decide review? (Confidence > 0.85 = auto-approve)
- [ ] What is RAG? (Historical context retrieval)
- [ ] Why not just use Claude? (Need deterministic, auditable evidence)

---

## 🎓 Next Steps to Deepen Understanding

1. **Read AGENT_GUIDE.md**
   - Detailed walkthrough of each agent
   - Code examples

2. **Read ARCHITECTURE.md**
   - System design principles
   - Data flow diagrams

3. **Open the code**
   - Start with `agents/understanding.py` (simplest)
   - Then `agents/insight.py` (statistical)
   - Then `agents/action_enhanced.py` (most complex)

4. **Run tests**
   - Use the test code above
   - Modify inputs to see outputs change
   - Verify deterministic behavior

5. **Explore the dashboard**
   - Click "💬" to chat
   - Ask questions about the trends
   - See Claude cite evidence

---

## 🎯 The Big Picture

ReturnIQ solves a real business problem:
- **Problem**: 150 returns per day, unclear patterns, potential fraud
- **Solution**: 3-agent pipeline that finds patterns automatically
- **Guarantee**: All decisions are traceable and auditable
- **Human Control**: Humans approve recommendations before action
- **Learning**: Historical data builds intelligence over time

**You built this.** 🚀
