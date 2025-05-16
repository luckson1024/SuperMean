/// <reference types="cypress" />
/// <reference types="chai" />

describe('API Authentication', () => {
  beforeEach(() => {
    // Clear local storage before each test to ensure clean state
    cy.clearLocalStorage();
  });

  it('should include auth token in API requests after login', () => {
    // Mock successful login response
    cy.intercept('POST', '**/auth/login', {
      statusCode: 200,
      body: {
        access_token: 'fake-jwt-token',
        user: {
          id: '1',
          username: 'testuser',
          email: 'test@example.com',
          role: 'user'
        }
      }
    }).as('loginRequest');

    // Mock a protected API endpoint
    cy.intercept('GET', '**/api/missions', (req: any) => {
      // Check if the request includes the Authorization header
      if (req.headers.authorization === 'Bearer fake-jwt-token') {
        req.reply({
          statusCode: 200,
          body: [{ id: '1', title: 'Test Mission' }]
        });
      } else {
        req.reply({
          statusCode: 401,
          body: { detail: 'Not authenticated' }
        });
      }
    }).as('missionsRequest');

    // Login
    cy.visit('/');
    cy.get('input[name="email"]').type('test@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.contains('button', 'Sign in').click();
    cy.wait('@loginRequest');

    // Navigate to missions page which should trigger the API request
    cy.contains('Missions').click();
    cy.wait('@missionsRequest');

    // Verify the request was successful (which means the auth token was included)
    cy.contains('Test Mission').should('be.visible');
  });

  it('should redirect to login when API returns 401', () => {
    // Set an expired token in localStorage
    cy.window().then((window: Window) => {
      window.localStorage.setItem('token', 'expired-token');
    });

    // Mock a protected API endpoint that returns 401
    cy.intercept('GET', '**/api/missions', {
      statusCode: 401,
      body: { detail: 'Token has expired' }
    }).as('missionsRequest');

    // Try to access a protected route
    cy.visit('/missions');
    cy.wait('@missionsRequest');

    // Should be redirected to login
    cy.url().should('include', '/');
    cy.contains('Sign in to your account').should('be.visible');
  });

  it('should refresh token when it expires', () => {
    // Mock successful login response
    cy.intercept('POST', '**/auth/login', {
      statusCode: 200,
      body: {
        access_token: 'initial-token',
        user: {
          id: '1',
          username: 'testuser',
          email: 'test@example.com',
          role: 'user'
        }
      }
    }).as('loginRequest');

    // Mock token refresh endpoint
    cy.intercept('POST', '**/auth/refresh', {
      statusCode: 200,
      body: {
        access_token: 'refreshed-token',
        token_type: 'bearer'
      }
    }).as('refreshToken');

    // Mock a protected API endpoint that first returns 401 (expired token) then succeeds
    let firstCall = true;
    cy.intercept('GET', '**/api/missions', (req: any) => {
      if (firstCall) {
        firstCall = false;
        req.reply({
          statusCode: 401,
          body: { detail: 'Token has expired' }
        });
      } else {
        // Check if the request includes the refreshed token
        if (req.headers.authorization === 'Bearer refreshed-token') {
          req.reply({
            statusCode: 200,
            body: [{ id: '1', title: 'Test Mission' }]
          });
        } else {
          req.reply({
            statusCode: 401,
            body: { detail: 'Not authenticated' }
          });
        }
      }
    }).as('missionsRequest');

    // Login
    cy.visit('/');
    cy.get('input[name="email"]').type('test@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.contains('button', 'Sign in').click();
    cy.wait('@loginRequest');

    // Navigate to missions page which should trigger the API request
    cy.contains('Missions').click();

    // First request fails with 401, which should trigger a token refresh
    cy.wait('@missionsRequest');
    cy.wait('@refreshToken');

    // Second request should succeed with the new token
    cy.wait('@missionsRequest');

    // Verify the request was successful (which means the auth token was refreshed)
    cy.contains('Test Mission').should('be.visible');

    // Verify the token was updated in localStorage
    cy.window().then((window: Window) => {
      expect(window.localStorage.getItem('token')).to.equal('refreshed-token');
    });
  });

  it('should handle API errors gracefully', () => {
    // Mock successful login response
    cy.intercept('POST', '**/auth/login', {
      statusCode: 200,
      body: {
        access_token: 'fake-jwt-token',
        user: {
          id: '1',
          username: 'testuser',
          email: 'test@example.com',
          role: 'user'
        }
      }
    }).as('loginRequest');

    // Mock a protected API endpoint that returns a server error
    cy.intercept('GET', '**/api/missions', {
      statusCode: 500,
      body: { detail: 'Internal server error' }
    }).as('missionsRequest');

    // Login
    cy.visit('/');
    cy.get('input[name="email"]').type('test@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.contains('button', 'Sign in').click();
    cy.wait('@loginRequest');

    // Navigate to missions page which should trigger the API request
    cy.contains('Missions').click();
    cy.wait('@missionsRequest');

    // Verify error message is displayed
    cy.contains('Error loading missions').should('be.visible');
    cy.contains('Internal server error').should('be.visible');
  });
});