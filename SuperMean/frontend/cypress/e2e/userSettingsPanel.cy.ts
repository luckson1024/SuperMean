describe('UserSettingsPanel', () => {
  // Setup for all tests - visit dashboard and open settings panel
  beforeEach(() => {
    cy.visit('/dashboard');
    cy.get('[data-testid="open-settings-button"]').click(); // Button that opens the panel
    cy.get('[role="dialog"]').as('settingsPanel'); // The panel is a dialog
  });
  
  // Intercept API calls for settings
  beforeEach(() => {
    // Mock the settings API response
    cy.intercept('GET', '/api/settings', {
      statusCode: 200,
      body: {
        theme: 'light',
        notifications_enabled: true,
        session_timeout_minutes: 60,
        auto_save: true,
        agent_view_mode: 'card',
        language: 'en'
      }
    }).as('getSettings');
    
    // Mock the settings update API
    cy.intercept('PUT', '/api/settings', {
      statusCode: 200
    }).as('saveSettings');
    
    // Mock the logout API
    cy.intercept('POST', '/api/logout', {
      statusCode: 200
    }).as('logout');
  });
  

  // Mocking the component directly for isolated testing might be more robust
  // if the panel is not tightly coupled to a specific page structure.
  // Example using Cypress component testing (requires setup):
  // import { mount } from '@cypress/react';
  // import UserSettingsPanel from '../../components/UserSettingsPanel';
  // beforeEach(() => {
  //   mount(<UserSettingsPanel isOpen={true} onClose={cy.stub().as('onCloseStub')} />);
  //   cy.get('[role="dialog"]').as('settingsPanel');
  // });


  it('should interact with theme selection', () => {
    // Wait for the panel to be fully loaded
    cy.wait('@getSettings');
    
    // Find the theme dropdown and select dark theme
    cy.get('@settingsPanel')
      .find('label')
      .contains('Theme')
      .parent()
      .find('select')
      .select('dark');
    
    // Verify the theme change is reflected in the UI
    // When Save Settings is clicked, the dark class should be applied to html
    cy.get('@settingsPanel')
      .find('button')
      .contains('Save Settings')
      .click();
    
    cy.wait('@saveSettings');
    cy.get('html').should('have.class', 'dark');
  });

  it('should interact with notifications toggle', () => {
    cy.wait('@getSettings');
    
    // Find the notifications checkbox and click it to toggle off
    cy.get('@settingsPanel')
      .find('label')
      .contains('Notifications')
      .parent()
      .find('input[type="checkbox"]')
      .click();
    
    // Verify the checkbox is now unchecked
    cy.get('@settingsPanel')
      .find('label')
      .contains('Notifications')
      .parent()
      .find('input[type="checkbox"]')
      .should('not.be.checked');
  });

  it('should interact with session timeout input and show validation errors', () => {
    cy.wait('@getSettings');
    
    // Test invalid value - too low
    cy.get('@settingsPanel')
      .find('label')
      .contains('Session Timeout')
      .parent()
      .find('input[type="number"]')
      .clear()
      .type('0');
    
    // Try to save to trigger validation
    cy.get('@settingsPanel')
      .find('button')
      .contains('Save Settings')
      .click();
    
    // Verify validation error message appears
    cy.get('@settingsPanel').should('contain', 'Session timeout must be greater than 0');
    
    // Test invalid value - too high
    cy.get('@settingsPanel')
      .find('label')
      .contains('Session Timeout')
      .parent()
      .find('input[type="number"]')
      .clear()
      .type('1500');
    
    // Verify validation error message appears
    cy.get('@settingsPanel').should('contain', 'Session timeout cannot exceed 24 hours (1440 minutes)');
    
    // Test valid value
    cy.get('@settingsPanel')
      .find('label')
      .contains('Session Timeout')
      .parent()
      .find('input[type="number"]')
      .clear()
      .type('120');
    
    // Verify no validation error messages appear
    cy.get('@settingsPanel').should('not.contain', 'Session timeout must be greater than 0');
    cy.get('@settingsPanel').should('not.contain', 'Session timeout cannot exceed 24 hours (1440 minutes)');
  });

  it('should interact with auto save toggle', () => {
    cy.wait('@getSettings');
    
    // Find the auto save checkbox and click it to toggle off
    cy.get('@settingsPanel')
      .find('label')
      .contains('Auto Save')
      .parent()
      .find('input[type="checkbox"]')
      .click();
    
    // Verify the checkbox is now unchecked
    cy.get('@settingsPanel')
      .find('label')
      .contains('Auto Save')
      .parent()
      .find('input[type="checkbox"]')
      .should('not.be.checked');
  });

  it('should interact with language selection', () => {
    cy.wait('@getSettings');
    
    // Find the language dropdown and select Spanish
    cy.get('@settingsPanel')
      .find('label')
      .contains('Language')
      .parent()
      .find('select')
      .select('es');
    
    // Verify the selection was made
    cy.get('@settingsPanel')
      .find('label')
      .contains('Language')
      .parent()
      .find('select')
      .should('have.value', 'es');
  });


  it('should call saveSettings and close the panel on Save Settings button click', () => {
    cy.wait('@getSettings');
    
    // Make a change to ensure the save is meaningful
    cy.get('@settingsPanel')
      .find('label')
      .contains('Theme')
      .parent()
      .find('select')
      .select('light');
    
    // Click the Save Settings button
    cy.get('@settingsPanel')
      .find('button')
      .contains('Save Settings')
      .click();
    
    // Verify the API call was made
    cy.wait('@saveSettings');
    
    // Verify the panel is closed after saving
    cy.get('[role="dialog"]').should('not.exist');
  });

  it('should close the panel on Cancel button click', () => {
    cy.wait('@getSettings');
    
    // Make a change that should not be saved
    cy.get('@settingsPanel')
      .find('label')
      .contains('Theme')
      .parent()
      .find('select')
      .select('dark');
    
    // Click the Cancel button
    cy.get('@settingsPanel')
      .find('button')
      .contains('Cancel')
      .click();
    
    // Verify the panel is closed
    cy.get('[role="dialog"]').should('not.exist');
    
    // Verify no settings API call was made
    cy.get('@saveSettings.all').should('have.length', 0);
  });

  it('should call handleLogout and redirect on Logout button click', () => {
    cy.wait('@getSettings');
    
    // Click the Logout button
    cy.get('@settingsPanel')
      .find('button')
      .contains('Logout')
      .click();
    
    // Verify the logout API call was made
    cy.wait('@logout');
    
    // Verify redirection to home/login page
    cy.url().should('include', '/');
  });

  it('should fetch user settings when panel opens', () => {
    // This test verifies that settings are fetched when the panel opens
    // The beforeEach already sets up the intercept and opens the panel
    
    // Verify the settings API was called
    cy.wait('@getSettings');
    
    // Verify the settings are displayed correctly
    cy.get('@settingsPanel')
      .find('select')
      .first()
      .should('have.value', 'light');
    
    cy.get('@settingsPanel')
      .find('input[type="checkbox"]')
      .first()
      .should('be.checked');
  });

  it('should apply theme changes immediately', () => {
    cy.wait('@getSettings');
    
    // Select dark theme
    cy.get('@settingsPanel')
      .find('label')
      .contains('Theme')
      .parent()
      .find('select')
      .select('dark');
    
    // Save settings
    cy.get('@settingsPanel')
      .find('button')
      .contains('Save Settings')
      .click();
    
    // Verify theme is applied to HTML element
    cy.get('html').should('have.class', 'dark');
    
    // Reopen settings panel to verify persistence
    cy.get('[data-testid="open-settings-button"]').click();
    cy.get('[role="dialog"]').as('settingsPanel');
    
    // Verify the theme selection is still dark
    cy.get('@settingsPanel')
      .find('label')
      .contains('Theme')
      .parent()
      .find('select')
      .should('have.value', 'dark');
  });
});