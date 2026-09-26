# ReturnIQ Documentation Index

**Quick Navigation Guide for all ReturnIQ Documentation**

## 📚 START HERE

### [1. DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md) ← You are here
Navigation guide for all documentation. Start here to understand what documentation exists.

### [2. DEEP_TESTING_GUIDE_WITH_COMMANDS.md](./DEEP_TESTING_GUIDE_WITH_COMMANDS.md)
Copy-paste ready commands for complete testing. Run each command in sequence to fully test the system.

---

## 👨‍⚖️ FOR JUDGES & EVALUATORS

### [3. COMPLETE_TECHNICAL_DOCUMENTATION.md](./COMPLETE_TECHNICAL_DOCUMENTATION.md)
Full architecture explanation including:
- System architecture overview
- All 9 AI agents and their responsibilities
- Database schema and models
- API endpoints with examples
- Technology stack and design decisions

### [4. USER_FLOW_DIAGRAM.md](./USER_FLOW_DIAGRAM.md)
Visual flowcharts showing:
- 5 different user personas and their journeys
- 9 AI agents and how they interact
- Complete return processing workflow
- Data flow between components

### [5. CODE_EXECUTION_AT_EACH_LEVEL.md](./CODE_EXECUTION_AT_EACH_LEVEL.md)
Actual code snippets showing:
- Execution flow at each processing level
- How each agent processes data
- How results cascade through the system
- Example input/output at each stage

---

## 🧪 FOR TESTING & QA

### [6. COMPLETE_TESTING_STEPS.md](./COMPLETE_TESTING_STEPS.md)
18 comprehensive testing phases:
- Frontend UI testing
- Backend API testing
- Agent behavior testing
- Integration testing
- Performance testing
- Edge case testing

### [7. SCALE_TESTING_GUIDE.md](./SCALE_TESTING_GUIDE.md)
Testing with large datasets:
- Generate 1M+ records
- Test performance at scale
- Load testing procedures
- Benchmark metrics

### [8. DEMO_SCRIPT.md](./DEMO_SCRIPT.md)
Step-by-step demo guide:
- Pre-demo checklist
- Demo walkthrough (15 minutes)
- Key talking points for each feature
- Handling common questions

---

## 🚀 QUICK START

### Prerequisites
- Docker and Docker Compose installed
- Python 3.11+
- Node.js 18+
- PostgreSQL 15
- Redis 7

### Running the Application

```bash
# Start all services
docker-compose up -d

# Check services are healthy
docker-compose ps

# View logs
docker-compose logs -f backend

# Access the application
Frontend: http://localhost:3000
API Docs: http://localhost:8000/docs
Grafana: http://localhost:3001 (admin/admin)
Prometheus: http://localhost:9090
```

### Stop the Application

```bash
docker-compose down
```

---

## 📊 System Components

### Frontend (React/TypeScript)
- **Location**: `/frontend/src`
- **Port**: 3000
- **Features**: Dashboard, real-time metrics, agent monitoring

### Backend (FastAPI)
- **Location**: `/backend`
- **Port**: 8000
- **Features**: 9 AI agents, REST API, metrics collection

### Database (PostgreSQL)
- **Port**: 5432
- **Storage**: `/postgres_data`
- **DB Name**: returniq
- **Credentials**: returniq_user / returniq_password

### Cache (Redis)
- **Port**: 6379 (internal)
- **Storage**: `/redis_data`
- **Purpose**: Session caching, metrics

### Monitoring
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
- **Metrics Port**: 9090

---

## 🤖 AI Agents (9 Total)

1. **Classifier Agent** - Categorizes returns (Defect, Wrong Item, Size, etc.)
2. **Emotional Intelligence Agent** - Analyzes sentiment, emotion, churn risk
3. **Root Cause Agent** - Identifies underlying reasons for returns
4. **Trend Detection Agent** - Finds patterns in returns data
5. **Recommendation Engine** - Suggests business improvements
6. **Fraud Detection Agent** - Flags suspicious return patterns
7. **Anomaly Detection Agent** - Identifies unusual behaviors
8. **Validation Agent** - Quality checks on all outputs
9. **Human Review Agent** - Manages flagged items for human intervention

---

## 📈 Key Metrics Tracked

- **Returns**: Total, by category, trend
- **Customer Sentiment**: Avg score, trend, at-risk count
- **System Performance**: API response time, throughput
- **Financial**: Total refund amount, cost of issues
- **Agent Accuracy**: Classification accuracy, confidence scores

---

## 🔐 Authentication

- **JWT Token-based** authentication
- **Demo Mode** for quick testing
- **Role-based** access control
- Environment variable: `ANTHROPIC_API_KEY`

---

## 📝 API Documentation

Full API documentation available at:
```
http://localhost:8000/docs
```

Main endpoints:
- `POST /api/returns` - Submit a return
- `GET /api/returns/{id}` - Get return details
- `POST /api/classify` - Run classifier
- `GET /api/trends` - View trends
- `POST /api/recommendations/generate` - Generate recommendations
- `GET /api/metrics/dashboard` - Get all metrics

---

## 🐛 Troubleshooting

### Application won't start
1. Check Docker is running: `docker ps`
2. Check logs: `docker-compose logs`
3. Verify ports are free: `lsof -i :8000` (should be empty)

### SSL Certificate Error
```bash
# Already fixed in Dockerfile.backend with --trusted-host flags
# If issues persist, rebuild:
docker-compose up -d --build
```

### Port Already in Use
```bash
# Find what's using the port
lsof -i :6379  # For example

# Either stop that process or modify docker-compose.yml port mappings
```

---

## 📞 Support

For detailed testing procedures: See `DEEP_TESTING_GUIDE_WITH_COMMANDS.md`
For architectural details: See `COMPLETE_TECHNICAL_DOCUMENTATION.md`
For demo walkthrough: See `DEMO_SCRIPT.md`

---

**Last Updated**: September 26, 2024
**Version**: 1.0.0
**Status**: Production Ready
