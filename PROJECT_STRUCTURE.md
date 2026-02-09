# CEPS Project Structure

## Overview
This document describes the complete project structure for CEPS MVP v2.

## Directory Structure

```
CEPS/
├── api/                           # FastAPI application
│   ├── __init__.py               # API module initialization
│   ├── main.py                   # Main FastAPI app (TODO: Phase 6)
│   ├── models.py                 # API-specific Pydantic models (TODO)
│   ├── dependencies.py           # Dependency injection (TODO)
│   └── routes/                   # API route modules (TODO)
│       ├── analysis.py           # Analysis endpoints
│       └── health.py             # Health check endpoints
│
├── agents/                        # Intelligence agents
│   ├── __init__.py               # Agents module initialization
│   ├── text_agent.py             # Text quality analysis (TODO: Phase 4)
│   ├── visual_agent.py           # Image analysis (TODO: Phase 4)
│   ├── ux_agent.py               # Structure & UX (TODO: Phase 4)
│   ├── trust_agent.py            # Trust signals (TODO: Phase 4)
│   └── tech_agent.py             # Technical health (TODO: Phase 4)
│
├── services/                      # Core services
│   ├── __init__.py               # Services module initialization
│   ├── scraper.py                # Web scraping (TODO: Phase 2)
│   ├── parser.py                 # HTML parsing (TODO: Phase 2)
│   ├── llm_router.py             # Gemini integration (TODO: Phase 3)
│   └── cache.py                  # Redis caching (TODO: Phase 3)
│
├── core/                          # Core business logic
│   ├── __init__.py               ✅ Module initialization
│   ├── config.py                 ✅ Configuration management
│   ├── database.py               ✅ Database connection
│   ├── logging.py                ✅ Logging setup
│   ├── models.py                 ✅ Data models
│   ├── exceptions.py             ✅ Custom exceptions
│   └── scoring.py                # CEPS aggregation (TODO: Phase 5)
│
├── workers/                       # Celery workers
│   ├── __init__.py               # Workers module initialization
│   ├── celery_app.py             # Celery configuration (TODO: Phase 6)
│   └── tasks.py                  # Background tasks (TODO: Phase 6)
│
├── ui/                            # Streamlit frontend
│   ├── __init__.py               # UI module initialization
│   ├── app.py                    # Main UI (TODO: Phase 7)
│   └── components/               # UI components (TODO: Phase 7)
│       ├── header.py
│       ├── results.py
│       └── charts.py
│
├── db/                            # Database
│   ├── schema.sql                ✅ Database schema
│   └── migrations/               # Alembic migrations (TODO)
│
├── tests/                         # Test suite
│   ├── test_agents/              # Agent tests (TODO: Phase 8)
│   ├── test_services/            # Service tests (TODO: Phase 8)
│   ├── test_api/                 # API tests (TODO: Phase 8)
│   └── conftest.py               ✅ Pytest configuration
│
├── scripts/                       # Utility scripts
│   ├── init_db.py                ✅ Database initialization
│   ├── setup.sh                  ✅ Development setup
│   └── test_analysis.py          ✅ Analysis testing script
│
├── terraform/                     # Infrastructure as Code
│   ├── main.tf                   # Main configuration (TODO: Phase 9)
│   ├── variables.tf              # Variables (TODO: Phase 9)
│   └── outputs.tf                # Outputs (TODO: Phase 9)
│
├── logs/                          # Application logs (auto-created)
│
├── .env                           ✅ Local environment variables
├── .env.example                  ✅ Environment template
├── .gitignore                    ✅ Git ignore rules
├── requirements.txt              ✅ Python dependencies
├── pyproject.toml                ✅ Project configuration
├── docker-compose.yml            ✅ Docker services
├── Dockerfile                    ✅ Docker build
├── conftest.py                   ✅ Pytest fixtures
├── README.md                     ✅ Project documentation
├── CONTRIBUTING.md               ✅ Contribution guidelines
├── development_sheet.md          ✅ Architecture documentation
└── project_workflow.md           ✅ Technical workflow
```

## Phase 1 Completion Status ✅

### Completed Files
1. ✅ `requirements.txt` - All dependencies defined
2. ✅ `.env.example` - Environment template
3. ✅ `.env` - Local configuration (needs GEMINI_API_KEY)
4. ✅ `.gitignore` - Comprehensive ignore rules
5. ✅ `README.md` - Complete project documentation
6. ✅ `CONTRIBUTING.md` - Contribution guidelines
7. ✅ `pyproject.toml` - Tool configurations
8. ✅ `conftest.py` - Pytest fixtures
9. ✅ `docker-compose.yml` - Docker orchestration
10. ✅ `Dockerfile` - Multi-stage Docker build
11. ✅ `db/schema.sql` - Database schema
12. ✅ `scripts/init_db.py` - Database initialization
13. ✅ `scripts/setup.sh` - Development setup
14. ✅ `scripts/test_analysis.py` - Testing script
15. ✅ `core/config.py` - Configuration management
16. ✅ `core/database.py` - Database connection
17. ✅ `core/logging.py` - Logging setup
18. ✅ `core/models.py` - Data models
19. ✅ `core/exceptions.py` - Custom exceptions
20. ✅ All module `__init__.py` files

### Directory Structure
✅ All directories created:
- `api/`, `agents/`, `services/`, `core/`, `workers/`, `ui/`
- `db/`, `db/migrations/`, `tests/`, `scripts/`, `terraform/`, `logs/`
- `ui/components/`, `tests/test_agents/`, `tests/test_services/`, `tests/test_api/`

## Next Steps

### Phase 2: Implement Scraper and Parser Services
- `services/scraper.py` - Web scraping with error handling
- `services/parser.py` - HTML parsing and data extraction

### Phase 3: Build LLM Router
- `services/llm_router.py` - Gemini 2.5 integration
- `services/cache.py` - Redis caching layer

### Phase 4: Implement Intelligence Agents
- `agents/text_agent.py` - Text quality analysis
- `agents/visual_agent.py` - Image analysis
- `agents/ux_agent.py` - Structure & UX
- `agents/trust_agent.py` - Trust signals
- `agents/tech_agent.py` - Technical health

### Phase 5: Build CEPS Score Aggregator
- `core/scoring.py` - Score aggregation logic

### Phase 6: Create FastAPI Backend
- `api/main.py` - FastAPI application
- `workers/celery_app.py` - Celery configuration
- `workers/tasks.py` - Background tasks

### Phase 7: Build Streamlit UI
- `ui/app.py` - Main UI
- `ui/components/` - UI components

### Phase 8: Testing
- Comprehensive test suite

### Phase 9: Deployment
- Terraform configurations
- Cloud deployment

## Key Features

### Configuration Management
- Environment-based configuration using pydantic-settings
- Centralized settings in `core/config.py`
- Validation and type checking
- Environment-specific overrides

### Database
- PostgreSQL with SQLAlchemy ORM
- Connection pooling
- Migration support (Alembic ready)
- Comprehensive schema with indexes and views

### Logging
- Structured logging with loguru
- JSON and text formats
- Separate log files for API, workers, and errors
- Log rotation and compression

### Error Handling
- Custom exception classes
- Centralized error handling
- Detailed error messages with context

### Caching
- Redis-based caching
- Cache key generation
- Configurable expiration
- Cache statistics tracking

### Monitoring
- Health check endpoints (TODO)
- Metrics collection (TODO)
- Error tracking (Sentry ready)
- Performance monitoring

## Development Workflow

1. **Setup Environment**
   ```bash
   ./scripts/setup.sh
   ```

2. **Configure API Keys**
   ```bash
   nano .env  # Add GEMINI_API_KEY
   ```

3. **Initialize Database**
   ```bash
   python scripts/init_db.py
   ```

4. **Start Services**
   ```bash
   # Option 1: Docker
   docker-compose up -d
   
   # Option 2: Local
   redis-server &
   uvicorn api.main:app --reload &
   celery -A workers.celery_app worker --loglevel=info &
   streamlit run ui/app.py
   ```

5. **Run Tests**
   ```bash
   pytest --cov=.
   ```

## Technology Stack

- **Backend**: FastAPI (async Python web framework)
- **Frontend**: Streamlit (rapid UI development)
- **Task Queue**: Celery + Redis
- **Database**: PostgreSQL 14+
- **Cache**: Redis 7+
- **AI/ML**: Google Gemini 2.5 (Flash + Pro)
- **Deployment**: Docker, GCP (Cloud Run, Cloud SQL, Memorystore)
- **IaC**: Terraform

## Security Considerations

1. **Secrets Management**
   - Never commit `.env` or API keys
   - Use Google Secret Manager in production
   - Rotate API keys regularly

2. **Input Validation**
   - Pydantic models for request validation
   - URL sanitization
   - HTML sanitization

3. **Rate Limiting**
   - Per-IP rate limiting
   - Per-user rate limiting
   - Cost control limits (images, text)

4. **Network Security**
   - HTTPS only
   - CORS configuration
   - Network policies in Kubernetes

## Performance Optimization

1. **Caching**
   - Redis caching for LLM responses
   - 24-hour expiration
   - Cache hit tracking

2. **Async Processing**
   - Celery for background tasks
   - Non-blocking API responses
   - Parallel agent execution

3. **Database**
   - Connection pooling
   - Indexes on common queries
   - Query optimization

4. **Cost Control**
   - Limit images per page (3 max)
   - Limit text characters (8000 max)
   - Limit page size (5MB max)
   - Scraper timeout (15 seconds)

## Monitoring & Observability

1. **Logs**
   - Structured JSON logging
   - Separate files for API, workers, errors
   - Log rotation and retention

2. **Metrics** (TODO)
   - Analysis completion time
   - LLM API calls and costs
   - Cache hit rates
   - Error rates

3. **Health Checks** (TODO)
   - Database connectivity
   - Redis connectivity
   - Gemini API availability

4. **Error Tracking**
   - Sentry integration ready
   - Detailed error context
   - Stack traces in development

## Documentation

- **README.md**: Project overview and setup
- **CONTRIBUTING.md**: Development guidelines
- **development_sheet.md**: Architecture details
- **project_workflow.md**: Technical workflow
- **API Documentation**: Auto-generated via FastAPI (TODO)

## Phase 1 Summary

✅ **Phase 1 is COMPLETE!**

We have successfully:
1. ✅ Created complete project structure
2. ✅ Defined all dependencies
3. ✅ Set up configuration management
4. ✅ Created database schema
5. ✅ Configured logging system
6. ✅ Defined data models
7. ✅ Set up error handling
8. ✅ Created Docker configuration
9. ✅ Set up testing framework
10. ✅ Created development scripts
11. ✅ Wrote comprehensive documentation

**Ready for Phase 2: Implementing core services!**
