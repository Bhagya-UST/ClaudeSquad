# ReturnIQ - AI-Powered Retail Returns Intelligence

**D3 Hackathon 2026 Solution**

ReturnIQ is a production-ready system that analyzes retail returns using a 3-agent pipeline with human review workflow, RAG-enhanced context, and AI-powered insights.

---

## 🎯 Quick Start

### 1️⃣ Install Dependencies
```bash
/opt/homebrew/bin/python3.11 -m pip install -r requirements.txt
```

### 2️⃣ Set API Key
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### 3️⃣ Run the Server
```bash
cd /Users/310952/Documents/D3-ClaudeSquad/git/ClaudeSquad
/opt/homebrew/bin/python3.11 api/index.py
```

### 4️⃣ Open Dashboard
```
http://localhost:5000
```

---

## 🤖 Agent Architecture

ReturnIQ uses **3 Core Analysis Agents + 3 Supporting Systems**:

### **3 Core Agents** (Sequential Pipeline)
| Agent | Purpose | Files | Output |
|-------|---------|-------|--------|
| 🧠 **Agent 1: Understanding** | Classify returns + detect sentiment | `agents/understanding.py` | Classification, sentiment, churn risk |
| 🔍 **Agent 2: Insight** | Detect trends + anomalies | `agents/insight.py` | Trends (9 detected), anomalies (statistical) |
| 💡 **Agent 3: Enhanced Action** | Generate verified recommendations | `agents/action_enhanced.py` | Recommendations with evidence + review status |

### **3 Supporting Systems**
| System | Purpose | Files |
|--------|---------|-------|
| 🤖 **Chatbot Agent** | Answer questions using Claude API | `agents/chatbot.py` |
| 💾 **Historical Store** | Persist analyses for trend tracking | `agents/historical_store.py` |
| 🔗 **RAG Retriever** | Retrieve historical context | `agents/rag_retriever.py` |

**→ See [`ARCHITECTURE.md`](ARCHITECTURE.md) for detailed explanation**

---

## 📊 Pipeline Flow

```
Synthetic Returns (150)
    ↓
[AGENT 1] Understand each return
    ↓ 150 classifications
[AGENT 2] Detect patterns & anomalies
    ↓ 9 trends, 2 anomalies  
[AGENT 3] Generate recommendations
    ↓ 6 recommendations with evidence
[CHATBOT] Answer questions with RAG context
    ↓
[DASHBOARD] Human reviews & approves
```

---

## ✨ Key Features

### 🎯 Real Retail Outcome
- Identifies high-return SKUs (e.g., SKU-101: 22 returns, 14.67%)
- Detects churn risk (28 customers at risk)
- Flags fraud suspects (11 suspicious returns)
- Suggests actionable improvements

### 🔐 Evidence-Based
- ✅ All recommendations have supporting return IDs
- ✅ Z-scores and significance metrics calculated
- ✅ Confidence thresholds enforce human review
- ✅ Claude explains evidence (doesn't invent it)

### 👥 Human Review Workflow
```
Confidence > 0.85
    ↓
[Auto-Approved] → Dashboard
    
Confidence 0.70-0.85
    ↓
[Pending Review] → Human clicks "Approve" or "Reject"
    
Confidence < 0.50
    ↓
[Manual Only] → Flag for investigation
```

### 📈 RAG Enhancement
- Stores historical analyses
- Compares current trends against baselines
- Retrieves similar past recommendations
- Enriches Claude's responses with context

---

## 📁 File Structure

```
ClaudeSquad/
├── agents/
│   ├── __init__.py
│   ├── models.py              # Data models
│   ├── understanding.py       # Agent 1: Classification
│   ├── insight.py             # Agent 2: Trends/Anomalies
│   ├── action_enhanced.py     # Agent 3: Recommendations
│   ├── orchestrator.py        # Coordinates agents
│   ├── chatbot.py             # Claude-powered assistant
│   ├── historical_store.py    # Stores analysis history
│   └── rag_retriever.py       # RAG context retrieval
│
├── api/
│   └── index.py               # Flask backend
│
├── public/
│   └── index.html             # Dashboard UI
│
├── synthetic_returns.py       # Demo data generator
├── requirements.txt           # Dependencies
├── ARCHITECTURE.md            # Detailed agent guide
└── README.md                  # This file
```

---

## 🚀 API Endpoints

### Analysis Endpoints
```
GET /api/analysis/overview         # Key metrics
GET /api/analysis/recommendations  # With supporting records
GET /api/analysis/trends           # Historical patterns
GET /api/analysis/anomalies        # Detected anomalies
```

### Review Workflow
```
GET /api/review/pending            # Pending human reviews
POST /api/review/approve           # Approve with notes
POST /api/review/reject            # Reject with notes
```

### Historical & RAG
```
GET /api/historical/context        # Baseline metrics
GET /api/historical/trends?pattern=SKU-101
GET /api/historical/anomalies?category=Fraud
POST /api/rag/context              # Build RAG context
```

### Chatbot
```
POST /api/chat                     # Send message
GET /api/chat/suggestions          # Suggested questions
POST /api/chat/reset               # Clear history
```

---

## 💡 Example Output

### Recommendation with Evidence
```json
{
  "id": "REC_37290",
  "title": "Address High return rate for SKU SKU-106",
  "priority": "HIGH",
  "confidence": 0.88,
  "status": "pending_review",
  "requires_review": true,
  "supporting_records": [
    "RET100001", "RET100005", "RET100013", 
    "RET100017", "RET100023"
  ],
  "description": "Pattern detected in 22 returns (14.67% of total). Significance: 0.60 (z-score: 1.81). Supporting evidence: 5 return records.",
  "estimated_impact": "5-15% reduction in returns",
  "required_action": "Review affected products and implement mitigation"
}
```

### Chatbot with RAG
```
User: "Why is SKU-101 returning so much?"

Claude: "SKU-101 has 22 returns (14.67% of total), significantly above baseline.
The primary reason is sizing issues (9 returns). 

Historically, this SKU has appeared in 3 past analyses with consistent sizing problems.
Z-score: 1.81, indicating statistically significant elevation.

Recommendation: Review sizing guide or consider fit improvements.
This recommendation requires human approval before implementation."
```

---

## 🧪 Testing

### Quick Test (No API Key Needed)
```bash
cd /Users/310952/Documents/D3-ClaudeSquad/git/ClaudeSquad
/opt/homebrew/bin/python3.11 << 'EOF'
from agents.orchestrator import ReturnIQOrchestrator
from synthetic_returns import generate_returns_csv
import pandas as pd

# Generate data
csv_path = "/tmp/test_returns.csv"
generate_returns_csv(num_returns=50, output_path=csv_path)

# Process
orch = ReturnIQOrchestrator()
df = pd.read_csv(csv_path)
understanding, insight, action = orch.process_returns(df)

print(f"✓ Trends: {len(insight.trends)}")
print(f"✓ Anomalies: {len(insight.anomalies)}")
print(f"✓ Recommendations: {len(action.recommendations)}")
EOF
```

---

## 🏗️ Architecture Principles

### "Claude Explains Evidence, Doesn't Invent It"
1. **Agents 1-2** calculate all evidence (deterministic Python)
2. **Agent 3** validates evidence against thresholds
3. **Chatbot** cites calculated metrics, not invented data
4. **Human review** required for final decisions

### Three Levels of Evidence
| Level | Confidence | Status | Human Action |
|-------|-----------|--------|--------------|
| High | > 0.85 | Auto-approved | Monitor |
| Medium | 0.70-0.85 | Pending review | Approve/Reject |
| Low | < 0.50 | Insufficient data | Investigate |

---

## 🎓 Understanding Each Agent

### Agent 1: Understanding (Classification)
```
Input: "Item arrived damaged"
       → Matches "damage" keyword
       → Classification: DAMAGE
       → Sentiment: NEGATIVE
       → Emotion Intensity: 0.85
       → Churn Risk: True (damage = dissatisfaction)
```

### Agent 2: Insight (Pattern Detection)
```
Input: 150 classifications from Agent 1
       → Count: SKU-101 appears 22 times
       → Percentage: 22/150 = 14.67%
       → Z-score: 2.1 (significant deviation)
       → Output: TREND detected
```

### Agent 3: Action (Recommendation)
```
Input: Trend with z-score=2.1, 5 supporting records
       → Significance: 0.88 (valid evidence)
       → Confidence > 0.85
       → Status: "approved" (auto-approve)
       → Human Review: Not required (high confidence)
       → Output: Recommendation with evidence trail
```

---

## 🔧 Configuration

### To Change Data Size
Edit `synthetic_returns.py`:
```python
generate_returns_csv(num_returns=300)  # Change 150 to 300
```

### To Adjust Confidence Thresholds
Edit `agents/action_enhanced.py`:
```python
CONFIDENCE_THRESHOLD_AUTO = 0.85    # Auto-approve threshold
CONFIDENCE_THRESHOLD_REVIEW = 0.70  # Review threshold
CONFIDENCE_THRESHOLD_REJECT = 0.50  # Reject threshold
```

---

## 📝 Solution Highlights

✅ **Specific Retail Outcome**: Analyzes 150 returns to identify high-risk SKUs and churn patterns
✅ **Actionable Recommendations**: Each rec has supporting evidence (return IDs, z-scores)
✅ **Human Review Workflow**: Auto-approve, pending review, or manual only based on confidence
✅ **RAG Integration**: Historical context enriches every analysis
✅ **Claude Explains Evidence**: No invented data, only calculated metrics
✅ **Hackathon-Ready**: Deployable, auditable, production-grade

---

## 📖 More Information

- **Detailed Architecture**: See [`ARCHITECTURE.md`](ARCHITECTURE.md)
- **Agent Definitions**: See `agents/*.py` files
- **API Reference**: See `api/index.py`
- **Data Models**: See `agents/models.py`

---

## 🤝 Support

For questions about:
- **Agents**: Read `ARCHITECTURE.md`
- **API**: Check `api/index.py` 
- **Data**: See `agents/models.py`
- **Flow**: Read this README

---

**Made with ❤️ for D3 Hackathon 2026**
