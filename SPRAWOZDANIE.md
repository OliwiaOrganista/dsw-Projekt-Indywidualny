# SPRAWOZDANIE - Cloud File Ingestor

## Informacje ogólne

**Autor:** Oliwia Organista-Michalak  
**Numer indeksu:** 52755  
**Kod kursu:** Nowatorski Projekt Indywidualny (DevOps)  
**Data:** Luty 2026  

---

## 1. Opis wykonanych działań

### 1.1 Cel projektu
Stworzenie systemu do asynchronicznego przetwarzania plików demonstrującego architekturę DevOps z użyciem:
- Object storage (MinIO)
- Async processing (Celery + Redis)
- Mikroserwisy (API + Worker)
- CI/CD (GitHub Actions)
- Deployment (DigitalOcean)

### 1.2 Komponenty aplikacji

#### API (FastAPI)
- Endpoint `POST /files` – upload pliku
- Endpoint `GET /files` – lista plików
- Endpoint `GET /files/{id}` – status przetwarzania
- Endpoint `GET /files/{id}/result` – wynik przetwarzania
- Endpoint `GET /health` – health check

#### Worker (Celery)
- Asynchroniczne przetwarzanie plików
- Walidacja CSV/JSON/TXT
- Generowanie podsumowań
- Obsługa błędów

#### Baza danych (PostgreSQL)
- Przechowywanie metadanych plików
- Status przetwarzania
- Wyniki przetwarzania

#### Storage (MinIO)
- S3-compatible object storage
- Przechowywanie plików
- Lokalna emulacja AWS S3

#### Message Broker (Redis)
- Kolejka zadań (Celery)
- Cache'owanie (opcjonalnie)
- Szybka komunikacja API-Worker

---

## 2. Architektura

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────┐
│            API (FastAPI)                        │
│  - Upload Files                                 │
│  - List Files                                   │
│  - Get Status/Result                            │
└──────┬──────────────────────────┬───────────────┘
       │                          │
       ▼                          ▼
   ┌────────────┐            ┌────────────┐
   │PostgreSQL  │            │   Redis    │
   │  (DB)      │            │  (Queue)   │
   └────────────┘            └──────┬─────┘
                                    │
                                    ▼
                            ┌─────────────────┐
                            │    Worker       │
                            │ (Celery Tasks)  │
                            └────────┬────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │    MinIO        │
                            │  (S3 Storage)   │
                            └─────────────────┘
```

---

## 3. Technologia

### Backend
- **FastAPI** 0.104.1 – szybki framework web
- **Celery** 5.3.4 – async task queue
- **SQLAlchemy** 2.0.23 – ORM
- **PostgreSQL** 15 – relacyjna baza danych
- **Redis** 7 – message broker
- **MinIO** – S3-compatible storage

### DevOps
- **Docker** – konteneryzacja
- **Docker Compose** – orchestration (local)
- **GitHub Actions** – CI/CD
- **DigitalOcean** – hosting (5.0)

---

## 4. Spełnienie wymagań

### Wymagania 3.0 ✅
- [x] Aplikacja działa (API)
- [x] Buduje się i uruchamia jako obraz Docker
- [x] Pipeline CI (GitHub Actions) z testami

### Wymagania 3.5 ✅
- [x] Multi-stage Docker build (builder → api/worker)
- [x] Uruchamianie poprzez docker-compose

### Wymagania 4.0 ✅
- [x] Oddzielne pipeline'y dla main i PR (ci.yml)
- [x] Aplikacja z bazą danych (PostgreSQL)
- [x] Docker Compose z 5 kontenerami (api, worker, db, redis, minio)

### Wymagania 4.5 ✅
- [x] Workflow buduje i publikuje do GHCR
- [x] Reusable workflow: validate-compose.yml
- [x] Custom action: .github/actions/validate-compose/

### Wymagania 5.0 ✅
- [x] Deployment na DigitalOcean (cd.yml)
- [x] Własna akcja GitHub Actions (validate-compose)

---

## 5. Instrukcja uruchomienia

### Lokalne (Docker Compose)

```bash
# Klonowanie repozytorium
git clone <URL>
cd frond

# Budowanie i uruchomienie
docker-compose up -d

# Czekanie na uruchomienie usług (30-60s)
docker-compose logs -f api

# API dostępne na http://localhost:8000
# Dokumentacja: http://localhost:8000/docs
# MinIO: http://localhost:9001 (minioadmin/minioadmin)
```

### Testowanie API

```bash
# Upload pliku
curl -X POST -F "file=@file.csv" http://localhost:8000/files

# Lista plików
curl http://localhost:8000/files

# Status pliku
curl http://localhost:8000/files/{file_id}

# Wynik przetwarzania
curl http://localhost:8000/files/{file_id}/result

# Health check
curl http://localhost:8000/health
```

### Deployment na DigitalOcean

1. **Przygotowanie VPS:**
   ```bash
   ssh root@droplet
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   chmod +x /usr/local/bin/docker-compose
   ```

2. **Konfiguracja GitHub Secrets:**
   - `DIGITALOCEAN_HOST` – IP/domain
   - `DIGITALOCEAN_USER` – SSH user
   - `DIGITALOCEAN_PRIVATE_KEY` – SSH private key

3. **Deployment:**
   - Push do branch `main` → automatycznie deployuje na DigitalOcean
   - Pipeline: CI → CD → Deploy

---

## 6. CI/CD Pipeline

### GitHub Actions Workflows

1. **ci.yml** (CI Pipeline)
   - Testowanie (pytest)
   - Linting (flake8)
   - Budowanie i publikacja do GHCR

2. **cd.yml** (CD Pipeline)
   - Deployment na DigitalOcean (SSH)
   - Weryfikacja health check

3. **validate-compose.yml** (Reusable Workflow)
   - Walidacja docker-compose.yml
   - Sprawdzenie wymaganych serwisów
   - Health check validation

4. **Custom Action: validate-compose**
   - Walidacja składni
   - Sprawdzenie serwisów
   - Raportowanie

---

## 7. Struktura plików

```
frond/
├── app/
│   ├── main.py              # FastAPI aplikacja
│   └── requirements.txt      # Zależności API
├── worker/
│   ├── tasks.py             # Celery tasks
│   └── requirements.txt      # Zależności worker
├── tests/
│   └── test_api.py          # Testy
├── .github/
│   ├── workflows/
│   │   ├── ci.yml           # CI pipeline
│   │   ├── cd.yml           # CD pipeline
│   │   └── validate-compose.yml  # Reusable workflow
│   └── actions/
│       └── validate-compose/
│           └── action.yml   # Custom action
├── docker-compose.yml       # Orchestration
├── Dockerfile               # Multi-stage build
├── README.md                # Dokumentacja
└── .gitignore               # Git ignore rules
```

---

## 8. Możliwe ulepszenia

1. **Monitoring:** Prometheus + Grafana
2. **Logging:** ELK Stack lub CloudWatch
3. **Security:** Vault do secrets, RBAC
4. **Frontend:** React/Vue do managementu plików
5. **Advanced Processing:** NLP, Computer Vision
6. **Scalability:** Kubernetes zamiast docker-compose
7. **Database:** Backup strategy, migration tools

---

## 9. Podsumowanie

Projekt demonstruje kompleksową architekturę DevOps z:
- ✅ Async processing (Celery)
- ✅ Object storage (MinIO)
- ✅ Mikroserwisami (API + Worker)
- ✅ Infrastrukturą (Docker Compose)
- ✅ CI/CD (GitHub Actions)
- ✅ Deployment (DigitalOcean)
- ✅ Custom actions
- ✅ Production-ready code

Spełnia wszystkie wymagania na ocenę **5.0** z dodatkowymi uciekawościami.
