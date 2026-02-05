# Cloud File Ingestor - Projekt DevOps

## 📋 Szybki Start

```bash
docker-compose up -d
```

API: http://localhost:8000  
Dokumentacja: http://localhost:8000/docs  
MinIO: http://localhost:9001

---

## 🏗️ Architektura

Asynchroniczny system przetwarzania plików z:
- **API** (FastAPI) – Upload i statusy plików
- **Worker** (Celery) – Asynchroniczne przetwarzanie
- **Baza danych** (PostgreSQL) – Metadane i wyniki
- **Storage** (MinIO) – Object storage
- **Kolejka** (Redis) – Broker zadań

---

## 🚀 Endpointy API

| Metoda | Endpoint | Opis |
|--------|----------|------|
| POST | `/files` | Upload pliku |
| GET | `/files` | Lista plików |
| GET | `/files/{id}` | Status pliku |
| GET | `/files/{id}/result` | Wynik przetwarzania |
| GET | `/health` | Health check |

---

## 📝 Upload i Przetwarzanie

```bash
# Upload pliku
curl -X POST -F "file=@data.csv" http://localhost:8000/files

# Sprawdzenie statusu
curl http://localhost:8000/files/{id}

# Pobranie wyniku
curl http://localhost:8000/files/{id}/result
```

---

## 🐳 Serwisy Docker Compose

- **api** (port 8000) – Aplikacja FastAPI
- **worker** – Procesor zadań Celery
- **db** (port 5432) – PostgreSQL
- **redis** (port 6379) – Message broker
- **minio** (port 9000/9001) – S3-compatible storage

---

## 🔄 CI/CD Pipeline'y

### GitHub Actions

1. **ci.yml** – Testy, linting, build i publikacja do GHCR
2. **cd.yml** – Deployment na DigitalOcean
3. **validate-compose.yml** – Reusable workflow
4. **Custom Action** – validate-compose

### Funkcjonalności

- ✅ Multi-stage Docker builds
- ✅ Automatyczne testy
- ✅ Publikacja obrazów do rejestru
- ✅ Deployment na VPS
- ✅ Health checks
- ✅ Reusable workflows
- ✅ Custom actions

---

## 📦 Wymagania (Ocena 5.0)

- [x] 3.0: Działająca aplikacja + Docker + CI pipeline
- [x] 3.5: Multi-stage + docker-compose
- [x] 4.0: Oddzielne pipeline'y + baza danych + 2+ kontenery
- [x] 4.5: Publikacja do rejestru + reusable workflow
- [x] 5.0: Deployment na VPS + custom actions

---

## 🔐 Konfiguracja Deployment'u

Ustaw GitHub Secrets:
- `DIGITALOCEAN_HOST` – IP/domena VPS
- `DIGITALOCEAN_USER` – Użytkownik SSH
- `DIGITALOCEAN_PRIVATE_KEY` – Klucz SSH

Push do gałęzi `main` → automatycznie wdrażane na DigitalOcean

---

## 📚 Dokumentacja

Pełną dokumentację znajdziesz w [SPRAWOZDANIE.md](SPRAWOZDANIE.md).

---

**Status:** Gotowe do wdrożenia ✅
