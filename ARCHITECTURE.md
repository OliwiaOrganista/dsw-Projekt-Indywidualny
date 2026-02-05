# PROJECT STRUCTURE

```
frond/
├── 📄 README.md                       # Quick start & overview
├── 📄 SPRAWOZDANIE.md                 # Polish detailed report
├── 📄 INSTALLATION.md                 # Installation & deployment guide
├── 📄 Makefile                        # Make commands for convenience
│
├── 🐳 Dockerfile                      # Multi-stage build (api + worker)
├── 🐳 docker-compose.yml              # Local orchestration (5 services)
├── 📝 .env.example                    # Environment variables template
├── 📝 .gitignore                      # Git ignore rules
│
├── 📁 app/                            # FastAPI Application
│   ├── main.py                        # FastAPI app, endpoints, tasks
│   ├── requirements.txt               # Python dependencies
│   └── __init__.py
│
├── 📁 worker/                         # Celery Worker
│   ├── tasks.py                       # Celery tasks, file processing
│   ├── requirements.txt               # Worker dependencies
│   └── __init__.py
│
├── 📁 tests/                          # Testing
│   ├── test_api.py                    # API endpoint tests
│   ├── test_db.py                     # Database model tests
│   ├── integration.sh                 # Integration test script
│   └── __init__.py
│
├── 📁 .github/                        # GitHub configuration
│   ├── workflows/
│   │   ├── ci.yml                     # CI pipeline (test, lint, build)
│   │   ├── cd.yml                     # CD pipeline (deploy to DigitalOcean)
│   │   └── validate-compose.yml       # Reusable compose validation
│   └── actions/
│       └── validate-compose/
│           └── action.yml             # Custom GitHub Action
│
├── 🚀 setup.sh                        # Automated setup (Linux/macOS)
├── 🚀 setup.bat                       # Automated setup (Windows)
├── 🚀 deploy.sh                       # Manual deployment script
│
├── 📊 pytest.ini                      # Pytest configuration
│
└── .git/                              # Git repository

```

---

## Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CLIENT                               │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────┐
        │        API (FastAPI) - Port 8000       │
        ├────────────────────────────────────────┤
        │ • POST /files                          │
        │ • GET /files                           │
        │ • GET /files/{id}                      │
        │ • GET /files/{id}/result               │
        │ • GET /health                          │
        └────────┬─────────────────────┬─────────┘
                 │                     │
         ┌───────▼─────────┐   ┌──────▼──────────┐
         │   PostgreSQL    │   │     Redis       │
         │   (Port 5432)   │   │  (Port 6379)    │
         ├─────────────────┤   ├─────────────────┤
         │ • Metadata      │   │ • Task Queue    │
         │ • Results       │   │ • Caching       │
         │ • User data     │   │ • Broker        │
         └────────┬────────┘   └────────┬────────┘
                  │                     │
                  │                     ▼
                  │         ┌────────────────────────┐
                  │         │  Worker (Celery)       │
                  │         ├────────────────────────┤
                  │         │ • File processing      │
                  │         │ • CSV validation       │
                  │         │ • Async tasks          │
                  │         │ • Error handling       │
                  │         └────────┬───────────────┘
                  │                  │
                  └──────────┬───────┘
                             │
                             ▼
                  ┌────────────────────────┐
                  │  MinIO (Port 9000)     │
                  ├────────────────────────┤
                  │ • Object Storage       │
                  │ • S3-compatible API    │
                  │ • File persistence     │
                  └────────────────────────┘
```

---

## Services Overview

### API Service
- **Technology:** FastAPI + Uvicorn
- **Port:** 8000
- **Function:** Handle HTTP requests, upload files, manage status
- **Database:** Connected to PostgreSQL
- **Queue:** Uses Redis via Celery

### Worker Service
- **Technology:** Celery + Python
- **Function:** Process files asynchronously
- **Broker:** Redis
- **Tasks:** File validation, summarization, result storage

### Database Service
- **Technology:** PostgreSQL 15
- **Port:** 5432
- **Data:** File metadata, processing results, user data
- **Volumes:** Persistent `postgres_data`

### Queue Service
- **Technology:** Redis
- **Port:** 6379
- **Function:** Celery broker, task queue, optional caching

### Storage Service
- **Technology:** MinIO (S3-compatible)
- **Port:** 9000 (API), 9001 (Console)
- **Function:** Object storage, file persistence
- **Volumes:** Persistent `minio_data`

---

## Deployment Architecture

```
┌──────────────────────────────────────────────────────┐
│              GitHub Repository                       │
├──────────────────────────────────────────────────────┤
│ • Source code                                        │
│ • GitHub Actions workflows                          │
│ • Custom actions                                    │
└────────────────┬─────────────────────────────────────┘
                 │
        ┌────────▼─────────┐
        │ GitHub Actions   │
        ├──────────────────┤
        │ 1. Test (pytest) │
        │ 2. Lint (flake8) │
        │ 3. Build (Docker)│
        │ 4. Push (GHCR)   │
        │ 5. Deploy (SSH)  │
        └────────┬─────────┘
                 │
                 ▼
        ┌──────────────────────────────────┐
        │   GitHub Container Registry      │
        │   (ghcr.io/owner/repo)          │
        ├──────────────────────────────────┤
        │ • api:latest                     │
        │ • api:sha                        │
        │ • worker:latest                  │
        │ • worker:sha                     │
        └────────┬─────────────────────────┘
                 │
                 ▼
        ┌──────────────────────────────────┐
        │   DigitalOcean Droplet           │
        │   (Production Environment)       │
        ├──────────────────────────────────┤
        │ • Docker Engine                  │
        │ • docker-compose                 │
        │ • Running services               │
        │ • Persistent volumes             │
        └──────────────────────────────────┘
```

---

## File Types

| Type | Files | Purpose |
|------|-------|---------|
| 🐍 Python | main.py, tasks.py, test_*.py | Application logic |
| 🐳 Docker | Dockerfile, docker-compose.yml | Containerization |
| 🔄 CI/CD | ci.yml, cd.yml, action.yml | Automation |
| 📝 Docs | README.md, SPRAWOZDANIE.md, INSTALLATION.md | Documentation |
| ⚙️ Config | .env.example, pytest.ini, Makefile | Configuration |
| 📦 Dependencies | requirements.txt | Python packages |

---

## Development Workflow

```
1. Development
   └─ Edit code → Test locally

2. Version Control
   └─ git add/commit → git push origin

3. CI Pipeline (Automated)
   └─ Test → Lint → Build → Publish

4. CD Pipeline (Automated)
   └─ Deploy to Staging → Health Check

5. Production
   └─ Manual approval or auto-deploy

6. Monitoring
   └─ Logs → Health checks → Rollback if needed
```

---

## Key Files Description

### Dockerfile
- **Multi-stage build:** builder → api + worker
- **Stage 1:** Builds dependencies (Builder)
- **Stage 2:** Runtime API image
- **Stage 3:** Runtime Worker image
- **Benefits:** Smaller images, separation of concerns

### docker-compose.yml
- **5 Services:** api, worker, db, redis, minio
- **Networks:** Automatic service discovery
- **Volumes:** Persistent data
- **Health checks:** Automatic service monitoring
- **Environment:** Configuration management

### GitHub Actions Workflows
- **ci.yml:** Test, lint, build, and publish on every push
- **cd.yml:** Deploy to DigitalOcean on main branch
- **validate-compose.yml:** Reusable workflow for validation
- **Custom action:** Validate docker-compose configuration

### Python Files
- **app/main.py:** FastAPI routes, database models, Celery tasks
- **worker/tasks.py:** Celery task definitions, file processing logic
- **tests/test_*.py:** Unit and integration tests

---

## Technology Stack Summary

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Framework | FastAPI | 0.104.1 | Web API |
| Worker | Celery | 5.3.4 | Async processing |
| Database | PostgreSQL | 15 | Data persistence |
| Queue | Redis | 7 | Message broker |
| Storage | MinIO | latest | Object storage |
| Container | Docker | latest | Containerization |
| Orchestration | Docker Compose | 2.0+ | Local orchestration |
| CI/CD | GitHub Actions | native | Automation |
| Testing | pytest | latest | Unit tests |
| Linting | flake8 | latest | Code quality |

---

**Generated:** February 2026  
**Project Status:** ✅ Production Ready
