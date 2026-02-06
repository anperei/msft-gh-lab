import re
import pytest
from playwright.sync_api import Page, expect

class TestDeviceManagementCore:
    """Core functionality tests for Device Inventory Management application
    
    Explores 5 key user flows:
    1. Page load and initial state
    2. Add new device workflow  
    3. Edit existing device workflow
    4. Delete device workflow
    5. Form validation and error handling
    """

    def test_page_loads_with_correct_structure(self, page: Page):
        """USER FLOW 1: Verify application loads with proper UI structure"""
        # Navigate and verify title
        expect(page).to_have_title(re.compile("Inventory Management"))
        
        # Verify main heading
        expect(page.get_by_role("heading", name="Device Management")).to_be_visible()
        
        # Verify form section
        expect(page.get_by_role("heading", name="Add New Device")).to_be_visible()
        
        # Verify device list section
        expect(page.get_by_role("heading", name="Devices")).to_be_visible()
        
        # Verify key form elements are present
        expect(page.get_by_label("Device Name")).to_be_visible()
        expect(page.get_by_label("Assigned To")).to_be_visible()
        expect(page.get_by_role("button", name="Add Device")).to_be_visible()

    def test_displays_seed_devices(self, page: Page):
        """Verify seed data from backend is displayed correctly"""
        device_list = page.locator(".device-list")
        expect(device_list).to_be_visible()
        
        # Check for specific seed devices from in_memory.py
        expect(device_list).to_contain_text("Laptop-001")
        expect(device_list).to_contain_text("Alice Johnson")
        expect(device_list).to_contain_text("Monitor-01")
        
        # Verify device cards have required action buttons
        expect(page.get_by_role("button", name="Edit")).to_have_count_greater_than(0)
        expect(page.get_by_role("button", name="Delete")).to_have_count_greater_than(0)

    def test_add_device_successful_workflow(self, page: Page):
        """USER FLOW 2: Test complete add device workflow"""
        initial_device_count = page.locator(".device-item").count()
        
        # Fill device form
        page.get_by_label("Device Name").fill("Test Laptop E2E")
        page.get_by_label("Assigned To").fill("QA Tester")
        
        # Submit form
        page.get_by_role("button", name="Add Device").click()
        
        # Verify device appears in list
        expect(page.get_by_text("Test Laptop E2E")).to_be_visible()
        expect(page.get_by_text("Assigned to: QA Tester")).to_be_visible()
        
        # Verify device count increased
        expect(page.locator(".device-item")).to_have_count(initial_device_count + 1)
        
        # Verify form fields reset after successful submission
        expect(page.get_by_label("Device Name")).to_have_value("")
        expect(page.get_by_label("Assigned To")).to_have_value("")

    def test_add_device_with_optional_assignment(self, page: Page):
        """Test adding device without assignment (optional field)"""
        page.get_by_label("Device Name").fill("Unassigned Device")
        # Leave "Assigned To" empty
        
        page.get_by_role("button", name="Add Device").click()
        
        expect(page.get_by_text("Unassigned Device")).to_be_visible()
        expect(page.get_by_text("Not assigned")).to_be_visible()

    def test_edit_device_complete_workflow(self, page: Page):
        """USER FLOW 3: Test complete edit device workflow"""
        # Click edit on first device
        first_device = page.locator(".device-item").first
        original_name = first_device.locator("h3").text_content()
        
        first_device.get_by_role("button", name="Edit").click()
        
        # Verify edit mode activated
        expect(page.get_by_role("heading", name="Edit Device")).to_be_visible()
        expect(page.get_by_role("button", name="Update Device")).to_be_visible()
        expect(page.get_by_role("button", name="Cancel")).to_be_visible()
        
        # Verify form pre-populated with existing data
        name_field = page.get_by_label("Device Name")
        expect(name_field).not_to_have_value("")
        
        # Make changes
        updated_name = f"Updated {original_name}"
        name_field.fill(updated_name)
        page.get_by_label("Assigned To").fill("Updated User")
        
        # Save changes
        page.get_by_role("button", name="Update Device").click()
        
        # Verify changes saved and visible
        expect(page.get_by_text(updated_name)).to_be_visible()
        expect(page.get_by_text("Assigned to: Updated User")).to_be_visible()
        
        # Verify returned to add mode
        expect(page.get_by_role("heading", name="Add New Device")).to_be_visible()

    def test_cancel_edit_workflow(self, page: Page):
        """Test canceling edit operation without saving changes"""
        initial_device_count = page.locator(".device-item").count()
        
        # Start editing first device
        first_device = page.locator(".device-item").first
        original_name = first_device.locator("h3").text_content()
        
        first_device.get_by_role("button", name="Edit").click()
        
        # Make changes but don't save
        page.get_by_label("Device Name").fill("Should Not Save")
        
        # Cancel edit
        page.get_by_role("button", name="Cancel").click()
        
        # Verify returned to add mode
        expect(page.get_by_role("heading", name="Add New Device")).to_be_visible()
        
        # Verify changes were not saved
        expect(page.get_by_text("Should Not Save")).not_to_be_visible()
        expect(page.get_by_text(original_name)).to_be_visible()
        expect(page.locator(".device-item")).to_have_count(initial_device_count)

    def test_delete_device_with_confirmation(self, page: Page):
        """USER FLOW 4: Test delete device workflow with confirmation"""
        initial_device_count = page.locator(".device-item").count()
        
        # Get name of device to delete
        first_device = page.locator(".device-item").first
        device_name = first_device.locator("h3").text_content()
        
        # Set up dialog handler to accept deletion
        page.on("dialog", lambda dialog: dialog.accept())
        
        # Delete device
        first_device.get_by_role("button", name="Delete").click()
        
        # Verify device removed
        expect(page.locator(".device-item")).to_have_count(initial_device_count - 1)
        expect(page.get_by_text(device_name)).not_to_be_visible()

    def test_delete_device_cancel_confirmation(self, page: Page):
        """Test canceling device deletion"""
        initial_device_count = page.locator(".device-item").count()
        
        # Set up dialog handler to cancel deletion
        page.on("dialog", lambda dialog: dialog.dismiss())
        
        # Try to delete
        page.locator(".device-item").first.get_by_role("button", name="Delete").click()
        
        # Verify no devices were removed
        expect(page.locator(".device-item")).to_have_count(initial_device_count)

    def test_form_validation_required_fields(self, page: Page):
        """USER FLOW 5: Test form validation for required fields"""
        # Try to submit empty form
        page.get_by_role("button", name="Add Device").click()
        
        # Required field validation should prevent submission
        name_field = page.get_by_label("Device Name")
        expect(name_field).to_have_attribute("required")
        
        # Verify still on add form (not submitted)
        expect(page.get_by_role("heading", name="Add New Device")).to_be_visible()

    def test_device_display_states(self, page: Page):
        """Test different device assignment display states"""
        device_list = page.locator(".device-list")
        
        # Should display assigned devices correctly  
        expect(device_list).to_contain_text("Assigned to:")
        
        # Should display unassigned devices
        expect(device_list).to_contain_text("Not assigned")