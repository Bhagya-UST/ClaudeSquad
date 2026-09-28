# ReturnIQ - Scale Testing Guide

**Testing with Large Datasets (1M+ Records)**

---

## Prerequisites

```bash
# Increase resources for Docker
# Mac: Docker → Preferences → Resources → Set Memory: 8GB+, CPUs: 4+
# Linux: Ensure sufficient system resources

# Verify setup
docker stats  # Monitor resource usage
```

---

## Phase 1: Load Testing Data Generator

### Generate 10,000 Returns

```bash
cat > /tmp/generate_returns.py << 'EOF'
import requests
import json
from datetime import datetime, timedelta
import random

API_URL = "http://localhost:8000"
TOKEN = requests.post(f"{API_URL}/api/auth/demo-token").json()['access_token']

REASONS = ["Defective", "Wrong Size", "Wrong Item", "Damaged", "Changed Mind"]
COMMENTS = [
    "Product broke after 1 week",
    "Not as described",
    "Wrong size ordered",
    "Quality not as expected",
    "Damaged in shipping"
]

def generate_and_submit(count=10000):
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    for i in range(count):
        return_data = {
            "customer_id": f"CUST_{i:06d}",
            "product_id": f"PROD_{random.randint(1, 1000):04d}",
            "order_date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
            "return_reason": random.choice(REASONS),
            "customer_comments": random.choice(COMMENTS),
            "product_condition": random.choice(["unworn", "opened", "worn"]),
            "refund_amount": round(random.uniform(10, 500), 2)
        }
        
        try:
            response = requests.post(
                f"{API_URL}/api/returns",
                json=return_data,
                headers=headers,
                timeout=10
            )
            
            if i % 500 == 0:
                print(f"Submitted {i} returns...")
            
            if response.status_code != 200:
                print(f"Error at {i}: {response.status_code}")
        
        except Exception as e:
            print(f"Exception at {i}: {e}")

if __name__ == "__main__":
    print("Generating 10,000 returns...")
    generate_and_submit(10000)
    print("Done!")
EOF

# Run generator
python /tmp/generate_returns.py
```

### Generate 100,000 Returns (Bulk Database Insert)

```bash
# Create CSV
cat > /tmp/returns_bulk.csv << 'EOF'
customer_id,product_id,order_date,return_reason,customer_comments,product_condition,refund_amount
CUST_000001,PROD_0001,2024-09-01,Defective,Product broke,opened,49.99
CUST_000002,PROD_0002,2024-09-02,Wrong Size,Not as described,unworn,79.99
CUST_000003,PROD_0003,2024-09-03,Damaged,Shipping damage,opened,99.99
EOF

# Load via PostgreSQL
docker-compose exec postgres psql -U returniq_user -d returniq -c \
"COPY returns (customer_id, product_id, order_date, return_reason, customer_comments, product_condition, refund_amount) 
FROM STDIN WITH CSV HEADER;" < /tmp/returns_bulk.csv
```

---

## Phase 2: Test Scalability

### Test API Response Times

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/demo-token | jq -r '.access_token')

# Single record fetch
time curl -s -X GET "http://localhost:8000/api/returns?limit=1" \
  -H "Authorization: Bearer $TOKEN" > /dev/null

# Large result set (100 records)
time curl -s -X GET "http://localhost:8000/api/returns?limit=100" \
  -H "Authorization: Bearer $TOKEN" > /dev/null

# Very large result set (1000 records)
time curl -s -X GET "http://localhost:8000/api/returns?limit=1000" \
  -H "Authorization: Bearer $TOKEN" > /dev/null
```

Expected Times:
- 1 record: < 100ms
- 100 records: < 300ms
- 1000 records: < 1s

### Test Trend Detection at Scale

```bash
# Detect trends with 10,000+ returns
curl -s -X POST "http://localhost:8000/api/trends/detect?period=monthly" \
  -H "Authorization: Bearer $TOKEN" | jq '.trends_count'

# This should complete in < 5 seconds
```

### Test Aggregation Performance

```bash
# Get metrics with large dataset
time curl -s -X GET "http://localhost:8000/api/metrics/dashboard" \
  -H "Authorization: Bearer $TOKEN" > metrics.json

# Check calculation time (should be < 2s)
```

---

## Phase 3: Database Performance

### Check Query Performance

```bash
docker-compose exec postgres psql -U returniq_user -d returniq << 'EOF'

-- Count returns
SELECT COUNT(*) FROM returns;

-- Index effectiveness
EXPLAIN ANALYZE
SELECT * FROM returns 
WHERE customer_id = 'CUST_000001'
LIMIT 10;

-- Aggregation query
EXPLAIN ANALYZE
SELECT 
  category,
  COUNT(*) as count,
  AVG(refund_amount) as avg_refund
FROM returns r
LEFT JOIN classifications c ON r.id = c.return_id
GROUP BY category
ORDER BY count DESC;

EOF
```

### Monitor Database Size

```bash
docker-compose exec postgres psql -U returniq_user -d returniq -c \
"SELECT 
  pg_database.datname,
  pg_size_pretty(pg_database_size(pg_database.datname)) AS size
FROM pg_database
WHERE datname = 'returniq';"

# Table sizes
docker-compose exec postgres psql -U returniq_user -d returniq -c \
"SELECT
  tablename,
  pg_size_pretty(pg_total_relation_size(tablename::regclass)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(tablename::regclass) DESC;"
```

---

## Phase 4: Concurrent User Testing

### Simulate 10 Concurrent Users

```bash
for user in {1..10}; do
  (
    for i in {1..10}; do
      curl -s -X POST http://localhost:8000/api/returns \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d "{\"customer_id\":\"USER_${user}_${i}\",\"product_id\":\"PROD_$i\",\"return_reason\":\"Test\",\"customer_comments\":\"Concurrent test\",\"refund_amount\":50}" > /dev/null
      sleep 0.5
    done
  ) &
done
wait
```

### Load Test with Apache Bench

```bash
ab -n 1000 -c 50 -H "Authorization: Bearer $TOKEN" http://localhost:8000/health

# Metrics:
# Requests per second
# Failed requests (should be 0)
# 95th percentile response time
```

---

## Phase 5: Memory & Resource Monitoring

### Watch Resource Usage

```bash
docker stats --no-stream

# Expected:
# Backend: < 500MB RAM, < 50% CPU
# PostgreSQL: < 2GB RAM, < 30% CPU
# Redis: < 100MB RAM
```

### Monitor During Load

```bash
# Terminal 1: Run load test
for i in {1..100}; do
  curl -s -X POST http://localhost:8000/api/returns \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{...}" &
done

# Terminal 2: Monitor
watch 'docker stats --no-stream | grep -E "returniq|NAME"'
```

---

## Phase 6: Cache Effectiveness

### Before Cache Hits

```bash
curl -X GET "http://localhost:8000/api/metrics/dashboard" \
  -H "Authorization: Bearer $TOKEN" \
  -w "@/tmp/curl-format.txt" -o /dev/null

# First request: ~2s (cold cache)
```

### After Cache Hits

```bash
# Run 5 times
for i in {1..5}; do
  curl -s -X GET "http://localhost:8000/api/metrics/dashboard" \
    -H "Authorization: Bearer $TOKEN" > /dev/null
  echo "Request $i done"
done

# Subsequent requests: ~100ms (cache hit)
```

---

## Phase 7: Stress Limits

### Find Breaking Point

```bash
# Start with 100 concurrent, increase to 1000
for threads in 100 500 1000 2000; do
  echo "Testing with $threads concurrent requests..."
  ab -n 5000 -c $threads \
    -H "Authorization: Bearer $TOKEN" \
    http://localhost:8000/api/returns?limit=10
  
  echo "Failed requests: $?"
  sleep 5
done
```

### Expected Limits
- Up to 1000 concurrent: < 2% errors
- Up to 5000 concurrent: < 10% errors
- Beyond 5000: Check infrastructure scaling

---

## Phase 8: Data Consistency

### Verify Data Integrity

```bash
docker-compose exec postgres psql -U returniq_user -d returniq << 'EOF'

-- Check orphaned records (classifications without returns)
SELECT COUNT(*) FROM classifications c
WHERE NOT EXISTS (SELECT 1 FROM returns r WHERE r.id = c.return_id);

-- Check orphaned EI records
SELECT COUNT(*) FROM emotional_intelligence ei
WHERE NOT EXISTS (SELECT 1 FROM returns r WHERE r.id = ei.return_id);

-- Verify aggregation consistency
SELECT
  COUNT(DISTINCT return_id) as total_returns,
  COUNT(DISTINCT CASE WHEN category IS NOT NULL THEN return_id END) as classified,
  ROUND(100.0 * COUNT(DISTINCT CASE WHEN category IS NOT NULL THEN return_id END) / 
        COUNT(DISTINCT return_id), 2) as classification_rate
FROM returns r
LEFT JOIN classifications c ON r.id = c.return_id;

EOF
```

---

## Phase 9: Report Generation

### Performance Report

```bash
cat > /tmp/perf_report.sh << 'EOF'
#!/bin/bash

echo "=== ReturnIQ Scale Testing Report ==="
echo "Date: $(date)"
echo ""

echo "Database Size:"
docker-compose exec postgres psql -U returniq_user -d returniq -c \
"SELECT COUNT(*) as returns FROM returns;"

echo ""
echo "API Response Times (cached):"
time curl -s http://localhost:8000/api/returns?limit=100 > /dev/null

echo ""
echo "System Resources:"
docker stats --no-stream

echo ""
echo "Data Integrity:"
docker-compose exec postgres psql -U returniq_user -d returniq -c \
"SELECT COUNT(*) FROM returns WHERE id NOT IN (SELECT DISTINCT return_id FROM classifications);"

EOF

chmod +x /tmp/perf_report.sh
/tmp/perf_report.sh
```

---

## Scaling Recommendations

### For 1M Records
- [ ] Increase PostgreSQL RAM: 8GB+
- [ ] Enable connection pooling (PgBouncer)
- [ ] Add read replicas
- [ ] Implement caching layer (Redis)
- [ ] Archive old data (> 6 months)

### For 10M Records
- [ ] Implement sharding/partitioning
- [ ] Use specialized analytics DB (BigQuery, Redshift)
- [ ] Implement materialized views
- [ ] Enable parallel query execution
- [ ] Consider data warehouse

---

**Last Updated**: September 26, 2024
