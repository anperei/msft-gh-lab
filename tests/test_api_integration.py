import pytest
from playwright.sync_api import Page, expect

class TestApiIntegration:
    """Test frontend-backend API integration"""

    def test_api_connectivity_on_page_load(self, page: Page):
        """Test that frontend successfully connects to backend API"""
        # Navigate to page (triggers API call to load devices)
        page.goto("http://localhost:3000")
        
        # Wait for devices to load (indicates API connectivity)
        expect(page.locator(".device-list")).to_be_visible()
        
        # Verify seed data loaded from API
        expect(page.locator(".device-item")).to_have_count_greater_than(0)

    def test_create_device_api_integration(self, page: Page):
        """Test device creation API integration"""
        # Create device through UI
        page.get_by_label("Device Name").fill("API Integration Test")
        page.get_by_label("Assigned To").fill("API Tester")
        
        page.get_by_role("button", name="Add Device").click()
        
        # Verify device appears (confirms API call succeeded)
        expect(page.get_by_text("API Integration Test")).to_be_visible()
        expect(page.get_by_text("Assigned to: API Tester")).to_be_visible()

    def test_update_device_api_integration(self, page: Page):
        """Test device update API integration"""
        # Edit existing device
        page.locator(".device-item").first.get_by_role("button", name="Edit").click()
        
        # Update fields
        page.get_by_label("Device Name").fill("Updated via API")
        page.get_by_label("Assigned To").fill("Updated User")
        
        page.get_by_role("button", name="Update Device").click()
        
        # Verify changes persisted (confirms API call succeeded)
        expect(page.get_by_text("Updated via API")).to_be_visible()
        expect(page.get_by_text("Assigned to: Updated User")).to_be_visible()

    def test_delete_device_api_integration(self, page: Page):
        """Test device deletion API integration"""
        initial_count = page.locator(".device-item").count()
        
        # Set up dialog handler
        page.on("dialog", lambda dialog: dialog.accept())
        
        # Delete device
        page.locator(".device-item").first.get_by_role("button", name="Delete").click()
        
        # Verify deletion persisted (confirms API call succeeded)
        expect(page.locator(".device-item")).to_have_count(initial_count - 1)

    def test_full_crud_cycle_integration(self, page: Page):
        """Test complete CRUD cycle through API"""
        # CREATE
        page.get_by_label("Device Name").fill("CRUD Test Device")
        page.get_by_role("button", name="Add Device").click()
        expect(page.get_by_text("CRUD Test Device")).to_be_visible()
        
        # UPDATE  
        crud_device = page.locator(".device-item:has-text('CRUD Test Device')")
        crud_device.get_by_role("button", name="Edit").click()
        page.get_by_label("Device Name").fill("Updated CRUD Device")
        page.get_by_role("button", name="Update Device").click()
        expect(page.get_by_text("Updated CRUD Device")).to_be_visible()
        
        # DELETE
        page.on("dialog", lambda dialog: dialog.accept())
        crud_device = page.locator(".device-item:has-text('Updated CRUD Device')")
        crud_device.get_by_role("button", name="Delete").click()
        expect(page.get_by_text("Updated CRUD Device")).not_to_be_visible()