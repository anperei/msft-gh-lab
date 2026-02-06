"""
Global test configuration and fixtures for Playwright tests.

This module provides shared fixtures and configuration for all test files.
"""

import pytest
from playwright.sync_api import Page, expect


@pytest.fixture(scope="session")
def app_url():
    """Base URL for the application"""
    return "http://localhost:3000"


@pytest.fixture(scope="function", autouse=True)
def setup_page(page: Page, app_url: str):
    """
    Navigate to the application before each test.
    
    This fixture runs automatically for all tests and provides:
    - Navigation to the application
    - Basic availability check
    """
    page.goto(app_url)
    
    # Verify app is loaded
    expect(page.get_by_role("heading", name="Device Management")).to_be_visible(timeout=5000)