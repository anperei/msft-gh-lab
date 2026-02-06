import pytest
from playwright.sync_api import Page, expect

class TestResponsiveDesign:
    """Test responsive design and mobile compatibility"""

    def test_mobile_viewport_layout(self, page: Page):
        """Test application layout on mobile viewport"""
        # Set mobile viewport size
        page.set_viewport_size({"width": 375, "height": 667})
        
        # Verify essential elements remain visible and functional
        expect(page.get_by_role("heading", name="Device Management")).to_be_visible()
        expect(page.get_by_label("Device Name")).to_be_visible()
        expect(page.get_by_role("button", name="Add Device")).to_be_visible()
        
        # Verify form is still usable
        page.get_by_label("Device Name").fill("Mobile Test Device")
        page.get_by_role("button", name="Add Device").click()
        
        expect(page.get_by_text("Mobile Test Device")).to_be_visible()

    def test_tablet_viewport_layout(self, page: Page):
        """Test application layout on tablet viewport"""
        # Set tablet viewport size
        page.set_viewport_size({"width": 768, "height": 1024})
        
        # Verify layout adapts properly
        expect(page.get_by_role("heading", name="Device Management")).to_be_visible()
        expect(page.locator(".device-list")).to_be_visible()

    def test_desktop_viewport_layout(self, page: Page):
        """Test application layout on desktop viewport"""
        # Set larger desktop viewport
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Verify all elements properly scaled
        expect(page.get_by_role("heading", name="Device Management")).to_be_visible()
        expect(page.locator(".form-section")).to_be_visible()
        expect(page.locator(".list-section")).to_be_visible()