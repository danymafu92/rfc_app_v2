<!--
Short, actionable Copilot instructions for rfc_app_v2 (Django + React + Supabase).
Keep this file concise and reference specific files/commands.
-->

# Copilot instructions for rfc_app_v2

Backend: Django REST Framework project in `weather_prediction/` exposing APIs under `/api` (see `api/views.py`, `api/urls.py`).
Frontend: React + Vite in `frontend/` — Vite dev server proxies `/api` to Django (see `vite.config.js` and `frontend/src/services/api.js`).
Auth/DB: Supabase (Postgres + Auth). Backend accepts Supabase access tokens via `api/authentication.py`.

Start here (high signal files):
- `weather_prediction/settings.py` — env keys, `ML_MODELS_DIR`, REST defaults
- `api/authentication.py`, `api/views.py`, `api/serializers.py`, `api/urls.py`
- `ml_models/*.py` — model wrappers and `predict(features: Dict) -> Dict` contract
- `frontend/src/services/api.js`, `frontend/src/services/supabase.js` — how client adds Authorization header
- `supabase/migrations/*.sql` — expected DB schema

Core architecture (big picture)
- Django REST API serves ML prediction endpoints under `/api/*` and expects bearer tokens from Supabase. See `api/views.py` for how ML wrappers are called.
- Frontend is a Vite React SPA that never hardcodes backend host; it calls relative `/api` endpoints. Vite proxies `/api` to Django for dev (see `vite.config.js`).
- ML wrappers live in `ml_models/` and try to load `*.pkl` models from `ML_MODELS_DIR` (configured in `settings.py`). If load fails, `predict()` returns deterministic fallbacks — tests depend on this behavior (`tests/test_ml_wrappers.py`).

Dev workflows & commands
- Backend: install via `pip install -r requirements.txt`, set env vars (see `.env.example` if present), then run `python manage.py runserver` (default http://localhost:8000).
- Frontend: from repo root run `npm install` then `npm run dev` (Vite dev server at http://localhost:5173). Vite proxies `/api` to the Django backend.
- Tests: Run unit tests with `python -m unittest` (the repo includes `tests/test_ml_wrappers.py`).

Project-specific conventions & gotchas
- All API endpoints default to Django REST `IsAuthenticated` (check `REST_FRAMEWORK` in `weather_prediction/settings.py`). Requests must include `Authorization: Bearer <supabase_access_token>`.
- Backend does not verify Supabase JWT signatures locally — `api/authentication.py` extracts user info from the token in a permissive way for dev. When testing APIs from curl/Postman include a real Supabase access token.
- ML wrapper contract: keep `predict(features: Dict) -> Dict`. Views call this and expect fallback behavior when model files are missing.
- Frontend auth flow: `frontend/src/services/api.js` uses `supabase.auth.getSession()` to attach the token. Do not hardcode tokens or backend origins in frontend code.

Where to update code when changing shapes or contracts
- API input/output shape changes → update `api/serializers.py` and matching viewsets in `api/views.py` and register routes in `api/urls.py`.
- ML model behavior changes → update `ml_models/*` wrappers and `tests/test_ml_wrappers.py`.

Quick example (curl)
curl -X POST http://localhost:8000/api/rainfall-predictions/predict/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"location_id": 1}'

Troubleshooting tips
- 403 / No API response: ensure a Supabase session token is present. The frontend sets this automatically; API clients must include it.
- Missing ML models: look at `weather_prediction/settings.py` for `ML_MODELS_DIR`; wrappers will fall back if `.pkl` files are absent.
- DB connection errors: repo expects an existing Supabase schema — inspect `supabase/migrations/` for SQL definitions.

If you need endpoint-by-endpoint payload examples, automated tests for ML wrappers, or help wiring CI/CD, ask which area to expand.

-- EOF
<!--
Short, actionable Copilot instructions for rfc_app_v2 (Django + React + Supabase).
Keep this file concise and reference specific files/commands.
-->

# Copilot instructions for rfc_app_v2

Backend: Django REST Framework project `weather_prediction/` exposing APIs under `/api` (see `api/views.py`, `api/urls.py`).
Frontend: React + Vite in `frontend/` — Vite dev server proxies `/api` to Django (see `vite.config.js` and `frontend/src/services/api.js`).
Auth/DB: Supabase (Postgres + Auth). Backend uses `api/authentication.py` to accept Supabase access tokens.

Key files to read first:
- `weather_prediction/settings.py` (env keys, `ML_MODELS_DIR`, REST settings)
- `api/authentication.py`, `api/views.py`, `api/urls.py`, `api/serializers.py`
- `ml_models/*.py` (model loading, `predict()` contract, fallback behavior)
- `frontend/src/services/api.js`, `frontend/src/services/supabase.js` (how the client adds Authorization headers)
- `supabase/migrations/*.sql` (expected DB schema)

Quick dev commands:
- Backend: `pip install -r requirements.txt` then set env vars and `python manage.py runserver` (http://localhost:8000)
- Frontend: `npm install` then `npm run dev` from repo root (Vite serves at http://localhost:5173 and proxies `/api`)
- Build frontend: `npm run build` → outputs `frontend/build` (Django will serve static files if present)

Project-specific patterns & gotchas:
- All API endpoints default to IsAuthenticated (check `REST_FRAMEWORK` in settings). Requests must include `Authorization: Bearer <supabase_access_token>`.
- Frontend never hardcodes backend host — use relative `/api` endpoints. The axios interceptor in `frontend/src/services/api.js` injects the Supabase token.
- ML wrappers live in `ml_models/`. They attempt to load a `*.pkl` from `ML_MODELS_DIR`. If load fails, `predict(features: Dict) -> Dict` returns deterministic fallbacks (see `tests/test_ml_wrappers.py`).
- There are no Django migrations in `api/migrations/` — the repo expects an existing Supabase schema; inspect `supabase/migrations/` for SQL.

When making changes:
- API shape changes -> update `api/serializers.py` and corresponding viewsets in `api/views.py`, then register routes in `api/urls.py`.
- Preserve the ML wrapper contract: `predict(features: Dict) -> Dict` and fallback behavior unless intentionally changing defaults.

Quick example (curl):
curl -X POST http://localhost:8000/api/rainfall-predictions/predict/ \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"location_id": 1}'

If anything is unclear or you want endpoint-by-endpoint example payloads or automated tests for ML wrappers, tell me which area to expand.
<!--
Purpose: Short, actionable instructions for AI coding assistants working on this repo.
Keep this file concise (~20-50 lines). Reference concrete files and commands below.
-->
# Copilot instructions for rfc_app_v2

This repository is a Django + React app for weather predictions. Use these notes to be productive quickly.

Core architecture (big picture)
- Backend: Django REST Framework (project: `weather_prediction/`) exposing APIs under `/api` (see `api/views.py`, `api/urls.py`).
- Frontend: React + Vite in `frontend/` — dev server proxies `/api` to Django (see `vite.config.js`).
- Data & Auth: Supabase (Postgres + Auth). Backend uses a Supabase JWT-based authentication adapter (`api/authentication.py`).
- Models: Lightweight ML wrappers in `ml_models/` (e.g. `rainfall_model.py`) that load `*.pkl` joblib models from `ML_MODELS_DIR`.

Quick developer workflows
- Install backend deps: `pip install -r requirements.txt` (root `requirements.txt`).
- Run Django dev server: `python manage.py runserver` (default http://localhost:8000).
- Install frontend deps and run: `npm install` then `npm run dev` in repo root (Vite root is `frontend/`). Frontend dev runs on http://localhost:5173 and proxies `/api` → `http://localhost:8000`.
- Build frontend for production: `npm run build` (outputs to `frontend/build`) — Django will serve static files from there if present.

Important environment variables (see `.env.example`)
- VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY — used by the frontend and also read by backend as `SUPABASE_URL` / `SUPABASE_KEY` in `settings.py`.
- DJANGO_SECRET_KEY, DEBUG, DB_* (DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT) — backend DB settings.

Authentication & API notes
- All API endpoints default to `IsAuthenticated` (see `REST_FRAMEWORK` in `weather_prediction/settings.py`).
- Frontend adds Supabase session token to requests using `frontend/src/services/api.js` (axios interceptor). The backend accepts a Bearer token and extracts user info without verifying signature (`api/authentication.py`).
- When testing APIs from tools (curl/Postman), include `Authorization: Bearer <access_token>` (a Supabase session access token).

ML models and fallbacks
- Model files are expected in `ML_MODELS_DIR` (set in `weather_prediction/settings.py`, defaults to `<repo>/ml_models`).
- If a model file is missing or fails to load, ML wrappers (e.g. `ml_models/rainfall_model.py`) return deterministic fallback predictions — check `predict()` for the fallback logic before changing behavior.

Database & migrations
- Supabase is the production DB; repo contains SQL migration(s) under `supabase/migrations/` (e.g. `20251017173107_create_initial_schema.sql`).
- Local development can point to a local Postgres via DB_* env vars. There are no Django migration files in `api/migrations/` beyond `__init__.py` — the repo assumes an existing Supabase schema.

Frontend ↔ Backend integration patterns
- Vite server proxies `/api` to Django — do not hardcode `http://localhost:8000` in frontend code; use relative `/api` endpoints (see `frontend/src/services/api.js`).
- Axios interceptor fetches current Supabase session: `supabase.auth.getSession()` and adds `Authorization: Bearer <token>` to API requests.

Files to read first (highest signal)
- `weather_prediction/settings.py` — env, ML path, REST framework defaults.
- `api/views.py` and `api/urls.py` — canonical API behavior and route names.
- `frontend/src/services/api.js` and `frontend/src/services/supabase.js` — how the client authenticates and calls the API.
- `ml_models/*.py` — model loading, fallback, training signatures.
- `supabase/migrations/*.sql` — DB schema expected by the app.

Conventions & gotchas
- API endpoints require authentication; local dev may need a Supabase session or a valid JWT to exercise endpoints.
- ML model training functions exist in the wrappers (`train`, `update_model`) — they save to `model_path` when set.
- Static files: production Django serves built frontend from `frontend/build`. `settings.py` adds `frontend/build/static` to `STATICFILES_DIRS` only when that folder exists.

When making changes
- Update the corresponding serializer (`api/serializers.py`) when changing API input/output shapes.
- Add viewset actions in `api/views.py` and register routes in `api/urls.py` via the DefaultRouter.
- For ML changes, preserve the `predict(features: Dict) -> Dict` contract used by the views (see examples in `views.py`).

If anything is unclear or you need additional examples (tests, CI, or deployment commands), ask for the area and I will expand this file.

Try it — quick commands and example API calls
- Install and start backend (one terminal):

```bash
pip install -r requirements.txt
export DJANGO_SECRET_KEY=devkey
export DEBUG=True
python manage.py runserver
```

- Start frontend (separate terminal):

```bash
npm install
npm run dev
```

- Example: call rainfall predict endpoint (replace <TOKEN> and <LOCATION_ID>):

```bash
curl -X POST http://localhost:8000/api/rainfall-predictions/predict/ \
	-H "Authorization: Bearer <TOKEN>" \
	-H "Content-Type: application/json" \
	-d '{"location_id": <LOCATION_ID>}'
```

Debugging checklist (common issues)
- No API response / 403: Ensure Supabase session token is present. Use the browser devtools network tab to inspect the Authorization header set by `frontend/src/services/api.js`.
- Missing ML model files: Check `weather_prediction/settings.py` for `ML_MODELS_DIR` and place `*.pkl` models there or rely on fallback logic in `ml_models/*.py`.
- Frontend 404 for /api routes: Confirm Vite proxy (see `vite.config.js`) is running and backend at http://localhost:8000.
- DB connection errors: Ensure DB_* env vars point to a reachable Postgres (Supabase or local). The repo expects an existing schema from `supabase/migrations/`.

---

If you'd like, I can expand the examples with curl + sample JSON responses for each prediction endpoint and a short set of tests to validate the ML wrappers.
