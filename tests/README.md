# Device Inventory Management - Test Suite

## Overview

This test suite provides comprehensive end-to-end testing for the Device Inventory Management application using Playwright Python. The tests follow the exploration findings and cover all core user workflows.

## Test Structure

### Core Test Files

- **`test_device_management.py`** - Primary functionality tests covering the 5 key user flows
- **`test_error_handling.py`** - Error states and validation scenarios  
- **`test_responsive_design.py`** - Mobile and responsive design testing
- **`test_api_integration.py`** - Frontend-backend API integration tests

### Configuration

- **`conftest.py`** - Test fixtures and setup configuration
- **`__init__.py`** - Package initialization

## Key User Flows Tested

### 1. Page Load & Initial State
- Application loads with proper UI structure
- Displays seed data from backend
- All essential elements visible and accessible

### 2. Add Device Workflow  
- Form validation for required fields
- Successful device creation with/without assignment
- Form reset after submission

### 3. Edit Device Workflow
- Edit mode activation and form pre-population  
- Successful updates with persistence
- Cancel edit without saving changes

### 4. Delete Device Workflow
- Deletion with confirmation dialog
- Cancel deletion via dialog
- Proper state management

### 5. Form Validation & Error Handling
- Required field validation
- Error message display
- Loading states during API calls

## Running Tests

### Prerequisites

Ensure both backend and frontend servers are running:

```bash
# Terminal 1: Start backend
cd backend
TEST_MODE=true uv run uvicorn src.main:app --reload --port 8000

# Terminal 2: Start frontend  
cd frontend
npm run dev
```

### Install Test Dependencies

```bash
# Install Playwright for Python
pip install pytest-playwright

# Install browsers
playwright install
```

### Execute Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_device_management.py

# Run with headed browser (useful for debugging)
pytest tests/ --headed

# Run with specific browser
pytest tests/ --browser=firefox

# Generate test report
pytest tests/ --html=report.html
```

## Test Locator Strategy

Following Playwright best practices, tests prioritize:

1. **Role-based locators**: `page.get_by_role("button", name="Add Device")`
2. **Label-based locators**: `page.get_by_label("Device Name")`
3. **Text-based locators**: `page.get_by_text("Device Management")`
4. **CSS selectors**: Only when necessary (`.device-list`, `.device-item`)

## Test Data Management

- Tests use the application's seed data from `backend/src/repositories/in_memory.py`
- Each test is isolated and doesn't affect others
- No external test data files required

## Debugging Failed Tests

- Use `--headed` flag to watch tests execute in browser
- Add `page.pause()` in test code for manual debugging
- Check browser console for JavaScript errors
- Review network tab for API call failures

## Continuous Integration

Tests are designed for CI environments:
- Headless execution by default
- No external dependencies beyond running servers
- Comprehensive coverage of critical user paths
- Fast execution with reliable selectors

## Coverage Areas

✅ **Functional Testing**: All CRUD operations  
✅ **UI Testing**: Form interactions and state management  
✅ **Integration Testing**: Frontend-backend API communication  
✅ **Responsive Testing**: Mobile and desktop layouts  
✅ **Accessibility Testing**: Labels and form validation  
✅ **Error Handling**: Validation and edge cases