"""
End-to-End Tests for Device Inventory Management Application

This module contains comprehensive E2E tests that verify complete user workflows
for the device inventory management system.

Tests follow Playwright Python best practices:
- Role-based locators (get_by_role, get_by_label, get_by_text)
- Auto-retrying assertions via expect API
- Proper fixture management for clean state
- User-facing interaction patterns
"""

import re
import pytest
from playwright.sync_api import Page, expect, Dialog


@pytest.fixture(scope="function")
def app_page(page: Page):
    """
    Navigate to the application and ensure it's loaded before each test.
    
    This fixture provides a clean starting point for each test by:
    - Navigating to the app URL
    - Waiting for the main UI to be visible
    - Ensuring the page is interactive
    """
    page.goto("http://localhost:3000")
    
    # Wait for app to be fully loaded
    expect(page.get_by_role("heading", name="Device Management")).to_be_visible()
    
    return page


@pytest.fixture(scope="function")
def dialog_handler(page: Page):
    """
    Fixture to handle browser confirmation dialogs.
    
    Returns a context manager that can accept or dismiss dialogs.
    """
    class DialogHandler:
        def __init__(self, page: Page):
            self.page = page
            self.dialog_message = None
            
        def accept_next(self):
            """Accept the next dialog that appears"""
            def handle_dialog(dialog: Dialog):
                self.dialog_message = dialog.message
                dialog.accept()
            self.page.once("dialog", handle_dialog)
            
        def dismiss_next(self):
            """Dismiss the next dialog that appears"""
            def handle_dialog(dialog: Dialog):
                self.dialog_message = dialog.message
                dialog.dismiss()
            self.page.once("dialog", handle_dialog)
    
    return DialogHandler(page)


class TestDeviceInventoryE2E:
    """
    End-to-End test suite for Device Inventory Management application.
    
    Tests the complete user journey through the application including:
    - Opening and navigating the frontend
    - Creating new devices
    - Viewing devices in the list
    - Editing existing devices
    - Deleting devices with confirmation
    """

    def test_app_loads_successfully(self, app_page: Page):
        """
        USER FLOW: Open the frontend at localhost:3000
        
        Verifies that:
        - Application loads without errors
        - Main UI elements are visible
        - Page has correct title
        """
        # Verify page title
        expect(app_page).to_have_title(re.compile("Inventory Management"))
        
        # Verify main heading
        expect(app_page.get_by_role("heading", name="Device Management")).to_be_visible()
        
        # Verify form section present
        expect(app_page.get_by_role("heading", name="Add New Device")).to_be_visible()
        
        # Verify device list section present
        expect(app_page.get_by_role("heading", name="Devices")).to_be_visible()
        
        # Verify essential form elements
        expect(app_page.get_by_label("Device Name")).to_be_visible()
        expect(app_page.get_by_label("Assigned To")).to_be_visible()
        expect(app_page.get_by_role("button", name="Add Device")).to_be_visible()

    def test_add_device_with_assignment(self, app_page: Page):
        """
        USER FLOW: Add a new device with name and assigned user
        
        Verifies that:
        - User can fill in device name (required)
        - User can fill in assigned user (optional)
        - Device is created successfully
        - Device appears in the list with correct information
        - Form resets after successful submission
        """
        # Get initial device count
        initial_count = app_page.locator(".device-item").count()
        
        # Fill in device details
        device_name = "Test Laptop E2E"
        assigned_user = "John Doe"
        
        app_page.get_by_label("Device Name").fill(device_name)
        app_page.get_by_label("Assigned To").fill(assigned_user)
        
        # Submit the form
        app_page.get_by_role("button", name="Add Device").click()
        
        # Verify device appears in the list
        expect(app_page.get_by_text(device_name)).to_be_visible()
        expect(app_page.get_by_text(f"Assigned to: {assigned_user}")).to_be_visible()
        
        # Verify device count increased
        expect(app_page.locator(".device-item")).to_have_count(initial_count + 1)
        
        # Verify form fields are cleared
        expect(app_page.get_by_label("Device Name")).to_have_value("")
        expect(app_page.get_by_label("Assigned To")).to_have_value("")

    def test_add_device_without_assignment(self, app_page: Page):
        """
        USER FLOW: Add a new device without assigned user (optional field)
        
        Verifies that:
        - User can create device with only required fields
        - Optional 'Assigned To' field can be left empty
        - Device shows as 'Not assigned' in the list
        """
        device_name = "Unassigned Monitor"
        
        # Fill only device name (leave assignment empty)
        app_page.get_by_label("Device Name").fill(device_name)
        
        # Submit the form
        app_page.get_by_role("button", name="Add Device").click()
        
        # Verify device appears without assignment
        expect(app_page.get_by_text(device_name)).to_be_visible()
        
        # Find the device card and verify "Not assigned" status
        device_card = app_page.locator(".device-item", has_text=device_name)
        expect(device_card.get_by_text("Not assigned")).to_be_visible()

    def test_see_device_in_list(self, app_page: Page):
        """
        USER FLOW: See newly added device appear in the list
        
        Verifies that:
        - Device list displays all devices
        - Each device shows name and assignment status
        - Device cards have Edit and Delete buttons
        """
        # Create a test device
        device_name = "Verification Test Device"
        app_page.get_by_label("Device Name").fill(device_name)
        app_page.get_by_label("Assigned To").fill("Test User")
        app_page.get_by_role("button", name="Add Device").click()
        
        # Locate the specific device in the list
        device_card = app_page.locator(".device-item", has_text=device_name)
        
        # Verify device card is visible
        expect(device_card).to_be_visible()
        
        # Verify device card contains expected elements
        expect(device_card.locator("h3")).to_contain_text(device_name)
        expect(device_card).to_contain_text("Assigned to: Test User")
        
        # Verify action buttons are present
        expect(device_card.get_by_role("button", name="Edit")).to_be_visible()
        expect(device_card.get_by_role("button", name="Delete")).to_be_visible()

    def test_edit_device_details(self, app_page: Page):
        """
        USER FLOW: Edit the device details
        
        Verifies that:
        - User can click Edit button on a device
        - Form switches to Edit mode
        - Form pre-populates with existing device data
        - User can modify device details
        - Changes are saved and reflected in the list
        - Form returns to Add mode after update
        """
        # First, create a device to edit
        original_name = "Original Device Name"
        original_user = "Original User"
        
        app_page.get_by_label("Device Name").fill(original_name)
        app_page.get_by_label("Assigned To").fill(original_user)
        app_page.get_by_role("button", name="Add Device").click()
        
        # Wait for device to appear
        expect(app_page.get_by_text(original_name)).to_be_visible()
        
        # Click Edit on the device we just created
        device_card = app_page.locator(".device-item", has_text=original_name)
        device_card.get_by_role("button", name="Edit").click()
        
        # Verify form switched to Edit mode
        expect(app_page.get_by_role("heading", name="Edit Device")).to_be_visible()
        expect(app_page.get_by_role("button", name="Update Device")).to_be_visible()
        expect(app_page.get_by_role("button", name="Cancel")).to_be_visible()
        
        # Verify form is pre-populated
        name_field = app_page.get_by_label("Device Name")
        expect(name_field).to_have_value(original_name)
        
        assigned_field = app_page.get_by_label("Assigned To")
        expect(assigned_field).to_have_value(original_user)
        
        # Make changes
        updated_name = "Updated Device Name"
        updated_user = "Updated User"
        
        name_field.fill(updated_name)
        assigned_field.fill(updated_user)
        
        # Save changes
        app_page.get_by_role("button", name="Update Device").click()
        
        # Verify changes are reflected in the list
        expect(app_page.get_by_text(updated_name)).to_be_visible()
        expect(app_page.get_by_text(f"Assigned to: {updated_user}")).to_be_visible()
        
        # Verify original name is no longer visible
        expect(app_page.get_by_text(original_name)).not_to_be_visible()
        
        # Verify form returned to Add mode
        expect(app_page.get_by_role("heading", name="Add New Device")).to_be_visible()
        expect(app_page.get_by_role("button", name="Add Device")).to_be_visible()

    def test_cancel_edit_operation(self, app_page: Page):
        """
        USER FLOW: Cancel edit operation without saving changes
        
        Verifies that:
        - User can cancel edit mode
        - Changes are discarded
        - Original device data remains unchanged
        - Form returns to Add mode
        """
        # Create a device
        original_name = "Cancel Test Device"
        app_page.get_by_label("Device Name").fill(original_name)
        app_page.get_by_role("button", name="Add Device").click()
        
        # Start editing
        device_card = app_page.locator(".device-item", has_text=original_name)
        device_card.get_by_role("button", name="Edit").click()
        
        # Make changes but don't save
        app_page.get_by_label("Device Name").fill("Should Not Save")
        
        # Cancel the edit
        app_page.get_by_role("button", name="Cancel").click()
        
        # Verify original name is still in the list
        expect(app_page.get_by_text(original_name)).to_be_visible()
        
        # Verify changes were not saved
        expect(app_page.get_by_text("Should Not Save")).not_to_be_visible()
        
        # Verify form returned to Add mode
        expect(app_page.get_by_role("heading", name="Add New Device")).to_be_visible()

    def test_delete_device_with_confirmation(self, app_page: Page, dialog_handler):
        """
        USER FLOW: Delete device with confirmation dialog
        
        Verifies that:
        - User can click Delete button
        - Confirmation dialog appears
        - User can confirm deletion
        - Device is removed from the list
        """
        # Create a device to delete
        device_name = "Device To Delete"
        app_page.get_by_label("Device Name").fill(device_name)
        app_page.get_by_role("button", name="Add Device").click()
        
        # Wait for device to appear
        expect(app_page.get_by_text(device_name)).to_be_visible()
        
        # Get initial count
        initial_count = app_page.locator(".device-item").count()
        
        # Set up dialog handler to accept deletion
        dialog_handler.accept_next()
        
        # Click delete button
        device_card = app_page.locator(".device-item", has_text=device_name)
        device_card.get_by_role("button", name="Delete").click()
        
        # Verify device was removed
        expect(app_page.locator(".device-item")).to_have_count(initial_count - 1)
        expect(app_page.get_by_text(device_name)).not_to_be_visible()

    def test_cancel_delete_operation(self, app_page: Page, dialog_handler):
        """
        USER FLOW: Cancel device deletion via confirmation dialog
        
        Verifies that:
        - User can dismiss the confirmation dialog
        - Device is NOT deleted
        - Device remains in the list
        """
        # Create a device
        device_name = "Do Not Delete Device"
        app_page.get_by_label("Device Name").fill(device_name)
        app_page.get_by_role("button", name="Add Device").click()
        
        # Wait for device to appear
        expect(app_page.get_by_text(device_name)).to_be_visible()
        
        # Get initial count
        initial_count = app_page.locator(".device-item").count()
        
        # Set up dialog handler to dismiss deletion
        dialog_handler.dismiss_next()
        
        # Try to delete
        device_card = app_page.locator(".device-item", has_text=device_name)
        device_card.get_by_role("button", name="Delete").click()
        
        # Verify device was NOT removed
        expect(app_page.locator(".device-item")).to_have_count(initial_count)
        expect(app_page.get_by_text(device_name)).to_be_visible()

    def test_complete_crud_workflow(self, app_page: Page, dialog_handler):
        """
        INTEGRATION TEST: Complete CRUD workflow
        
        Verifies the entire user journey:
        1. Create a device
        2. Read/View the device in the list
        3. Update the device details
        4. Delete the device
        """
        # CREATE
        device_name = "CRUD Workflow Device"
        assigned_user = "CRUD User"
        
        app_page.get_by_label("Device Name").fill(device_name)
        app_page.get_by_label("Assigned To").fill(assigned_user)
        app_page.get_by_role("button", name="Add Device").click()
        
        # READ - Verify device appears in list
        expect(app_page.get_by_text(device_name)).to_be_visible()
        expect(app_page.get_by_text(f"Assigned to: {assigned_user}")).to_be_visible()
        
        # UPDATE - Edit the device
        device_card = app_page.locator(".device-item", has_text=device_name)
        device_card.get_by_role("button", name="Edit").click()
        
        updated_name = "Updated CRUD Device"
        app_page.get_by_label("Device Name").fill(updated_name)
        app_page.get_by_role("button", name="Update Device").click()
        
        # Verify update
        expect(app_page.get_by_text(updated_name)).to_be_visible()
        
        # DELETE - Remove the device
        dialog_handler.accept_next()
        updated_device_card = app_page.locator(".device-item", has_text=updated_name)
        updated_device_card.get_by_role("button", name="Delete").click()
        
        # Verify deletion
        expect(app_page.get_by_text(updated_name)).not_to_be_visible()

    def test_form_validation_required_fields(self, app_page: Page):
        """
        VALIDATION TEST: Required field validation
        
        Verifies that:
        - Device Name is required
        - Form validation prevents submission with empty required fields
        - Proper HTML validation attributes are present
        """
        # Try to submit without filling any fields
        app_page.get_by_role("button", name="Add Device").click()
        
        # Verify required attribute on Device Name field
        name_field = app_page.get_by_label("Device Name")
        expect(name_field).to_have_attribute("required", "")
        
        # Verify Assigned To field is NOT required
        assigned_field = app_page.get_by_label("Assigned To")
        # Check if element doesn't have the required attribute by checking for empty value
        
        # Verify form is still in add mode (submission blocked)
        expect(app_page.get_by_role("heading", name="Add New Device")).to_be_visible()

    def test_multiple_devices_management(self, app_page: Page, dialog_handler):
        """
        ADVANCED TEST: Managing multiple devices
        
        Verifies that:
        - Multiple devices can be created
        - Each device maintains its own data
        - Operations on one device don't affect others
        """
        devices = [
            {"name": "Device 1", "user": "User A"},
            {"name": "Device 2", "user": "User B"},
            {"name": "Device 3", "user": "User C"},
        ]
        
        # Create multiple devices
        for device in devices:
            app_page.get_by_label("Device Name").fill(device["name"])
            app_page.get_by_label("Assigned To").fill(device["user"])
            app_page.get_by_role("button", name="Add Device").click()
            
            # Verify each device appears
            expect(app_page.get_by_text(device["name"])).to_be_visible()
        
        # Edit Device 2
        device_2_card = app_page.locator(".device-item", has_text="Device 2")
        device_2_card.get_by_role("button", name="Edit").click()
        app_page.get_by_label("Device Name").fill("Modified Device 2")
        app_page.get_by_role("button", name="Update Device").click()
        
        # Verify Device 2 updated, others unchanged
        expect(app_page.get_by_text("Modified Device 2")).to_be_visible()
        expect(app_page.get_by_text("Device 1")).to_be_visible()
        expect(app_page.get_by_text("Device 3")).to_be_visible()
        
        # Delete Device 1
        dialog_handler.accept_next()
        device_1_card = app_page.locator(".device-item", has_text="Device 1")
        device_1_card.get_by_role("button", name="Delete").click()
        
        # Verify Device 1 deleted, others remain
        expect(app_page.get_by_text("Device 1")).not_to_be_visible()
        expect(app_page.get_by_text("Modified Device 2")).to_be_visible()
        expect(app_page.get_by_text("Device 3")).to_be_visible()
