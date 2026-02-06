# Plan: In-Memory Test Mode Repository

## Objective
Add an in-memory repository implementation to FastAPI backend for local development and testing without requiring Azure Cosmos DB connection.

## Implementation Steps

### 1. Create In-Memory Repository Module
**File**: `backend/src/repositories/in_memory.py`

- Implement async functions mirroring Cosmos interface:
  - `get_devices(skip: int, limit: int)` → list of Device models
  - `get_device_by_id(device_id: str)` → Device or None
  - `create_device(name: str, assigned_to: str | None)` → Device
  - `update_device(device_id: str, **kwargs)` → Device or None
  - `delete_device(device_id: str)` → bool
- Use `asyncio.Lock` for thread-safe dictionary access
- Generate UUIDs and timestamps (`datetime.now(datetime.UTC)`) for test data
- Store devices in module-level dict: `_devices: dict[str, dict]`

### 2. Update Repository Router
**File**: `backend/src/repositories/__init__.py`

- Read `TEST_MODE` environment variable (default: `"false"`)
- Conditionally import: `from .in_memory import *` if `TEST_MODE == "true"`, else `from .cosmos import *`
- Expose all repository functions at module level

### 3. Skip Cosmos Initialization in Test Mode
**File**: `backend/src/db/cosmos.py`

- Check `TEST_MODE` in `get_database()` and `get_container()` functions
- Return `None` or mock objects when `TEST_MODE == "true"`
- Prevent connection errors by short-circuiting client initialization

### 4. Seed Test Data on Startup
**File**: `backend/src/main.py`

- In lifespan context manager (startup phase):
  - If `TEST_MODE == "true"`, call a seeding function
  - Populate 3-5 sample devices with realistic data (e.g., "Laptop-001", "Monitor-02")
  - Log seeding completion

### 5. Document Environment Variable
**File**: `backend/Dockerfile` & `PREREQUISITES.md`

- Add `TEST_MODE` to Dockerfile comments or ENV documentation
- Update PREREQUISITES.md with local dev instructions:
  ```bash
  TEST_MODE=true uvicorn src.main:app --reload
  ```

## Key Design Decisions

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| State Persistence | In-memory data lost on restart | Acceptable for dev/test; enables fresh state between runs |
| Thread Safety | Use `asyncio.Lock` | Supports concurrent requests in single-threaded Uvicorn |
| Env Var Default | `TEST_MODE=false` | Production-safe; explicit opt-in for test mode |
| Auto-Fallback | No auto-activate when `COSMOS_ENDPOINT` missing | Explicit control; prevents silent fallback masking real issues |

## Files Modified
1. `backend/src/repositories/in_memory.py` ← **NEW**
2. `backend/src/repositories/__init__.py`
3. `backend/src/db/cosmos.py`
4. `backend/src/main.py`
5. `backend/Dockerfile` (comments/docs only)
6. `PREREQUISITES.md`

## Verification Steps
- [ ] Run `TEST_MODE=true python -m uvicorn backend.src.main:app --reload` 
- [ ] Verify GET `/devices` returns seeded test data
- [ ] Verify POST `/devices`, PUT, DELETE operations work in-memory
- [ ] Verify app starts without errors when `TEST_MODE=false` (Cosmos mode)
