# Copilot Instructions for Inventory Management App

This project is an Azure Developer CLI (azd) compatible application with a React frontend, Python FastAPI backend, and Azure Cosmos DB database, deployed to Azure Container Apps.

## Architectural Overview

- **Frontend**: React (Vite, TypeScript) located in `frontend/`. Serves as the UI for managing devices.
- **Backend**: Python FastAPI located in `backend/`. Provides REST API endpoints (`/devices`).
  - Uses `uv` for Python package management.
  - Connects to Azure Cosmos DB for persistence.
- **Database**: Azure Cosmos DB (NoSQL).
- **Infrastructure**: defined in `infra/` using Bicep.
- **Deployment**: Orchestrated via `azd` (`azure.yaml`).

## Developer Workflows

### Prerequisites
- Azure Developer CLI (`azd`)
- Docker
- Node.js & npm
- Python & `uv` (Universal Python/Pip replacement)

### Local Development

**Backend (`backend/`):**
1.  Install dependencies: `uv sync`
2.  Run dev server: `uv run uvicorn src.main:app --reload`
    - Runs on port 8000 by default.

**Frontend (`frontend/`):**
1.  Install dependencies: `npm install`
2.  Run dev server: `npm run dev`
    - Runs on port 5173 by default.
    - Configuration in `vite.config.ts`.
    - `VITE_API_URL` environment variable controls API endpoint (defaults to `/api` or localhost).

### Deployment
- Run `azd up` to provision resources and deploy code to Azure.
- `infra/main.bicep` is the entry point for infrastructure definition.

## Code Conventions & Patterns

### Backend (Python/FastAPI)
- **Structure**:
  - `src/main.py`: App entry point, lifecycle management, and API routes.
  - `src/db/`: Database connection logic (Cosmos DB).
  - `src/repositories/`: Data access layer.
  - `src/schemas.py`: Pydantic models for request/response validation.
- **Database Access**:
  - Use `src.db.cosmos.get_cosmos_client()` for connections.
  - Prefer proper repository patterns in `src/repositories/` over direct DB access in routes.
  - **Important**: The app uses asynchronous Cosmos DB clients (`azure-cosmos`).

### Frontend (React/Vite)
- **Structure**:
  - `src/components/`: Reusable UI components (`DeviceList`, `DeviceForm`).
  - `src/types.ts`: TypeScript interfaces mirroring backend Pydantic schemas.
- **State Management**: Uses React hooks (`useState`, `useEffect`) for local state.
- **API Calls**: Direct `fetch` calls in `App.tsx` (consider refactoring to a service layer if complexity grows).

### Infrastructure (Bicep)
- **Modules**: Reusable modules are in `infra/core/`.
- **Naming**: Resource naming depends on `resourceToken` generated in `main.bicep` to ensure uniqueness.

## Critical Files
- `azure.yaml`: Project definition for `azd`.
- `backend/pyproject.toml`: Python dependencies managed by `uv`.
- `frontend/vite.config.ts`: Vite configuration.
- `infra/main.bicep`: Main infrastructure template.
