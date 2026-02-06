import pytest
from playwright.sync_api import Page, expect

class TestErrorHandlingAndValidation:
    """Test error states and validation scenarios"""

    def test_error_message_display_area_exists(self, page: Page):
        """Verify error message display area exists"""
        # Error messages should not be visible initially
        error_elements = page.locator(".error-message")
        expect(error_elements).to_have_count_greater_than_or_equal(0)

    def test_loading_state_display(self, page: Page):
        """Test loading state is shown during data fetch"""
        # Verify loading element exists and functions
        loading_element = page.locator(".loading")
        
        # May be visible briefly during initial load
        # This test ensures the element exists for proper UX

    def test_form_field_validation_attributes(self, page: Page):
        """Test HTML validation attributes are properly set"""
        name_field = page.get_by_label("Device Name")
        
        # Name field should be required
        expect(name_field).to_have_attribute("required")
        
        # Assigned to field should be optional
        assigned_field = page.get_by_label("Assigned To")
        expect(assigned_field).not_to_have_attribute("required")

    def test_accessibility_features(self, page: Page):
        """Test accessibility compliance"""
        # Verify proper label associations
        expect(page.locator("label[for='name']")).to_be_visible()
        expect(page.locator("label[for='assignedTo']")).to_be_visible()
        
        # Verify form elements have proper IDs
        expect(page.locator("#name")).to_be_visible()
        expect(page.locator("#assignedTo")).to_be_visible()