# PhishGuard 🛡️

**AI-Powered Phishing Detection & Real-Time Browser Protection**

> IIT Guwahati Coding Club — Even Semester 2026

## Overview

PhishGuard is a production-grade phishing detection system with three core components:

1. **FastAPI Backend** — 47-feature ML inference, threat intelligence, LLM explanations
2. **Chrome Extension (WXT)** — Real-time browser protection with glassmorphic overlays
3. **Next.js 15 Dashboard** — Analyst SOC dashboard with real-time feeds and threat maps

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Chrome Extension │────▶│   FastAPI API     │◀────│  Next.js 15     │
│   (WXT/MV3)     │     │   (Backend)       │     │  Dashboard      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
              ┌──────────┐ ┌──────┐ ┌────────┐
              │PostgreSQL│ │Redis │ │Qdrant  │
              │   16     │ │  7   │ │ VecDB  │
              └──────────┘ └──────┘ └────────┘
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+ (for local dashboard dev)
- Python 3.11+ (for local backend dev)

### Run with Docker
```bash
cp .env.example .env
# Fill in API keys in .env
make dev
```

### Run Locally (without Docker)

**Backend:**
```bash
cd backend
pip install -r requirements.txt
python -m app.ml.train          # Train ML model
uvicorn app.main:app --reload   # Start API server
```

**Dashboard:**
```bash
cd dashboard
npm install
npm run dev
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/scan/url` | Scan a URL for phishing |
| POST | `/api/v1/scan/email` | Scan email links |
| POST | `/api/v1/scan/batch` | Batch URL scan |
| GET | `/api/v1/reports/summary` | Scan statistics |
| GET | `/api/v1/reports/scans` | Paginated scan history |
| GET | `/api/v1/reports/export/stix` | STIX 2.1 export |
| POST | `/api/v1/feedback/submit` | Report false positives |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |
| GET | `/stream/scans` | SSE live feed |

## Technology Stack

- **Backend:** FastAPI, SQLAlchemy (async), LightGBM, Groq LLM
- **Frontend:** Next.js 15, Framer Motion, Recharts, Zustand
- **Extension:** WXT (Manifest V3), TypeScript
- **Database:** PostgreSQL 16, Redis 7, Qdrant
- **ML:** LightGBM, DistilBERT, 47-feature extraction
- **Observability:** Prometheus, Grafana, Loki, structlog
