# ReturnIQ - Complete Technical Documentation

**AI-Powered Return Intelligence Platform**

---

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [AI Agents (9 Total)](#ai-agents)
4. [Database Schema](#database-schema)
5. [API Endpoints](#api-endpoints)
6. [Data Flow](#data-flow)
7. [Deployment](#deployment)

---

## System Architecture

### High-Level Overview

```
┌─────────────────┐
│  React Frontend │
│   (Port 3000)   │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────────────────────────────┐
│         FastAPI Backend                 │
│         (Port 8000)                     │
│  ┌─────────────────────────────────┐   │
│  │  Agent Orchestrator (v2)        │   │
│  │  ┌──────────────────────────┐   │   │
│  │  │ 9 AI Agents (Claude)     │   │   │
│  │  ├─ Classifier             │   │   │
│  │  ├─ Emotional Intelligence │   │   │
│  │  ├─ Root Cause             │   │   │
│  │  ├─ Trend Detection        │   │   │
│  │  ├─ Recommendation Engine  │   │   │
│  │  ├─ Fraud Detection        │   │   │
│  │  ├─ Anomaly Detection      │   │   │
│  │  ├─ Validation             │   │   │
│  │  └─ Human Review           │   │   │
│  └──────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  Hybrid RAG System              │   │
│  │  (Elasticsearch + Embeddings)   │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  Metrics & Observability        │   │
│  │  ┌─ Safety Guardrails        │   │   │
│  │  └─ Metrics Collector          │   │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
         │                │
         │                │
    ┌────▼────┐      ┌────▼──────┐
    │PostgreSQL│      │  Redis    │
    │   DB    │      │  Cache    │
    │(Port    │      │           │
    │ 5432)   │      └───────────┘
    └─────────┘
```

### Component Details

#### 1. **Frontend (React/TypeScript)**
- **Framework**: React 18 with TypeScript
- **Port**: 3000
- **Features**:
  - Real-time dashboard with metrics
  - Return submission form
  - Agent monitoring
  - Trend visualization
  - Customer profiles
  - Recommendation management

#### 2. **Backend (FastAPI)**
- **Framework**: FastAPI with Uvicorn
- **Port**: 8000
- **Features**:
  - REST API with 30+ endpoints
  - JWT authentication
  - Rate limiting (slowapi)
  - CORS middleware
  - Background task processing

#### 3. **Agent Orchestrator**
- **Role**: Central coordinator for all 9 AI agents
- **Responsibilities**:
  - Route returns to appropriate agents
  - Manage agent execution flow
  - Handle agent failures
  - Collect and aggregate results

#### 4. **Database Layer**
- **DBMS**: PostgreSQL 15
- **ORM**: SQLAlchemy
- **Port**: 5432
- **Tables**: 8 core tables (Returns, Classifications, Trends, Recommendations, etc.)

#### 5. **Cache Layer**
- **System**: Redis 7
- **Port**: 6379 (internal only)
- **Uses**: Session caching, metrics storage, request deduplication

#### 6. **Monitoring Stack**
- **Prometheus**: Metrics collection (Port 9090)
- **Grafana**: Dashboards and visualization (Port 3001)
- **Custom Metrics**: API response times, agent performance, business metrics

---

## Technology Stack

### Frontend
```
React 18.2.0                 # UI Framework
TypeScript 5.1.x             # Type Safety
Tailwind CSS 3.x             # Styling
Recharts 2.10.x              # Charts & Visualization
Axios                        # HTTP Client
React Query                  # Data Fetching
```

### Backend
```
FastAPI 0.104.1              # Web Framework
Uvicorn 0.24.0               # ASGI Server
SQLAlchemy 2.0.23            # ORM
Pydantic 2.5.0               # Data Validation
Anthropic SDK 0.25.0+        # Claude API
LangChain 0.1.0              # Agent Framework
redis-py 5.0.1               # Redis Client
elasticsearch-py 8.10.0      # Search Engine
```

### Infrastructure
```
Docker & Docker Compose      # Containerization
PostgreSQL 15                # Primary Database
Redis 7                      # Cache
Prometheus                   # Metrics
Grafana                      # Monitoring UI
```

### Security
```
python-jose 3.3.0            # JWT Tokens
passlib 1.7.4 + bcrypt       # Password Hashing
cryptography 41.0.7          # Encryption
```

---

## AI Agents

### 1. **Classifier Agent**
**Purpose**: Categorize returns into business types

**Input**: Return reason, customer comments, product info
**Output**: 
```json
{
  "category": "Defective Product",
  "confidence": 0.95,
  "reasoning": "Customer reported button stopped working after 2 weeks",
  "sub_categories": ["Mechanical Failure", "Quality Issue"]
}
```
**Algorithm**: Claude 3 with few-shot prompting

---

### 2. **Emotional Intelligence Agent**
**Purpose**: Analyze customer sentiment and churn risk

**Input**: Customer comments, return history
**Output**:
```json
{
  "sentiment_score": -2.5,
  "emotion": "frustrated",
  "intensity": 8,
  "churn_risk": true,
  "churn_risk_score": -4.2,
  "lifecycle_stage": "at_risk"
}
```
**Logic**: Sentiment analysis + churn prediction model

---

### 3. **Root Cause Agent**
**Purpose**: Identify underlying reasons for returns

**Input**: Return details, product specs, manufacturing data
**Output**:
```json
{
  "root_cause": "Manufacturing defect in batch 2024-Q3-001",
  "evidence": ["Serial number range", "Quality control report"],
  "probability": 0.88,
  "recommendation": "Halt production batch immediately"
}
```

---

### 4. **Trend Detection Agent**
**Purpose**: Identify patterns in returns data

**Input**: Historical returns (7-30 days)
**Output**:
```json
{
  "trends": [
    {
      "title": "iPhone 15 Screen Issues",
      "description": "32% of returns mention screen problems",
      "returns_count": 156,
      "percentage": 32,
      "z_score": 3.2,
      "significance": "CRITICAL",
      "evidence_returns": [...]
    }
  ]
}
```
**Algorithm**: Statistical anomaly detection with z-scores

---

### 5. **Recommendation Engine**
**Purpose**: Generate actionable business improvements

**Input**: Trends, returns patterns, financial impact
**Output**:
```json
{
  "recommendations": [
    {
      "text": "Improve quality control in screen assembly process",
      "type": "operational",
      "estimated_impact": 45000,
      "impact_unit": "USD_saved",
      "confidence": 0.92,
      "evidence": ["Trend analysis", "Cost impact data"]
    }
  ]
}
```

---

### 6. **Fraud Detection Agent**
**Purpose**: Identify suspicious return patterns

**Input**: Return details, customer history
**Output**:
```json
{
  "is_fraudulent": false,
  "fraud_score": 0.15,
  "risk_indicators": [
    "First-time customer",
    "High-value item"
  ],
  "recommendation": "Standard processing"
}
```

---

### 7. **Anomaly Detection Agent**
**Purpose**: Find unusual behaviors outside norms

**Input**: Return metrics, customer behavior
**Output**:
```json
{
  "anomalies": [
    {
      "type": "spike",
      "metric": "returns_per_day",
      "current_value": 450,
      "baseline": 280,
      "z_score": 4.1,
      "severity": "HIGH"
    }
  ]
}
```

---

### 8. **Validation Agent**
**Purpose**: Quality check on all agent outputs

**Input**: Outputs from other agents
**Output**:
```json
{
  "is_valid": true,
  "confidence": 0.98,
  "issues": [],
  "warnings": []
}
```

---

### 9. **Human Review Agent**
**Purpose**: Route flagged items for human review

**Input**: Flagged returns, confidence thresholds
**Output**:
```json
{
  "status": "pending_review",
  "priority": "high",
  "assigned_to": "queue",
  "reason": "Low classification confidence (0.65 < 0.70)",
  "suggested_action": "Request additional customer information"
}
```

---

## Database Schema

### Returns Table
```sql
CREATE TABLE returns (
  id UUID PRIMARY KEY,
  customer_id VARCHAR(255) INDEXED,
  product_id VARCHAR(255) INDEXED,
  order_date DATETIME,
  return_date DATETIME,
  return_reason TEXT,
  customer_comments TEXT,
  product_condition VARCHAR(50),
  refund_amount FLOAT,
  created_at DATETIME,
  updated_at DATETIME
);
```

### Classifications Table
```sql
CREATE TABLE classifications (
  id UUID PRIMARY KEY,
  return_id UUID INDEXED,
  category VARCHAR(100),
  confidence FLOAT,
  reasoning TEXT,
  agent_version VARCHAR(50),
  created_at DATETIME
);
```

### Trends Table
```sql
CREATE TABLE trends (
  id UUID PRIMARY KEY,
  title VARCHAR(255),
  description TEXT,
  returns_count INT,
  percentage_of_total FLOAT,
  z_score FLOAT,
  significance_level VARCHAR(20),
  evidence JSON,
  created_at DATETIME
);
```

### Recommendations Table
```sql
CREATE TABLE recommendations (
  id UUID PRIMARY KEY,
  return_id UUID,
  trend_id UUID,
  recommendation_text TEXT,
  recommendation_type VARCHAR(100),
  estimated_impact FLOAT,
  confidence FLOAT,
  evidence JSON,
  status VARCHAR(50),
  validation_status VARCHAR(50),
  approval_date DATETIME,
  implementation_date DATETIME,
  actual_impact FLOAT,
  created_at DATETIME,
  updated_at DATETIME
);
```

### Emotional Intelligence Table
```sql
CREATE TABLE emotional_intelligence (
  id UUID PRIMARY KEY,
  return_id UUID INDEXED,
  sentiment_score FLOAT,
  emotion VARCHAR(50),
  intensity INT,
  churn_risk BOOLEAN,
  churn_risk_score FLOAT,
  lifecycle_stage VARCHAR(50),
  created_at DATETIME
);
```

### Additional Tables
- **audit_logs**: Action audit trail
- **metrics_log**: Time-series metrics
- **MetricsLog**: Performance tracking

---

## API Endpoints

### Authentication
```
POST /api/auth/login
  - Body: username, password
  - Returns: JWT access_token

POST /api/auth/demo-token
  - Returns: Demo JWT token (testing only)

GET /api/auth/me
  - Returns: Current user info
```

### Returns Management
```
POST /api/returns
  - Submit new return for processing
  - Triggers async agent pipeline

GET /api/returns
  - List returns with filters
  - Params: status, classification, skip, limit

GET /api/returns/{return_id}
  - Get complete return analysis
  - Includes all agent outputs
```

### Classification
```
POST /api/classify
  - Run classifier agent on return

GET /api/classify/{return_id}
  - Get classification result
```

### Trends Analysis
```
POST /api/trends/detect
  - Run trend detection on historical data
  - Params: period (weekly/monthly)

GET /api/trends
  - Get top trends
  - Params: period, skip, limit

GET /api/trends/{trend_id}
  - Get trend details with evidence
```

### Recommendations
```
POST /api/recommendations/generate
  - Generate recommendations from trends
  - Params: trend_id or return_id

GET /api/recommendations
  - List recommendations
  - Params: status, skip, limit

POST /api/recommendations/{rec_id}/approve
  - Approve recommendation for implementation

POST /api/recommendations/{rec_id}/implement
  - Mark as implemented with actual impact
```

### Emotional Intelligence
```
POST /api/emotional-intelligence/{return_id}
  - Analyze customer sentiment and churn risk

GET /api/customers/{customer_id}/emotional-profile
  - Get customer's emotional trend

GET /api/at-risk-customers
  - Get customers at high churn risk
  - Params: threshold, skip, limit
```

### Metrics & Observability
```
GET /api/metrics/dashboard
  - All dashboard metrics in real-time

GET /api/metrics/kpis
  - Core KPIs only

GET /api/metrics/financial
  - Financial impact metrics

GET /api/metrics/performance
  - System performance metrics

GET /api/metrics/ml
  - ML model performance

GET /api/metrics/customers
  - Customer insights

GET /api/metrics/trends
  - Trend analysis metrics

GET /api/metrics/risk
  - Risk analysis metrics

GET /api/metrics/health
  - System health status
```

### Audit & Compliance
```
GET /api/audit-logs
  - Get audit trail
  - Params: action, user_id, skip, limit

POST /api/evaluations/run-weekly
  - Trigger evaluation framework

GET /api/evaluations/latest
  - Get latest evaluation results
```

---

## Data Flow

### Return Processing Pipeline

```
1. Customer Submits Return
   ↓
2. API Stores in Database
   ↓
3. Background Task Triggered
   ↓
4. PARALLEL AGENT PROCESSING:
   ├─ Classifier Agent → Category + Confidence
   ├─ Emotional Intelligence Agent → Sentiment + Churn Risk
   ├─ Root Cause Agent → Underlying Reason
   └─ [Other specialized agents as needed]
   ↓
5. Validation Agent
   └─ Quality check all outputs
   ↓
6. Results Stored in Database
   ↓
7. Frontend Displays Analysis
   ↓
8. [Optional] Human Review for Low Confidence Items
   ↓
9. Trend Detection (Batch Job)
   ├─ Identifies patterns
   ├─ Calculates statistical significance
   └─ Stores trends
   ↓
10. Recommendation Generation
    ├─ Based on trends
    ├─ Validated by guardrails
    └─ Presented for approval
```

### Agent Orchestration Flow
```python
AgentOrchestrator receives Return
    ↓
[Determine which agents to run]
    ↓
[Execute agents in parallel/sequence]
    ↓
[Collect results with error handling]
    ↓
[Validate outputs]
    ↓
[Store in database]
    ↓
[Return to API endpoint]
```

---

## Deployment

### Docker Services
```
returniq-postgres   - PostgreSQL 15 database
returniq-redis      - Redis cache (internal)
returniq-backend    - FastAPI backend
returniq-frontend   - React frontend
returniq-prometheus - Metrics collection
returniq-grafana    - Monitoring dashboard
```

### Environment Variables
```
ANTHROPIC_API_KEY       # Required: Claude API key
DATABASE_URL            # PostgreSQL connection
REDIS_URL               # Redis connection
FRONTEND_URL            # Frontend base URL
```

### Performance Tuning

**Database**
- Indexes on: customer_id, return_date, created_at
- Connection pooling: 20 connections
- Replication: Recommended for production

**API**
- Rate limiting: 1000 requests/minute
- Request timeout: 30 seconds
- Max payload: 10MB

**Agents**
- Parallel execution: Up to 5 agents simultaneously
- Timeout per agent: 60 seconds
- Retry logic: 3 retries on failure

---

## Security Considerations

1. **Authentication**: JWT tokens with expiration
2. **Authorization**: Role-based access control
3. **Data Encryption**: TLS in transit, encryption at rest
4. **Rate Limiting**: Prevent abuse
5. **Input Validation**: Pydantic schemas
6. **Audit Logging**: All actions tracked
7. **Guardrails**: Safety checks on agent outputs

---

## Monitoring & Observability

### Key Metrics
- API response times
- Agent execution times
- Database query performance
- Error rates
- Business metrics (ROI, accuracy)

### Dashboards
- System health dashboard
- Agent performance dashboard
- Financial impact dashboard
- Customer insights dashboard

### Alerts
- High error rate (>5%)
- Slow response times (>2s)
- Database connection issues
- Agent failures

---

**Version**: 1.0.0
**Last Updated**: September 26, 2024
**Status**: Production Ready
