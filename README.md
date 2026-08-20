# Smart Bus Stop AI — Production-Ready System

> **AI-powered suitability analysis, location optimization, and infrastructure recommendation for urban bus stops.**

[![Backend](https://img.shields.io/badge/backend-FastAPI-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Frontend](https://img.shields.io/badge/frontend-React%20%2B%20Vite-61DAFB?logo=react)](https://react.dev)
[![ML](https://img.shields.io/badge/ML-scikit--learn-F7931E?logo=scikit-learn)](https://scikit-learn.org)
[![Docker](https://img.shields.io/badge/docker-compose-2496ED?logo=docker)](https://docs.docker.com/compose)

---

## Overview

The **Smart Bus Stop AI** system helps urban planners and transport engineers decide **where to place, upgrade, or re-route bus stops** using machine-learning suitability scoring and spatial optimization.

Given a location's physical and demand characteristics, the system:
- Predicts a **Suitability Score** (0–100) using a Random Forest surrogate model
- Identifies **positive/negative factors** driving that score
- Recommends **infrastructure upgrades** (shelter size, bus bays, CCTV)
- Finds the **top 5 candidate locations** for a new stop in any radius
- Compares **two locations** side-by-side

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Browser (React)                   │
│  Dashboard │ Analyze │ Compare │ Audit │ Map        │
└────────────────────────┬────────────────────────────┘
                         │ HTTP/REST
┌────────────────────────▼────────────────────────────┐
│               FastAPI Backend (Python)               │
│  /analyze-location   /compare-locations              │
│  /analyze-coordinates /optimize-location             │
│  /bus-stops          /recommend-infrastructure       │
│  /health                                             │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐  │
│  │  ML Service │ │ Rule Engine  │ │  GIS Module  │  │
│  │(Random Forest│ │(Scoring &    │ │(Haversine &  │  │
│  │ Regressor)  │ │ Recs)        │ │ KNN Derive)  │  │
│  └─────────────┘ └──────────────┘ └──────────────┘  │
└────────────────────────┬────────────────────────────┘
                         │ SQLAlchemy
┌────────────────────────▼────────────────────────────┐
│              PostgreSQL 15 (Database)                │
│  bus_stops table (15,000 rows)                       │
│  Spatial index: (Latitude, Longitude)                │
└─────────────────────────────────────────────────────┘
```

**Data Reality Distinction:**
- Inputs provided via the **Analyze form** → `Analysis_Type: "Explicit"` (real user data)
- Inputs derived from a **map coordinate click** → `Analysis_Type: "Derived"` (proximity-interpolated estimate)

---

## Features

| Feature | Description |
|---|---|
| 🗺️ Interactive GIS Map | Drop a pin anywhere; click "Analyze" for instant suitability analysis |
| 📍 Location Optimizer | Select a search radius; get the top 5 candidate stop locations |
| ⚖️ Compare Locations | Side-by-side suitability comparison of two locations |
| 🔍 Existing Stop Audit | Browse 200 sampled stops, sorted by improvement priority |
| 📊 Dashboard | Summary statistics and key KPIs |
| 🛠️ Infrastructure Recommender | Get shelter size and amenity recommendations |
| 🏥 Health Endpoint | `/health` reports DB + ML model status |

---

## Prerequisites

| Tool | Version |
|---|---|
| Python | 3.10+ |
| Node.js | 18+ |
| Docker + Docker Compose | 24+ (for containerised run) |
| PostgreSQL | 15+ (local run only) |

---

## Dataset Setup

The system requires the cleaned CSV dataset to be present at:
```
data/cleaned/bus_stop_optimization_dataset_15000_cleaned.csv
```

**Option A — Use the included cleaned data** (already present in the repo):
```bash
ls data/cleaned/
# bus_stop_optimization_dataset_15000_cleaned.csv  ✓
```

**Option B — Re-run the preprocessing pipeline** (requires raw data in `data/raw/`):
```bash
cd SmartBusStop
python ml/preprocessing/clean_and_eda.py
```

---

## Environment Variables

All configuration is via environment variables. Copy the example:
```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_USER` | `postgres` | PostgreSQL username |
| `POSTGRES_PASSWORD` | `changeme` | **Change in production!** |
| `POSTGRES_DB` | `smartbusstop` | Database name |
| `DATABASE_URL` | auto-built | Full connection string |
| `BACKEND_CORS_ORIGINS` | `["http://localhost:5173"]` | Allowed frontend origins |
| `LOG_LEVEL` | `INFO` | DEBUG, INFO, WARNING, ERROR |
| `APP_ENV` | `production` | development / production |
| `RATE_LIMIT` | `60/minute` | API rate limit |
| `VITE_API_URL` | `http://localhost:8000` | Frontend → backend URL |
| `BACKEND_PORT` | `8000` | Backend host port |
| `FRONTEND_PORT` | `80` | Frontend host port |

---

## Running with Docker Compose (Recommended)

This is the simplest way to run the full stack:

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/SmartBusStop.git
cd SmartBusStop

# 2. Configure environment
cp .env.example .env
# Edit .env: set a strong POSTGRES_PASSWORD

# 3. Build and start all services
docker compose up --build

# Services started:
#   db        → PostgreSQL at localhost:5432
#   db-init   → Seeds bus_stops table (one-shot)
#   backend   → FastAPI at http://localhost:8000
#   frontend  → React app at http://localhost:80
```

Visit **http://localhost** to open the web app.
Visit **http://localhost:8000/docs** for the interactive API documentation.

**Stop all services:**
```bash
docker compose down

# To also delete the database volume:
docker compose down -v
```

---

## Running Locally (Without Docker)

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env to point DATABASE_URL at your local PostgreSQL instance

# (Optional) Seed the database
python scripts/init_db.py

# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API running at: **http://localhost:8000**
Interactive docs: **http://localhost:8000/docs**

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env
# VITE_API_URL=http://localhost:8000

# Start the dev server
npm run dev
```

Web app at: **http://localhost:5173**

---

## Running Tests

### Backend

```bash
cd backend
source venv/bin/activate   # or activate your env

# Run all tests with verbose output
python -m pytest tests/ -v --tb=short

# Run a specific test module
python -m pytest tests/test_engine.py -v
python -m pytest tests/test_api.py -v
```

### Frontend (Lint)

```bash
cd frontend
npm run lint
```

---

## Running the Simulation (Optional)

The SUMO traffic simulation requires a local SUMO installation and is **not included in Docker Compose** due to host-specific graphics/display requirements.

```bash
# Install SUMO (macOS)
brew install sumo

# Run the baseline simulation
python simulation/scripts/run_baseline.py

# Run the optimized scenario
python simulation/scripts/run_optimized.py

# Results are written to simulation/results/
```

See [docs/simulation_architecture.md](docs/simulation_architecture.md) for full details.

---

## API Documentation

All endpoints are documented interactively at `http://localhost:8000/docs`.

### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | System health (DB + ML model status) |
| `POST` | `/analyze-location` | Suitability analysis from explicit features |
| `POST` | `/analyze-coordinates` | Suitability analysis from GPS coordinates |
| `POST` | `/optimize-location` | Find top 5 candidate stop locations |
| `POST` | `/compare-locations` | Side-by-side comparison of two locations |
| `POST` | `/recommend-infrastructure` | Infrastructure recommendations |
| `GET` | `/bus-stops` | Sampled 200 stops with scores |
| `GET` | `/bus-stops/{stop_id}` | Single stop data and analysis |
| `GET` | `/simulation/results` | Latest SUMO simulation report |

### Example: Analyze Location

```bash
curl -X POST http://localhost:8000/analyze-location \
  -H "Content-Type: application/json" \
  -d '{
    "Passenger_Count": 75,
    "Boarding": 40,
    "Alighting": 35,
    "Road_Width": 12.0,
    "Walking_Distance_m": 150.0,
    "Distance_to_Next_Stop_m": 600.0,
    "Traffic_Level": "Moderate",
    "Bus_Frequency": 10,
    "Waiting_Time_min": 5,
    "Occupancy_pct": 70.0
  }'
```

### Traffic Level Values

`Traffic_Level` must be one of: `"Low"`, `"Moderate"`, `"High"`

### Hard Constraints (Score → 0)

- `Road_Width < 6 m`
- `Distance_to_Next_Stop_m < 200 m`

---

## Project Structure

```
SmartBusStop/
├── backend/
│   ├── app/
│   │   ├── api/endpoints.py        # All API route handlers
│   │   ├── core/
│   │   │   ├── config.py           # Settings (pydantic-settings)
│   │   │   └── database.py         # SQLAlchemy engine + session
│   │   ├── models/
│   │   │   ├── domain.py           # SQLAlchemy ORM model
│   │   │   └── schemas.py          # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── engine.py           # Deterministic scoring rules
│   │   │   ├── gis.py              # Haversine + feature derivation
│   │   │   ├── ml_service.py       # ML model loading + inference
│   │   │   └── optimization.py     # Grid search optimizer
│   │   └── main.py                 # App factory, middleware, /health
│   ├── scripts/init_db.py          # Database seeding script
│   ├── tests/                      # pytest test suite
│   │   ├── conftest.py
│   │   ├── test_engine.py
│   │   ├── test_gis.py
│   │   ├── test_optimization.py
│   │   └── test_api.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/                  # Route-level React pages
│   │   ├── components/             # Reusable UI components
│   │   └── services/api.ts         # Typed Axios API client
│   ├── nginx.conf                  # Production Nginx config
│   ├── Dockerfile
│   └── .env.example
├── ml/
│   ├── models/                     # Trained .pkl files
│   ├── preprocessing/              # Data cleaning scripts
│   └── training/                   # Model training scripts
├── data/
│   ├── cleaned/                    # Cleaned CSV datasets
│   └── raw/                        # Original source data
├── simulation/                     # SUMO simulation files
├── docs/                           # Reports and documentation
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Troubleshooting

**Backend 500 errors on start?**
→ Ensure `ml/models/best_reg_model.pkl` exists. Run the training pipeline if not.

**Frontend can't reach backend?**
→ Check `VITE_API_URL` in `.env` matches where the backend is running.

**Docker: backend exits immediately?**
→ The ML model file may be missing. Check `docker compose logs backend`.

**Database connection refused?**
→ PostgreSQL may not be ready yet. The `db-init` service retries automatically. For local runs, ensure PostgreSQL is running and `DATABASE_URL` is correct.
