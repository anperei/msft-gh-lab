# AI Agent Instructions for Inventory Management App

## Project Overview
A full-stack device inventory manager: React + TypeScript frontend, FastAPI Python backend, Azure Cosmos DB backend. Deployed via Azure Container Apps using Infrastructure-as-Code.

## Architecture

**Three-layer design:**
- **Frontend** (React/Vite/TS): `frontend/src/App.tsx` orchestrates UI state and API calls to `/api/devices`
- **Backend** (FastAPI): `backend/src/main.py` exposes REST API (CRUD for devices), routes to pluggable storage
- **Storage**: Cosmos DB (production) or in-memory dict (testing); clients use `DefaultAzureCredential` for managed identity auth

**Key insight:** The backend uses an **abstraction layer** at `backend/src/repositories/__init__.py` that selects either `cosmos_repo.py` (production) or `in_memory.py` (TEST_MODE) at import time, eliminating the need for Azure connectivity in local development.

## Build & Run

**Backend** (Python 3.11+ required):
```bash
cd backend
uv sync                              # Install dependencies via uv (Python package manager)
TEST_MODE=true uv run uvicorn src.main:app --reload  # Local with in-memory data
# or without TEST_MODE: requires COSMOS_ENDPOINT, COSMOS_DB_NAME, COSMOS_DEVICES_CONTAINER env vars
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev         # Vite dev server on :5173, proxies /api -> backend
npm run build       # TypeScript + Vite production build
```

**Deploy to Azure:**
```bash
azd auth login             # One-time: authenticate to Azure
azd env new                # One-time: initialize environment
azd env set AZURE_LOCATION eastus  # Set region
azd up                     # Full: provision resources + build + deploy
```

## Critical Patterns

### Repository Abstraction
Both `cosmos_repo.py` and `in_memory.py` export identical async functions: `list_devices(skip, limit)`, `get_device(id)`, `create_device(device)`, `update_device(id, device)`, `delete_device(id)`. When adding `backend/` functionality, always update **both** repositories or add a guard for TEST_MODE.

### Cosmos DB Client & Credentials
`backend/src/db/cosmos.py` uses **lazy initialization** — the CosmosClient is created on first use via `get_cosmos_client()`, not on app startup. This is intentional: avoids blocking startup when COSMOS_ENDPOINT isn't set. The client uses `DefaultAzureCredential()`, which works with:
- Azure Container Apps: system-assigned managed identity (RBAC role assigned by `infra/core/data/cosmos-rbac.bicep`)
- Local machine: `azd auth login` credentials via Azure CLI

### Schemas & Validation
`backend/src/schemas.py` uses Pydantic: `DeviceBase` (common fields), `DeviceCreate` (for POST), `DeviceUpdate` (partial, all fields optional), `DeviceResponse` (includes `id` + timestamps). Validation is declarative (Field constraints); see `DeviceCreate` for examples. Timestamp fields are ISO 8601 strings.

### Environment-Driven Behavior
- `TEST_MODE=true`: Skip Cosmos DB, use in-memory storage, seed test data on startup
- `ALLOWED_ORIGINS` (default `*`): CORS origins for frontend
- `COSMOS_ENDPOINT`, `COSMOS_DB_NAME`, `COSMOS_DEVICES_CONTAINER`: Cosmos DB connection (invalid URLs raise ValueError lazily)

## API Contract

Endpoints in `backend/src/main.py`:
- `GET /health`: Simple liveness probe
- `GET /devices?skip=0&limit=100`: List devices (paginated, sorted by created_at DESC)
- `GET /devices/{id}`: Get device or 404
- `POST /devices`: Create device, returns 201 + DeviceResponse
- `PUT /devices/{id}`: Partial update (only `name` and `assigned_to` are patchable)
- `DELETE /devices/{id}`: Delete, returns 204

Frontend (`frontend/src/App.tsx`) calls these endpoints using `fetch()` with `VITE_API_URL` env var (defaults to `/api`). Response format is DeviceResponse (matches backend schema).

## Infrastructure & Deployment

`azure.yaml` lists services: front/backend both containerize via `Dockerfile`, deploy to Container Apps. See `infra/main.bicep` for resource graph:
- **Cosmos DB**: Created by `infra/core/data/cosmos.bicep`, RBAC role assignment in `cosmos-rbac.bicep`
- **Container Registry**: Holds images
- **Container Apps**: Runs frontend (public URL) and backend (private, internal URL for frontend)
- **Hooks**: `infra/hooks/preprovision.sh` runs before provisioning (e.g., validation)

Environment variables injected at deploy time via `infra/main.parameters.json` and `azure.yaml`.

## Common Workflows

### Add a new field to Device
1. Update `backend/src/schemas.py` (add to `DeviceBase` or specific classes)
2. Run `backend/src/repositories/in_memory.py` migration manually (it's a dict, add to fixture)
3. Update `cosmos_repo.py`: new fields auto-merge in `update_device()` but check `create_device()`
4. Update `frontend/src/types.ts` (Device and DeviceCreate interfaces)
5. Update form/list UI in `frontend/src/components/`
6. Test locally: `TEST_MODE=true` then add via form

### Debug Cosmos DB issues locally
Set `TEST_MODE=false` and provide real credentials:
```bash
export COSMOS_ENDPOINT="https://...cosmosdb.azure.com:443/"
export COSMOS_DB_NAME="inventory"
export COSMOS_DEVICES_CONTAINER="devices"
export AZURE_TENANT_ID=...  # From 'azd env list'
export AZURE_SUBSCRIPTION_ID=...
azd auth login
uv run uvicorn src.main:app --reload
```

### Add a new endpoint
1. Add Pydantic schema if needed in `backend/src/schemas.py`
2. Add repository function in both `in_memory.py` and `cosmos_repo.py`
3. Add route in `backend/src/main.py` (uses FastAPI dependency injection)
4. Frontend: add `fetch()` call in `App.tsx` or component
5. Test with `TEST_MODE=true`; then test against real Cosmos DB if available

## Testing & Validation

- **Linting**: Frontend has ESLint (`npm run lint`), backend uses Pylint/Pylance
- **Type checking**: Frontend is strict TypeScript; backend uses Pydantic runtime validation
- **Manual**: Run locally with TEST_MODE, verify CRUD works, check browser console/network tab

## Key Files Reference

- **Backend entry**: `backend/src/main.py` — all routes and CORS setup
- **Repository abstraction**: `backend/src/repositories/__init__.py` — dispatch logic
- **Cosmos client**: `backend/src/db/cosmos.py` — lazy loads, uses managed identity
- **Schemas**: `backend/src/schemas.py` — Pydantic models (single source of truth for fields)
- **Frontend main**: `frontend/src/App.tsx` — state management, API calls
- **Frontend types**: `frontend/src/types.ts` — mirrors backend schemas
- **Deployment config**: `azure.yaml` — service metadata; `infra/main.bicep` — resource definitions

## 🧪 Testing
- **Framework**: Use Playwright with `pytest-playwright` for End-to-End tests.
- **Guidance**: When writing or updating tests, STRICTLY follow the instructions in `.github/instructions/playwright-python.instructions.md`.
