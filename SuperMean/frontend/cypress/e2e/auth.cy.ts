/// <reference types="cypress" />
/// <reference types="cypress/types/net-stubbing" />
/// <reference types="cypress/types/cypress" />
describe('Authentication Flow', () => {
  beforeEach(() => {
    // Clear local storage before each test to ensure clean state
    cy.clearLocalStorage();
  });

  it('should display login page', () => {
    cy.visit('/');
    cy.contains('Sign in to your account');
    cy.get('input[name="email"]').should('exist');
    cy.get('input[name="password"]').should('exist');
    cy.contains('button', 'Sign in').should('exist');
  });

  it('should navigate to register page', () => {
    cy.visit('/');
    cy.contains('Don\'t have an account? Register').click();
    cy.url().should('include', '/register');
    cy.contains('Create your account');
    cy.get('input[name="username"]').should('exist');
    cy.get('input[name="email"]').should('exist');
    cy.get('input[name="password"]').should('exist');
    cy.get('input[name="confirm-password"]').should('exist');
  });

  it('should show error when passwords do not match on register page', () => {
    cy.visit('/register');
    cy.get('input[name="username"]').type('testuser');
    cy.get('input[name="email"]').type('test@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.get('input[name="confirm-password"]').type('password456');
    cy.contains('button', 'Register').click();
    cy.contains('Passwords do not match').should('be.visible');
  });

  it('should show error on failed login', () => {
    // Mock failed login response
    cy.intercept('POST', '**/auth/login', {
      statusCode: 401,
      body: { detail: 'Invalid credentials' }
    }).as('loginRequest');

    cy.visit('/');
    cy.get('input[name="email"]').type('wrong@example.com');
    cy.get('input[name="password"]').type('wrongpassword');
    cy.contains('button', 'Sign in').click();
    cy.wait('@loginRequest');
    cy.contains('Invalid credentials').should('be.visible');
  });

  it('should redirect to dashboard after successful login', () => {
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

    cy.visit('/');
    cy.get('input[name="email"]').type('test@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.contains('button', 'Sign in').click();
    cy.wait('@loginRequest');
    cy.url().should('include', '/dashboard');
    cy.contains('Welcome, testuser!').should('be.visible');
    // Verify JWT token is stored in local storage
    cy.window().then((window) => {
      expect(window.localStorage.getItem('token')).to.equal('fake-jwt-token');
    });
  });

  it('should redirect to login page when accessing protected route while unauthenticated', () => {
    cy.visit('/dashboard');
    cy.url().should('include', '/');
    cy.contains('Sign in to your account').should('be.visible');
  });

  it('should successfully log out', () => {
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

    // Login first
    cy.visit('/');
    cy.get('input[name="email"]').type('test@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.contains('button', 'Sign in').click();
    cy.wait('@loginRequest');
    cy.url().should('include', '/dashboard');

    // Then logout
    cy.contains('Sign out').click();
    cy.url().should('include', '/');
    cy.contains('Sign in to your account').should('be.visible');
  });
});