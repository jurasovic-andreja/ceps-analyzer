# CEPS MVP v2 — Infrastructure Architecture

## Architecture Diagram
```
                ┌────────────────────┐
                │    Streamlit UI    │
                │  (Frontend Layer)  │
                └─────────┬──────────┘
                          │ HTTPS
                          ▼
                ┌────────────────────┐
                │  API / App Server  │
                │   (FastAPI)        │
                └─────────┬──────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
┌──────────────┐  ┌────────────────┐  ┌─────────────────┐
│ Scraper      │  │ AI Orchestrator│  │ Scoring Engine  │
│ Service      │  │ (Agent Router) │  │ CEPS Logic      │
└──────┬───────┘  └──────┬─────────┘  └────────┬────────┘
       │                  │                     │
       ▼                  ▼                     ▼
  HTML Parser      LLM Providers Layer     Score Aggregator
       │                  │
       ▼                  ▼
 Image Ranker      Vision / Text Models
```

## 1. Hosting Recommendations

| Component | Technology | Why? |
|-----------|------------|------|
| Frontend | Streamlit Cloud / Render | Rapid deployment |
| Backend API | FastAPI | Async, lightweight |
| Worker tasks | Celery + Redis | Parallel analysis |
| Hosting | AWS / GCP / Fly.io | Scalability |
| Storage | PostgreSQL | Analysis results storage |
| Cache | Redis | LLM response caching |

## 2. LLM Routing Layer

Necessary because different agents utilize different models.
```python
class LLMRouter:
    def analyze_text(self, text):
        return call_text_model(text)

    def analyze_image(self, image_url, context):
        return call_vision_model(image_url, context)

    def embeddings(self, text):
        return call_embedding_model(text)
```

### Model Mapping

- **Text Agent**: LLM (Cheaper/faster model)
- **Vision Agent**: Vision-capable model
- **Similarity Checks**: Embedding model

## 3. Async Job Flow

Page analysis takes 5–15 seconds → handled via background jobs.

1. User clicks ANALYZE
2. API receives URL
3. Task enters Celery queue
4. Worker executes agents in parallel
5. Result is saved to the DB
6. UI polls for the result

## 4. Logical Microservices

- **scraper_service**: Fetches HTML
- **parser_service**: Extracts text and images
- **visual_service**: Ranking + Vision API calls
- **text_service**: Text AI analysis
- **scoring_service**: Calculates final CEPS score

## 5. Caching Strategy

LLM calls are expensive → caching is mandatory.
```python
cache_key = hash(image_url + context_text)
if redis.exists(cache_key):
    return redis.get(cache_key)
else:
    result = vision_call()
    redis.set(cache_key, result, ex=86400) # 24h expiration
```

## 6. Database Schema

### Table: `analyses`

| Field | Type |
|-------|------|
| `id` | UUID |
| `url` | TEXT |
| `ceps_score` | FLOAT |
| `text_score` | FLOAT |
| `visual_score` | FLOAT |
| `ux_score` | FLOAT |
| `trust_score` | FLOAT |
| `tech_score` | FLOAT |
| `created_at` | TIMESTAMP |

## 7. Rate Limiting (Cost Control)

- `MAX_IMAGES_PER_PAGE = 3`
- `MAX_TEXT_CHARS = 8000`

## 8. Security

- Scraping timeouts
- Block oversized pages
- HTML Sanitization

## 9. Scaling Strategy

- **MVP**: 1 worker
- **Growth**: Horizontally scale Celery workers
- **High Load**: Queue prioritization

## 10. End-to-End Flow

1. User enters URL
2. API creates analysis job
3. Scraper → Parser
4. Agents run in parallel (Text, Visual, UX, Trust, Tech)
5. Score Aggregator runs
6. Save to DB
7. UI displays result

## MVP v2 Infrastructure Definition of Done

- [ ] Backend API is operational
- [ ] Background worker system is functional
- [ ] LLM routing layer is implemented
- [ ] Caching is enabled
- [ ] Results are stored in DB
- [ ] UI successfully retrieves results

## Result

This is a scalable AI analysis architecture, yet simple enough for an MVP.