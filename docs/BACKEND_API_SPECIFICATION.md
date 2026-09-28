# ReturnIQ Backend API Specification

This document defines all API endpoints needed to power the interactive frontend features.

---

## Base URL
```
http://localhost:3000/api
```

---

## Authentication

All endpoints require authentication token in header:
```
Authorization: Bearer {jwt_token}
```

---

## 1. Dashboard Metrics

### GET /metrics/dashboard
Get high-level metrics for the Overview tab.

**Query Parameters:**
- `timeRange`: `day|week|month|year` (default: `month`)
- `customerId`: Optional - filter by customer

**Response:**
```json
{
  "classification": {
    "accuracy": 96.2,
    "confidence": 94.8,
    "total_classified": 12450
  },
  "returns": {
    "total_processed": 12450,
    "processing_rate": 847,
    "avg_latency_ms": 1200
  },
  "trends": {
    "detected": 15,
    "anomalies": 3,
    "avg_z_score": 2.8
  },
  "recommendations": {
    "generated": 328,
    "approval_rate": 92.3,
    "implementation_rate": 78.5
  },
  "llm": {
    "tokens_used": 2847000,
    "avg_latency_ms": 1450,
    "error_rate": 0.2,
    "hallucination_rate": 0.87
  },
  "churn": {
    "at_risk_customers": 12,
    "prevention_rate": 89.5
  },
  "guardrails": {
    "pii_masked": 847,
    "hallucinations_detected": 5,
    "bias_alerts": 0,
    "harmful_content": 0
  },
  "business_impact": {
    "returns_prevented": 847,
    "estimated_savings_usd": 4200000,
    "time_saved_hours": 340
  }
}
```

**Status:** 200 OK

---

## 2. Returns Management

### GET /returns
Get paginated list of returns with optional filtering and sorting.

**Query Parameters:**
```
page=1
limit=50
search=query          // Search across ID, customer name, product
classification=SIZING,QUALITY,FRAUD
status=pending,approved,rejected,implemented
roi_min=2.0          // Minimum ROI multiplier
churn_risk=high,medium,low
sort_by=date,roi,churn,amount
sort_order=asc,desc
customer_id=CUST_001
date_from=2024-01-01
date_to=2024-12-31
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "RET_001",
      "customerId": "CUST_001",
      "customerName": "John Smith",
      "orderDate": "2024-08-15T10:30:00Z",
      "returnDate": "2024-08-20T14:45:00Z",
      "sku": "SKU_456",
      "productName": "Blue T-Shirt Size M",
      "category": "SIZING",
      "quantity": 1,
      "amount": 45.99,
      "reason": "Shirt runs too small",
      "comments": "I ordered my usual size M but this shirt is significantly smaller than expected. Unworn and with tags.",
      "classification": {
        "result": "SIZING",
        "confidence": 0.96
      },
      "rootCause": {
        "result": "Supplier fabric change - 2% shrinkage",
        "confidence": 0.88
      },
      "fraudScore": 0.02,
      "churnRisk": 0.15,
      "roiPotential": 3.77,
      "status": "pending",
      "recommendation": {
        "id": "REC_001",
        "title": "Update size chart for SKU #456",
        "type": "PRODUCT",
        "roi": 3.77
      }
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 12450,
    "pages": 249
  }
}
```

**Status:** 200 OK

---

### GET /returns/{id}
Get detailed information about a specific return including full agent analysis.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "RET_001",
    "customerId": "CUST_001",
    "customerName": "John Smith",
    "email": "john@example.com",
    "phone": "(555) 123-4567",
    "orderDate": "2024-08-15T10:30:00Z",
    "returnDate": "2024-08-20T14:45:00Z",
    "orderAmount": 45.99,
    "sku": "SKU_456",
    "productName": "Blue T-Shirt Size M",
    "category": "SIZING",
    "quantity": 1,
    "reason": "Shirt runs too small",
    "comments": "I ordered my usual size M but this shirt is significantly smaller than expected. Unworn and with tags.",
    "images": [
      "https://cdn.example.com/returns/RET_001_1.jpg",
      "https://cdn.example.com/returns/RET_001_2.jpg"
    ],
    "classification": {
      "result": "SIZING",
      "confidence": 0.96
    },
    "rootCause": {
      "result": "Supplier fabric change - 2% shrinkage",
      "confidence": 0.88
    },
    "fraudScore": 0.02,
    "churnRisk": 0.15,
    "agentAnalyses": [
      {
        "agent": "Classifier",
        "status": "complete",
        "confidence": 0.96,
        "processingTime": 2.3,
        "tokensUsed": 334,
        "decision": "SIZING",
        "reasoning": "Customer explicitly stated sizing complaint with unworn condition",
        "evidence": [
          "Customer text: 'Shirt runs too small'",
          "Product condition: Unworn with tags",
          "Size ordered: M (usual size)"
        ],
        "alternatives": [
          { "name": "OTHER", "confidence": 0.03 },
          { "name": "QUALITY", "confidence": 0.01 }
        ],
        "metrics": {
          "accuracy": 96.2,
          "latency_ms": 2300,
          "tokens_used": 334
        }
      },
      {
        "agent": "Root Cause Analysis",
        "status": "complete",
        "confidence": 0.88,
        "processingTime": 3.1,
        "tokensUsed": 456,
        "decision": "Supplier fabric change causing shrinkage",
        "reasoning": "Multiple SKUs from same supplier showing 24% return rate spike",
        "evidence": [
          "SKU 456, 457, 458 all from Supplier ABC",
          "Return rate increased from 5% to 24% in 1 week",
          "Supplier recently changed fabric supplier",
          "1,243 total affected returns"
        ],
        "alternatives": [
          { "name": "Size chart error", "confidence": 0.08 },
          { "name": "Manufacturing defect", "confidence": 0.04 }
        ],
        "metrics": {
          "accuracy": 92.1,
          "latency_ms": 3100,
          "tokens_used": 456
        }
      }
    ],
    "recommendation": {
      "id": "REC_001",
      "title": "Update size chart for SKU #456",
      "description": "Adjust sizing measurements and communicate updated fit guide to customers",
      "type": "PRODUCT",
      "impact": {
        "returnsPreventable": 496,
        "estimatedSavings": 18848,
        "implementationCost": 5000,
        "roi": 3.77,
        "confidence": 0.92
      },
      "calculation": {
        "currentReturnRate": 24.0,
        "baselineReturnRate": 3.5,
        "effectivenessPercentage": 50,
        "affectedUnits": 5200,
        "perReturnCost": 38
      },
      "timeline": {
        "implementation": "2 hours",
        "testing": "4 hours",
        "rollout": "Immediate",
        "roiRealization": "Within 30 days"
      },
      "risks": [
        {
          "risk": "Supplier non-compliance",
          "impact": "high",
          "mitigation": "Start with internal size chart update"
        },
        {
          "risk": "Customer adoption",
          "impact": "medium",
          "mitigation": "A/B test new sizing with 10% of customers"
        }
      ],
      "status": "pending"
    },
    "status": "pending",
    "processingTime": 12.3,
    "createdAt": "2024-08-20T14:45:00Z",
    "updatedAt": "2024-08-20T14:45:12Z"
  }
}
```

**Status:** 200 OK | 404 Not Found

---

### POST /returns/{id}/approve
Approve a return and its recommendation for implementation.

**Request Body:**
```json
{
  "approvedBy": "user_id",
  "notes": "Optional notes",
  "scheduledDate": "2024-08-25T09:00:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "RET_001",
    "status": "approved",
    "approvedBy": "user_id",
    "approvedAt": "2024-08-20T15:00:00Z",
    "recommendation": {
      "id": "REC_001",
      "status": "approved"
    }
  }
}
```

**Status:** 200 OK | 400 Bad Request | 404 Not Found

---

### POST /returns/{id}/reject
Reject a return and its recommendation.

**Request Body:**
```json
{
  "rejectedBy": "user_id",
  "reason": "Does not meet criteria",
  "notes": "Optional detailed notes"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "RET_001",
    "status": "rejected",
    "rejectedBy": "user_id",
    "rejectedAt": "2024-08-20T15:00:00Z",
    "rejectionReason": "Does not meet criteria"
  }
}
```

**Status:** 200 OK | 400 Bad Request | 404 Not Found

---

### POST /returns/bulk-approve
Bulk approve multiple returns.

**Request Body:**
```json
{
  "returnIds": ["RET_001", "RET_002", "RET_003"],
  "approvedBy": "user_id",
  "notes": "Q3 high-priority batch"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "approved": 3,
    "failed": 0,
    "results": [
      { "id": "RET_001", "status": "approved" },
      { "id": "RET_002", "status": "approved" },
      { "id": "RET_003", "status": "approved" }
    ]
  }
}
```

**Status:** 200 OK

---

## 3. Customers & Churn

### GET /customers/at-risk
Get list of customers at risk of churn.

**Query Parameters:**
```
limit=50
churnRisk_min=0.5    // Minimum churn risk (0-1)
sort_by=churnRisk,ltv,eqScore
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "customerId": "CUST_12345",
      "name": "Maria Garcia",
      "email": "maria@example.com",
      "phone": "(555) 123-4567",
      "ltv": 2500,
      "eqScore": -4.2,
      "churnRisk": 0.92,
      "emotionalState": "VERY FRUSTRATED",
      "returnsLast30Days": 3,
      "primarySentiment": "Customer expressed extreme frustration with multiple returns",
      "sentiments": [
        "Anger",
        "Frustration",
        "Disappointment",
        "Resignation"
      ],
      "lastReturn": "2024-08-18T10:30:00Z",
      "interventionRecommended": "Executive Outreach Call",
      "successProbability": 0.70,
      "suggestedOffer": "$50 Account Credit + Priority Support",
      "suggestedMessage": "We sincerely apologize for your experience. We've reviewed your returns and want to make this right.",
      "interactionHistory": [
        {
          "date": "2024-08-20T14:00:00Z",
          "type": "email",
          "action": "Support response sent"
        }
      ]
    }
  ],
  "summary": {
    "total": 847,
    "critical": 12,
    "high": 45,
    "medium": 234
  }
}
```

**Status:** 200 OK

---

### GET /customers/{id}
Get detailed customer information.

**Response:**
```json
{
  "success": true,
  "data": {
    "customerId": "CUST_001",
    "name": "John Smith",
    "email": "john@example.com",
    "phone": "(555) 123-4567",
    "accountCreated": "2020-03-15T10:30:00Z",
    "ltv": 2500,
    "totalOrders": 15,
    "totalReturns": 3,
    "returnRate": 0.20,
    "avgOrderValue": 89.50,
    "churnRisk": 0.15,
    "eqScore": -1.2,
    "sentiments": ["Neutral", "Slight frustration"],
    "previousInterventions": [
      {
        "date": "2024-08-10T09:00:00Z",
        "type": "email",
        "description": "Loyalty offer sent",
        "outcome": "purchase_within_7_days"
      }
    ],
    "returns": [
      "RET_001",
      "RET_045",
      "RET_089"
    ]
  }
}
```

**Status:** 200 OK | 404 Not Found

---

### POST /customers/{id}/intervention
Log a customer intervention action.

**Request Body:**
```json
{
  "action": "call|email|offer|escalate",
  "timestamp": "2024-08-20T14:00:00Z",
  "executedBy": "user_id",
  "details": {
    "message": "Optional message sent",
    "offer": "Optional offer details",
    "notes": "Conversation notes"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "customerId": "CUST_001",
    "intervention": {
      "id": "INT_001",
      "action": "call",
      "timestamp": "2024-08-20T14:00:00Z",
      "status": "logged"
    },
    "followUpDue": "2024-08-27T14:00:00Z"
  }
}
```

**Status:** 201 Created | 400 Bad Request

---

### POST /customers/{id}/intervention/{interventionId}/outcome
Log the outcome of an intervention.

**Request Body:**
```json
{
  "outcome": "successful|partial|failed",
  "notes": "Customer agreed to try again, offered $50 credit",
  "actualChurnRisk": 0.45,
  "followUpScheduled": "2024-08-27T14:00:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "intervention": {
      "id": "INT_001",
      "status": "completed",
      "outcome": "successful",
      "actualChurnRisk": 0.45,
      "originalChurnRisk": 0.92,
      "churnRiskReduction": 0.47
    }
  }
}
```

**Status:** 200 OK

---

## 4. Agent Feedback & Training

### POST /feedback/agent/{agentName}
Submit feedback on an agent's decision for model improvement.

**Path Parameters:**
- `agentName`: Classifier, RootCause, TrendDetection, Anomaly, Fraud, Recommendation, Validation, HumanReview, EI

**Request Body:**
```json
{
  "returnId": "RET_001",
  "feedback": "correct|incorrect|unsure",
  "correctionDetails": {
    "correctDecision": "QUALITY",
    "reasoning": "The product had a seam defect, not sizing"
  },
  "submittedBy": "user_id",
  "timestamp": "2024-08-20T14:00:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "feedbackId": "FB_001",
    "agent": "Classifier",
    "feedback": "incorrect",
    "status": "logged",
    "impactScore": 0.87,
    "message": "Thank you! This feedback helps improve our models."
  }
}
```

**Status:** 201 Created

---

### GET /agents/metrics
Get performance metrics for all agents.

**Query Parameters:**
```
timeRange=week|month|year
includeHistorical=true
```

**Response:**
```json
{
  "success": true,
  "data": {
    "classifier": {
      "accuracy": 96.2,
      "confidence": 0.945,
      "latency_ms": 2300,
      "tokensUsed": 334,
      "feedbackCount": 2847,
      "correctCount": 2732,
      "incorrectCount": 115,
      "trend": "up"
    },
    "rootCause": {
      "accuracy": 92.1,
      "confidence": 0.881,
      "latency_ms": 3100,
      "tokensUsed": 456,
      "feedbackCount": 1923,
      "correctCount": 1769,
      "incorrectCount": 154,
      "trend": "stable"
    },
    "fraud": {
      "accuracy": 89.3,
      "confidence": 0.734,
      "latency_ms": 2800,
      "tokensUsed": 289,
      "feedbackCount": 1456,
      "correctCount": 1299,
      "incorrectCount": 157,
      "trend": "up"
    }
  }
}
```

**Status:** 200 OK

---

## 5. Recommendations

### GET /recommendations
Get list of recommendations pending approval.

**Query Parameters:**
```
status=pending|approved|rejected|implemented
type=PRODUCT,SUPPLIER,LOGISTICS,PROCESS
roi_min=2.0
sort_by=roi,confidence,date
limit=50
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "REC_001",
      "title": "Update size chart for SKU #456",
      "description": "Adjust sizing measurements and communicate updated fit guide to customers",
      "type": "PRODUCT",
      "status": "pending",
      "impact": {
        "returnsPreventable": 496,
        "estimatedSavings": 18848,
        "implementationCost": 5000,
        "roi": 3.77,
        "confidence": 0.92
      },
      "createdAt": "2024-08-20T14:45:12Z",
      "associatedReturns": 1243
    }
  ],
  "summary": {
    "pending": 28,
    "approved": 156,
    "implemented": 89,
    "totalPotentialSavings": 2847000
  }
}
```

**Status:** 200 OK

---

### POST /recommendations/{id}/approve
Approve a recommendation for implementation.

**Request Body:**
```json
{
  "approvedBy": "user_id",
  "implementationDate": "2024-08-25T09:00:00Z",
  "notes": "Schedule with product team"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "REC_001",
    "status": "approved",
    "approvedAt": "2024-08-20T15:00:00Z",
    "implementationDate": "2024-08-25T09:00:00Z"
  }
}
```

**Status:** 200 OK

---

## 6. Manager Actions

### GET /manager/action-items
Get action items for manager dashboard.

**Query Parameters:**
```
priority=critical,high,medium,low
filter=all|pending|overdue
limit=50
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "ACT_001",
      "type": "recommendation",
      "title": "Update Size Chart for SKU #456",
      "description": "Multiple sizing issues detected from Supplier ABC",
      "impact": "high",
      "priority": "critical",
      "dueDate": "2024-08-21T09:00:00Z",
      "owner": "Sarah Chen",
      "action": "Review and approve size chart update. Expected to prevent 496 returns.",
      "metrics": [
        { "label": "Returns Prevented", "value": 496 },
        { "label": "Estimated Savings", "value": "$18.8K" },
        { "label": "ROI", "value": "3.77x" },
        { "label": "Confidence", "value": "92%" }
      ],
      "status": "pending_approval"
    }
  ],
  "summary": {
    "total": 47,
    "critical": 3,
    "high": 12,
    "overdue": 2,
    "potentialSavings": 2847000
  }
}
```

**Status:** 200 OK

---

### POST /manager/action-items/{id}/approve
Approve an action item.

**Request Body:**
```json
{
  "approvedBy": "user_id",
  "notes": "Approved for immediate implementation"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "ACT_001",
    "status": "approved",
    "approvedAt": "2024-08-20T15:00:00Z"
  }
}
```

**Status:** 200 OK

---

## 7. Trends & Analytics

### GET /trends
Get detected trends.

**Query Parameters:**
```
limit=20
sort_by=severity,date,affectedReturns
includeAnomalies=true
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "TREND_001",
      "title": "Sizing issues with SKU #456",
      "description": "Multiple returns for sizing issues from specific product",
      "affectedReturns": 1243,
      "returnRate": 0.24,
      "zScore": 3.2,
      "severity": "critical",
      "detectedAt": "2024-08-19T10:30:00Z",
      "status": "investigating",
      "relatedProduct": {
        "sku": "SKU_456",
        "name": "Blue T-Shirt Size M"
      },
      "relatedSupplier": "Supplier ABC",
      "recommendation": "REC_001"
    }
  ]
}
```

**Status:** 200 OK

---

## Error Responses

All endpoints return standardized error responses:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR|NOT_FOUND|UNAUTHORIZED|SERVER_ERROR",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

**Common Status Codes:**
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error
- 503: Service Unavailable

---

## Rate Limiting

- **Free tier:** 100 requests/minute
- **Pro tier:** 1000 requests/minute
- **Enterprise:** Unlimited

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1692547200
```

---

## Pagination

List endpoints support pagination:

**Request:**
```
GET /returns?page=2&limit=50
```

**Response:**
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 50,
    "total": 12450,
    "pages": 249,
    "hasNext": true,
    "hasPrev": true
  }
}
```

---

## Sorting

**Format:** `sort_by=field&sort_order=asc|desc`

**Example:**
```
GET /returns?sort_by=roi&sort_order=desc
```

---

## Filtering

Filters can be combined with `&`:

```
GET /returns?classification=SIZING&status=pending&roi_min=3.0&sort_by=roi
```

---

## Timestamps

All timestamps are ISO 8601 format in UTC:
```
2024-08-20T14:45:12Z
```

---

## Implementation Priority

**Phase 1 (Week 1):** Core CRUD
- GET /returns
- GET /returns/{id}
- POST /returns/{id}/approve
- POST /returns/{id}/reject

**Phase 2 (Week 2):** Churn & Feedback
- GET /customers/at-risk
- POST /customers/{id}/intervention
- POST /feedback/agent/{agentName}

**Phase 3 (Week 3):** Advanced
- GET /manager/action-items
- GET /agents/metrics
- GET /trends

**Phase 4 (Week 4):** Polish
- Bulk operations
- Analytics
- Reports

---

## Database Schema Examples

### Returns Table
```sql
CREATE TABLE returns (
  id VARCHAR(50) PRIMARY KEY,
  customer_id VARCHAR(50) NOT NULL,
  order_date TIMESTAMP NOT NULL,
  return_date TIMESTAMP NOT NULL,
  sku VARCHAR(50) NOT NULL,
  amount DECIMAL(10,2),
  reason TEXT,
  classification VARCHAR(20),
  classification_confidence DECIMAL(4,3),
  root_cause TEXT,
  fraud_score DECIMAL(4,3),
  churn_risk DECIMAL(4,3),
  status VARCHAR(20),
  recommendation_id VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_customer (customer_id),
  INDEX idx_status (status),
  INDEX idx_classification (classification)
);
```

### Customers Table
```sql
CREATE TABLE customers (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(100),
  phone VARCHAR(20),
  lifetime_value DECIMAL(12,2),
  total_orders INT,
  total_returns INT,
  churn_risk DECIMAL(4,3),
  eq_score DECIMAL(5,2),
  last_return_date TIMESTAMP,
  created_at TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_churn_risk (churn_risk),
  INDEX idx_ltv (lifetime_value)
);
```

### Interventions Table
```sql
CREATE TABLE interventions (
  id VARCHAR(50) PRIMARY KEY,
  customer_id VARCHAR(50) NOT NULL,
  action VARCHAR(20),
  executed_by VARCHAR(50),
  timestamp TIMESTAMP,
  outcome VARCHAR(20),
  notes TEXT,
  follow_up_due TIMESTAMP,
  created_at TIMESTAMP,
  INDEX idx_customer (customer_id),
  INDEX idx_action (action),
  INDEX idx_outcome (outcome),
  FOREIGN KEY (customer_id) REFERENCES customers(id)
);
```

