# vector-engine-alan-vo — Alan Vo

> Work in progress. This checkpoint may be incomplete or fail tests. See PLAN.md and STATUS.md before use.


> Vector embedding and similarity search engine for AI/ML applications

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm 9+

### Backend Setup
```bash
cd backend
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Run Tests
```bash
# Backend tests
cd backend
venv/bin/pytest tests/ -v

# Frontend tests
cd frontend
npm test
```

### Build Frontend for Production
```bash
cd frontend
npm run build
```

## Configuration

Copy `.env.example` to `.env` and adjust values:
- `DATABASE_URL` — SQLite path (default: `sqlite+aiosqlite:///./data/vector_engine.db`)
- `CORS_ORIGINS` — Comma-separated allowed origins
- `VITE_API_BASE` — Frontend API base URL (default: `http://127.0.0.1:8000/health`)

## Project Structure

```
backend/
  app/
    api/v1/health.py      # Health check endpoints
    core/config.py        # Pydantic settings
    core/database.py      # SQLAlchemy async setup
    main.py               # FastAPI app factory
  requirements.txt
  tests/
frontend/
  src/
    App.tsx               # Health dashboard
    api/client.ts         # API client
    main.tsx              # Entry point
  index.html              # Vite entry
  package.json
  vite.config.ts
```

## License

MIT — Alan Vo <alanvo@gmail.com>
