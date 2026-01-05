# Inventory Management App

A simple inventory management application built with React and FastAPI, deployed to Azure Container Apps.

## Features

- Add new devices to inventory
- Edit device information (name, assigned to)
- View all devices
- Delete devices

## Tech Stack

- **Frontend**: React + Vite + TypeScript
- **Backend**: Python FastAPI with uv
- **Database**: Azure Database for PostgreSQL
- **Hosting**: Azure Container Apps

## Prerequisites

- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- [Docker](https://www.docker.com/get-started)
- Azure subscription

## Local Development

### Backend
```bash
cd backend
uv sync
uv run uvicorn src.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Deploy to Azure

```bash
azd up
```

This single command will:
1. Provision all Azure resources (Container Apps, PostgreSQL, Container Registry)
2. Create a User-Assigned Managed Identity for the backend
3. Grant the identity AcrPull on the Container Registry before app creation
4. Build and push Docker images
5. Deploy frontend and backend using the identity (backend runs with minReplicas=1)
6. Run post-provision to initialize the database and create an AAD-backed DB role for the backend identity

### Requirements for `azd up`

- Be logged in to Azure: 
  
  ```bash
  azd auth login
  ```

- Provide a Microsoft Entra (AAD) principal to configure as the PostgreSQL AAD admin. You can use your signed-in user or a service principal. Capture its object id and set it before provisioning so AAD auth works and the post-provision script can create the DB role:

  ```bash
  # Get object id of the signed-in user
  az ad signed-in-user show --query id -o tsv

  # Set it for this azd environment (replace <OBJECT_ID>)
  azd env set principalId <OBJECT_ID>
  ```

  Alternatively, add it to `infra/main.parameters.json` as a parameter if you prefer file-based configuration.

## Environment Variables

The deployment sets and uses the following:
- `BACKEND_URL`: Backend API endpoint for the frontend
- `DB_HOST`: PostgreSQL server FQDN
- `DB_NAME`: Database name (default: `inventory`)
- `BACKEND_IDENTITY_NAME`: Name of the user-assigned identity used by the backend (also the DB role created)
- Backend container settings:
  - `USE_MANAGED_IDENTITY=true`: Enable AAD token-based auth for PostgreSQL
  - `DB_USER`: Set to `BACKEND_IDENTITY_NAME` and used with AAD access tokens

## Architecture

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Frontend   │─────>│   Backend    │─────>│  PostgreSQL  │
│ (React App)  │      │  (FastAPI)   │      │   Database   │
└──────────────┘      └──────────────┘      └──────────────┘
  Container App         Container App        Flexible Server
```
