# ReturnIQ - Complete Testing Steps (18 Phases)

**Comprehensive Testing Procedures for All System Components**

---

## Pre-Test Requirements

```bash
docker-compose up -d
sleep 30
docker-compose ps  # Verify all healthy
```

---

## Phase 1-3: Health & Authentication

| Phase | Test | Command | Expected |
|-------|------|---------|----------|
| 1 | System Health | `curl http://localhost:8000/health` | 200 OK |
| 2 | DB Connected | `docker-compose exec postgres pg_isready` | accepting |
| 3 | Auth Token | `curl -X POST http://localhost:8000/api/auth/demo-token` | access_token |

---

## Phase 4-6: Return Management

| Phase | Test | Expected Result |
|-------|------|-----------------|
| 4 | Submit Single Return | Return ID generated, status="accepted" |
| 5 | Submit 5 Concurrent | All store successfully |
| 6 | List Returns | Returns with pagination work |

---

## Phase 7-9: AI Agent Testing

| Phase | Agent | Test | Expected |
|-------|-------|------|----------|
| 7 | Classifier | Classify defective item | Category + 0.90+ confidence |
| 8 | Emotional Intel | Analyze frustrated customer | Sentiment < 0, churn_risk flagged |
| 9 | Root Cause | Find manufacturing issue | Root cause identified |

---

## Phase 10-12: Advanced Features

| Phase | Feature | Test | Expected |
|-------|---------|------|----------|
| 10 | Trends Detection | Detect patterns in 10+ returns | 2+ trends identified |
| 11 | Recommendations | Generate from trend | Actionable with confidence > 0.80 |
| 12 | At-Risk Customers | Get churn-flagged customers | Customers listed with risk scores |

---

## Phase 13-15: Metrics & Monitoring

| Phase | Metric Type | Check |
|-------|-------------|-------|
| 13 | Dashboard Metrics | All KPIs populate |
| 14 | Financial Impact | Refund totals calculate |
| 15 | Performance | API response < 500ms |

---

## Phase 16-18: Integration & Quality

| Phase | Test | Success Criteria |
|-------|------|------------------|
| 16 | End-to-End Flow | Submit → Classify → View → Recommend |
| 17 | Error Handling | Invalid data → 422 error |
| 18 | Database Integrity | All records consistent, no orphans |

---

## Critical Test Cases

### Test Case 1: Happy Path
```bash
1. Submit return with complete data
2. Verify classification completes
3. Check metrics updated
4. Confirm no errors in logs
Expected: All steps succeed without issues
```

### Test Case 2: Low Confidence
```bash
1. Submit vague return comment
2. Classifier returns confidence < 0.70
3. Item flagged for human review
4. Verify in database
Expected: Flagged = true, status = "pending_review"
```

### Test Case 3: Churn Detection
```bash
1. Submit frustrated customer comments
2. EI agent flags churn risk
3. Check at-risk-customers list
4. Send intervention
Expected: Customer appears in at-risk list with high score
```

### Test Case 4: Trend Detection
```bash
1. Submit 20 returns with same defect
2. Run trend detection
3. Statistical significance calculated
4. Recommendations generated
Expected: Trend found with z-score > 2.0
```

### Test Case 5: Data Consistency
```bash
1. Submit return
2. Query from API
3. Query from database
4. Compare results
Expected: Data matches exactly
```

---

## Automated Test Script

```bash
#!/bin/bash
set -e

TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/demo-token | jq -r '.access_token')
RESULTS=()

# Test 1: Health check
echo "Testing health..."
if curl -s http://localhost:8000/health | grep -q '"status":"ok"'; then
  RESULTS+=("✓ Health Check")
else
  RESULTS+=("✗ Health Check")
fi

# Test 2: Submit return
echo "Testing return submission..."
RETURN_ID=$(curl -s -X POST http://localhost:8000/api/returns \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"customer_id":"TEST","product_id":"TEST","return_reason":"Defective","customer_comments":"Test comment","refund_amount":50}' \
  | jq -r '.return_id')

if [ ! -z "$RETURN_ID" ] && [ "$RETURN_ID" != "null" ]; then
  RESULTS+=("✓ Return Submission")
else
  RESULTS+=("✗ Return Submission")
fi

# Test 3: Get classification
sleep 2
echo "Testing classification..."
CONFIDENCE=$(curl -s -X GET "http://localhost:8000/api/returns/$RETURN_ID" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.classification.confidence // 0')

if (( $(echo "$CONFIDENCE > 0.5" | bc -l) )); then
  RESULTS+=("✓ Classification")
else
  RESULTS+=("✗ Classification")
fi

# Test 4: List returns
echo "Testing list..."
COUNT=$(curl -s -X GET "http://localhost:8000/api/returns" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.total')

if [ "$COUNT" -gt "0" ]; then
  RESULTS+=("✓ List Returns")
else
  RESULTS+=("✗ List Returns")
fi

# Test 5: Metrics
echo "Testing metrics..."
KPI_COUNT=$(curl -s -X GET "http://localhost:8000/api/metrics/dashboard" \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.kpis | length')

if [ "$KPI_COUNT" -gt "0" ]; then
  RESULTS+=("✓ Metrics")
else
  RESULTS+=("✗ Metrics")
fi

# Print results
echo ""
echo "Test Results:"
for result in "${RESULTS[@]}"; do
  echo "  $result"
done

# Summary
PASSED=$(echo "${RESULTS[@]}" | grep -c "✓" || echo 0)
FAILED=$(echo "${RESULTS[@]}" | grep -c "✗" || echo 0)
echo ""
echo "PASSED: $PASSED"
echo "FAILED: $FAILED"
```

---

## Browser Testing Checklist

### Frontend UI (http://localhost:3000)
- [ ] Page loads without errors
- [ ] Dashboard metrics display
- [ ] Return submission form renders
- [ ] Form validation works
- [ ] Submit return button functional
- [ ] Submitted returns appear in list
- [ ] Classification displays correctly
- [ ] Charts render without errors
- [ ] Responsive on mobile
- [ ] Dark mode works (if available)
- [ ] Error messages display properly
- [ ] Loading states show

### API Documentation (http://localhost:8000/docs)
- [ ] Swagger UI loads
- [ ] All endpoints listed
- [ ] Try-it-out functionality works
- [ ] Example requests work
- [ ] Response schemas shown

### Monitoring (http://localhost:9090)
- [ ] Prometheus loads
- [ ] Metrics available
- [ ] Queries work

### Grafana (http://localhost:3001)
- [ ] Loads with admin/admin
- [ ] Dashboards exist
- [ ] Panels display data

---

## Log Inspection

```bash
# Check for errors
docker-compose logs backend | grep -i error
docker-compose logs frontend | grep -i error
docker-compose logs postgres | grep -i error

# Check request counts
docker-compose logs backend | grep "POST\|GET" | wc -l

# Check database activity
docker-compose logs postgres | grep "statement" | tail -20
```

---

## Performance Benchmarks

| Metric | Target | Acceptable |
|--------|--------|-----------|
| API Response Time | < 200ms | < 500ms |
| Database Query | < 100ms | < 300ms |
| Agent Processing | < 2s | < 5s |
| Page Load Time | < 1s | < 2s |
| Requests/sec | > 100 | > 50 |

---

## Stress Test

```bash
# 100 concurrent submissions
for i in {1..100}; do
  curl -s -X POST http://localhost:8000/api/returns \
    -H "Content-Type: application/json" \
    -d "{\"customer_id\":\"STRESS_$i\",\"product_id\":\"P$i\",\"return_reason\":\"Test\",\"customer_comments\":\"Stress test\",\"refund_amount\":50}" &
done
wait

# Check results
curl -s http://localhost:8000/api/returns?limit=1 | jq '.total'
```

---

## Regression Testing

Run after any code changes:
```bash
./test_complete.sh  # Run automated test script
Check browser manually
Verify metrics updated
```

---

**Last Updated**: September 26, 2024
