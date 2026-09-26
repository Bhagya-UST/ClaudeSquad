# ReturnIQ - Deep Testing Guide with Commands

**Copy-Paste Ready Commands for Complete Testing**

---

## 📋 Pre-Testing Checklist

```bash
# 1. Ensure Docker is running
docker ps

# 2. Start all services
cd /Users/299518/Desktop/WC/ReturnIQ
docker-compose up -d

# 3. Wait 30 seconds for services to initialize
sleep 30

# 4. Verify all services are healthy
docker-compose ps

# Expected output: All services should show "Up" or "Healthy"
```

---

## 🧪 Phase 1: System Connectivity & Health Checks

### 1.1 Backend Health Check
```bash
curl -X GET http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "service": "ReturnIQ API",
  "version": "1.0.0",
  "timestamp": "2024-09-26T..."
}
```

### 1.2 Database Connectivity
```bash
# Check PostgreSQL
docker-compose exec postgres pg_isready -U returniq_user
```

**Expected Output:**
```
accepting connections
```

### 1.3 Redis Connectivity
```bash
# Check Redis
docker-compose exec redis redis-cli ping
```

**Expected Output:**
```
PONG
```

### 1.4 System Health Status
```bash
curl -X GET http://localhost:8000/api/metrics/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "rag_system": "ready",
  "llm_api": "operational",
  "uptime_seconds": 1234,
  "timestamp": "2024-09-26T..."
}
```

---

## 🔐 Phase 2: Authentication Testing

### 2.1 Get Demo Token (For Quick Testing)
```bash
curl -X POST http://localhost:8000/api/auth/demo-token \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2.2 Save Token to Variable
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/demo-token \
  -H "Content-Type: application/json" | jq -r '.access_token')

echo "Token: $TOKEN"
```

### 2.3 Test Authentication
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "user_id": "demo_user",
  "username": "demo",
  "email": "demo@returniq.local",
  "role": "analyst"
}
```

---

## 📥 Phase 3: Return Submission Testing

### 3.1 Submit Single Return
```bash
curl -X POST http://localhost:8000/api/returns \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "customer_id": "CUST001",
    "product_id": "PROD123",
    "order_date": "2024-09-01",
    "return_date": "2024-09-26",
    "return_reason": "Defective",
    "customer_comments": "The button stopped working after 2 weeks of use. Very disappointed with the quality.",
    "product_condition": "opened",
    "refund_amount": 49.99
  }'
```

**Expected Response:**
```json
{
  "status": "accepted",
  "return_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Return submitted for analysis"
}
```

### 3.2 Save Return ID
```bash
RETURN_ID=$(curl -s -X POST http://localhost:8000/api/returns \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "customer_id": "CUST002",
    "product_id": "PROD456",
    "order_date": "2024-09-05",
    "return_date": "2024-09-26",
    "return_reason": "Wrong Size",
    "customer_comments": "Ordered medium but received large. Would like to exchange.",
    "product_condition": "unworn",
    "refund_amount": 79.99
  }' | jq -r '.return_id')

echo "Return ID: $RETURN_ID"
```

### 3.3 Submit Multiple Returns (Bulk Testing)
```bash
for i in {1..5}; do
  curl -s -X POST http://localhost:8000/api/returns \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{
      \"customer_id\": \"CUST0$i\",
      \"product_id\": \"PROD$((i*100))\",
      \"order_date\": \"2024-09-0$i\",
      \"return_date\": \"2024-09-26\",
      \"return_reason\": \"$([ $((i % 2)) -eq 0 ] && echo 'Defective' || echo 'Wrong Size')\",
      \"customer_comments\": \"Return reason comment $i\",
      \"product_condition\": \"opened\",
      \"refund_amount\": $((50 + i * 10))
    }"
  echo "Submitted return $i"
  sleep 1
done
```

---

## 🧠 Phase 4: Agent Testing (Classification)

### 4.1 Wait for Processing (Optional)
```bash
# Wait 10 seconds for async processing
sleep 10
```

### 4.2 Get Return Details
```bash
curl -X GET http://localhost:8000/api/returns/$RETURN_ID \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

**Expected Response**: Full return with classification data

### 4.3 Run Classifier Explicitly
```bash
curl -X POST http://localhost:8000/api/classify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"return_id\": \"$RETURN_ID\"}"
```

**Expected Response:**
```json
{
  "classification_id": "660e8400-e29b-41d4-a716-446655440000",
  "category": "Defective Product",
  "confidence": 0.95,
  "reasoning": "Customer reported button malfunction...",
  "flagged_for_review": false
}
```

### 4.4 Get Classification
```bash
curl -X GET http://localhost:8000/api/classify/$RETURN_ID \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

---

## 💭 Phase 5: Emotional Intelligence Testing

### 5.1 Analyze Emotional Intelligence
```bash
curl -X POST http://localhost:8000/api/emotional-intelligence/$RETURN_ID \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "eq_id": "770e8400-e29b-41d4-a716-446655440000",
  "sentiment_score": -2.5,
  "emotion": "frustrated",
  "intensity": 8,
  "churn_risk": true,
  "churn_risk_score": -4.2,
  "lifecycle_stage": "at_risk",
  "intervention_flag": true
}
```

### 5.2 Get Customer Emotional Profile
```bash
curl -X GET "http://localhost:8000/api/customers/CUST001/emotional-profile" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### 5.3 Get At-Risk Customers
```bash
curl -X GET "http://localhost:8000/api/at-risk-customers?threshold=-3.0&limit=10" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

---

## 📊 Phase 6: Trends Analysis Testing

### 6.1 Detect Trends
```bash
curl -X POST "http://localhost:8000/api/trends/detect?period=weekly" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "trends_count": 2,
  "trend_ids": ["880e8400-e29b-41d4-a716-446655440000"],
  "trends": [
    {
      "title": "Defective Products",
      "description": "40% of returns are defective items",
      "returns_count": 12,
      "percentage": 40,
      "z_score": 2.1,
      "significance": "SIGNIFICANT"
    }
  ]
}
```

### 6.2 List Trends
```bash
curl -X GET "http://localhost:8000/api/trends?period=weekly&limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### 6.3 Get Trend Details
```bash
# First get the trend ID from previous call
TREND_ID="880e8400-e29b-41d4-a716-446655440000"

curl -X GET "http://localhost:8000/api/trends/$TREND_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

---

## 💡 Phase 7: Recommendations Testing

### 7.1 Generate Recommendations from Trend
```bash
curl -X POST "http://localhost:8000/api/recommendations/generate" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"trend_id\": \"$TREND_ID\"}"
```

**Expected Response:**
```json
{
  "recommendations_count": 2,
  "recommendations": [
    {
      "recommendation_id": "990e8400-e29b-41d4-a716-446655440000",
      "text": "Improve quality control process",
      "type": "operational",
      "estimated_impact": 45000,
      "confidence": 0.92,
      "validation_status": "approved"
    }
  ]
}
```

### 7.2 List Recommendations
```bash
curl -X GET "http://localhost:8000/api/recommendations?status=pending_approval&limit=10" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### 7.3 Approve Recommendation
```bash
REC_ID="990e8400-e29b-41d4-a716-446655440000"

curl -X POST "http://localhost:8000/api/recommendations/$REC_ID/approve" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN"
```

### 7.4 Implement Recommendation
```bash
curl -X POST "http://localhost:8000/api/recommendations/$REC_ID/implement" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"actual_impact": 42000}'
```

---

## 📈 Phase 8: Metrics Testing

### 8.1 Get Dashboard Metrics
```bash
curl -X GET http://localhost:8000/api/metrics/dashboard \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### 8.2 Get KPI Metrics
```bash
curl -X GET http://localhost:8000/api/metrics/kpis \
  -H "Authorization: Bearer $TOKEN" | jq '.kpis | .[0:3]'
```

### 8.3 Get Financial Metrics
```bash
curl -X GET http://localhost:8000/api/metrics/financial \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### 8.4 Get Performance Metrics
```bash
curl -X GET http://localhost:8000/api/metrics/performance \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### 8.5 Get ML Metrics
```bash
curl -X GET http://localhost:8000/api/metrics/ml \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### 8.6 Get Customer Metrics
```bash
curl -X GET http://localhost:8000/api/metrics/customers \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### 8.7 Get Risk Metrics
```bash
curl -X GET http://localhost:8000/api/metrics/risk \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

---

## 🔍 Phase 9: List Endpoints Testing

### 9.1 List All Returns
```bash
curl -X GET "http://localhost:8000/api/returns?limit=10" \
  -H "Authorization: Bearer $TOKEN" | jq '.data | .[0:2]'
```

### 9.2 Filter Returns by Status
```bash
curl -X GET "http://localhost:8000/api/returns?status=processed&limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

### 9.3 Filter Returns by Classification
```bash
curl -X GET "http://localhost:8000/api/returns?classification=Defective&limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

---

## 📋 Phase 10: Audit & Compliance Testing

### 10.1 Get Audit Logs
```bash
curl -X GET "http://localhost:8000/api/audit-logs?limit=10" \
  -H "Authorization: Bearer $TOKEN" | jq '.data | .[0:3]'
```

### 10.2 Filter Audit Logs by Action
```bash
curl -X GET "http://localhost:8000/api/audit-logs?action=create_return&limit=5" \
  -H "Authorization: Bearer $TOKEN" | jq '.'
```

---

## 🎨 Phase 11: Frontend UI Testing

### 11.1 Access Frontend
Open in browser:
```
http://localhost:3000
```

### 11.2 Frontend Features to Test
- [ ] Dashboard loads
- [ ] Real-time metrics display
- [ ] Return submission form works
- [ ] View submitted returns
- [ ] Charts and visualizations render
- [ ] Dark mode toggle (if available)
- [ ] Responsive design (test on mobile)
- [ ] Error handling (submit empty form)
- [ ] Loading states display
- [ ] Toast notifications appear

---

## 📊 Phase 12: API Documentation Testing

### 12.1 Access Swagger UI
```
http://localhost:8000/docs
```

### 12.2 Test Each Endpoint in Swagger
- Click "Try it out" on each endpoint
- Execute with example values
- Verify responses match documentation

### 12.2 Access ReDoc
```
http://localhost:8000/redoc
```

---

## 📈 Phase 13: Monitoring & Observability

### 13.1 Prometheus Metrics
```
http://localhost:9090
```

Try these queries:
```
# API response time
histogram_quantile(0.95, http_request_duration_seconds_bucket)

# Error rate
rate(errors_total[5m])

# Requests per second
rate(http_requests_total[1m])
```

### 13.2 Grafana Dashboards
```
http://localhost:3001
Username: admin
Password: admin
```

---

## ⚡ Phase 14: Performance & Load Testing

### 14.1 Concurrent Return Submissions
```bash
# Submit 10 returns concurrently
for i in {1..10}; do
  curl -s -X POST http://localhost:8000/api/returns \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{
      \"customer_id\": \"PERF_TEST_$i\",
      \"product_id\": \"PROD_LOAD_$i\",
      \"order_date\": \"2024-09-26\",
      \"return_date\": \"2024-09-26\",
      \"return_reason\": \"Test Return\",
      \"customer_comments\": \"Load test return $i\",
      \"product_condition\": \"opened\",
      \"refund_amount\": 99.99
    }" &
done
wait
```

### 14.2 API Response Time Test
```bash
# Measure response time
time curl -X GET "http://localhost:8000/api/returns?limit=100" \
  -H "Authorization: Bearer $TOKEN" > /dev/null
```

**Expected**: < 500ms response time

### 14.3 Stress Test with Apache Bench
```bash
# Install if needed: brew install httpd

ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" http://localhost:8000/health
```

---

## 🧠 Phase 15: Error Handling Testing

### 15.1 Invalid Return ID
```bash
curl -X GET "http://localhost:8000/api/returns/invalid-id" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected**: 404 error

### 15.2 Missing Required Fields
```bash
curl -X POST http://localhost:8000/api/returns \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{}'
```

**Expected**: 422 validation error

### 15.3 Unauthorized Access
```bash
curl -X GET "http://localhost:8000/api/returns" \
  -H "Authorization: Bearer invalid-token"
```

**Expected**: 401 unauthorized

### 15.4 Rate Limiting
```bash
# Make 1001 requests to trigger rate limit
for i in {1..1001}; do
  curl -s -X GET http://localhost:8000/health > /dev/null
done
```

**Expected**: 429 Too Many Requests (on 1001st request)

---

## 🗄️ Phase 16: Database Testing

### 16.1 Direct Database Query
```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U returniq_user -d returniq -c "
  SELECT COUNT(*) as total_returns FROM returns;
"
```

### 16.2 Check Database Size
```bash
docker-compose exec postgres psql -U returniq_user -d returniq -c "
  SELECT
    pg_database.datname,
    pg_size_pretty(pg_database_size(pg_database.datname)) AS size
  FROM pg_database
  WHERE datname = 'returniq';
"
```

### 16.3 Check Active Connections
```bash
docker-compose exec postgres psql -U returniq_user -d returniq -c "
  SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;
"
```

---

## 🧩 Phase 17: Integration Testing (End-to-End)

### 17.1 Complete Return Processing Flow
```bash
# 1. Submit return
RETURN_ID=$(curl -s -X POST http://localhost:8000/api/returns \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "customer_id": "E2E_TEST",
    "product_id": "E2E_PROD",
    "order_date": "2024-09-20",
    "return_date": "2024-09-26",
    "return_reason": "Defective",
    "customer_comments": "E2E test with defective product",
    "product_condition": "opened",
    "refund_amount": 199.99
  }' | jq -r '.return_id')

echo "Created return: $RETURN_ID"

# 2. Wait for processing
sleep 5

# 3. Get classification
curl -s -X GET "http://localhost:8000/api/returns/$RETURN_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.classification'

# 4. Analyze emotional intelligence
curl -s -X POST "http://localhost:8000/api/emotional-intelligence/$RETURN_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.emotion'

# 5. Verify in database
docker-compose exec postgres psql -U returniq_user -d returniq -c \
  "SELECT id, category, confidence FROM classifications WHERE return_id = '$RETURN_ID';"
```

---

## 📊 Phase 18: Data Export & Reporting

### 18.1 Export Returns as JSON
```bash
curl -s -X GET "http://localhost:8000/api/returns?limit=1000" \
  -H "Authorization: Bearer $TOKEN" | jq '.data' > returns_export.json
```

### 18.2 Export Recommendations as JSON
```bash
curl -s -X GET "http://localhost:8000/api/recommendations?limit=1000" \
  -H "Authorization: Bearer $TOKEN" | jq '.data' > recommendations_export.json
```

### 18.3 Get Summary Metrics
```bash
curl -s -X GET http://localhost:8000/api/metrics/dashboard \
  -H "Authorization: Bearer $TOKEN" | jq '.summary' > metrics_summary.json
```

---

## 🐛 Debugging Commands

### View Backend Logs
```bash
docker-compose logs -f backend --tail=50
```

### View Frontend Logs
```bash
docker-compose logs -f frontend --tail=50
```

### View Database Logs
```bash
docker-compose logs -f postgres --tail=50
```

### Check Docker Resource Usage
```bash
docker stats
```

### Restart Services
```bash
# Restart backend only
docker-compose restart backend

# Restart all services
docker-compose restart
```

---

## ✅ Test Completion Checklist

- [ ] Phase 1: Health checks pass
- [ ] Phase 2: Authentication works
- [ ] Phase 3: Returns submitted successfully
- [ ] Phase 4: Classification works
- [ ] Phase 5: Emotional intelligence analyzed
- [ ] Phase 6: Trends detected
- [ ] Phase 7: Recommendations generated
- [ ] Phase 8: All metrics endpoints respond
- [ ] Phase 9: List endpoints work with filters
- [ ] Phase 10: Audit logs recorded
- [ ] Phase 11: Frontend UI loads
- [ ] Phase 12: API documentation accessible
- [ ] Phase 13: Monitoring dashboards work
- [ ] Phase 14: Performance within limits
- [ ] Phase 15: Error handling correct
- [ ] Phase 16: Database operations work
- [ ] Phase 17: End-to-end flow complete
- [ ] Phase 18: Data export successful

---

## 🎯 Success Criteria

✅ All 18 phases pass
✅ API response times < 500ms
✅ No unhandled errors in logs
✅ Database integrity maintained
✅ All metrics collecting data
✅ Frontend renders without errors
✅ Authentication/authorization working
✅ Agent responses accurate

---

**Test Date**: _________________
**Tester**: _________________
**Status**: ✅ PASSED / ❌ FAILED

**Notes**:
