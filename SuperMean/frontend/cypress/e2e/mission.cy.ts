/// <reference types="cypress" />

describe('Mission Management', () => {
  beforeEach(() => {
    // Mock successful login to get authenticated
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

    // Login before each test
    cy.visit('/');
    cy.get('input[name="email"]').type('test@example.com');
    cy.get('input[name="password"]').type('password123');
    cy.contains('button', 'Sign in').click();
    cy.wait('@loginRequest');
    cy.url().should('include', '/dashboard');

    // Navigate to missions page
    cy.contains('Missions').click();
    cy.url().should('include', '/missions');
  });

  it('should display missions list', () => {
    // Mock missions list response
    cy.intercept('GET', '**/missions', {
      statusCode: 200,
      body: [
        {
          id: '1',
          title: 'Build Login Page',
          description: 'Create a responsive login page with validation',
          status: 'in_progress',
          created_at: '2023-06-15T10:00:00Z',
          assigned_agents: ['agent1', 'agent2']
        },
        {
          id: '2',
          title: 'Implement Dashboard',
          description: 'Design and implement user dashboard with metrics',
          status: 'pending',
          created_at: '2023-06-16T10:00:00Z',
          assigned_agents: []
        }
      ]
    }).as('getMissions');

    // Verify missions are displayed
    cy.contains('h1', 'Missions').should('be.visible');
    cy.contains('Build Login Page').should('be.visible');
    cy.contains('Implement Dashboard').should('be.visible');
    cy.contains('In Progress').should('be.visible');
    cy.contains('Pending').should('be.visible');
  });

  it('should create a new mission', () => {
    // Mock create mission response
    cy.intercept('POST', '**/missions', {
      statusCode: 201,
      body: {
        id: '3',
        title: 'New Test Mission',
        description: 'This is a test mission created via Cypress',
        status: 'pending',
        created_at: '2023-06-17T10:00:00Z',
        assigned_agents: []
      }
    }).as('createMission');

    // Click create mission button
    cy.contains('button', 'Create Mission').click();
    
    // Fill out the form
    cy.get('input[name="title"]').type('New Test Mission');
    cy.get('textarea[name="description"]').type('This is a test mission created via Cypress');
    cy.contains('button', 'Submit').click();
    
    // Wait for the request to complete
    cy.wait('@createMission');
    
    // Verify the new mission appears in the list
    cy.contains('New Test Mission').should('be.visible');
    cy.contains('This is a test mission created via Cypress').should('be.visible');
  });

  it('should view mission details', () => {
    // Mock mission details response
    cy.intercept('GET', '**/missions/1', {
      statusCode: 200,
      body: {
        id: '1',
        title: 'Build Login Page',
        description: 'Create a responsive login page with validation',
        status: 'in_progress',
        created_at: '2023-06-15T10:00:00Z',
        assigned_agents: ['agent1', 'agent2'],
        steps: [
          { id: '1', description: 'Design mockup', status: 'completed' },
          { id: '2', description: 'Implement HTML/CSS', status: 'completed' },
          { id: '3', description: 'Add form validation', status: 'in_progress' }
        ]
      }
    }).as('getMissionDetails');

    // Click on a mission to view details
    cy.contains('Build Login Page').click();
    
    // Verify mission details are displayed
    cy.contains('h2', 'Build Login Page').should('be.visible');
    cy.contains('Create a responsive login page with validation').should('be.visible');
    cy.contains('Status: In Progress').should('be.visible');
    
    // Verify steps are displayed
    cy.contains('Design mockup').should('be.visible');
    cy.contains('Implement HTML/CSS').should('be.visible');
    cy.contains('Add form validation').should('be.visible');
  });

  it('should update mission status', () => {
    // Mock mission update response
    cy.intercept('PATCH', '**/missions/1', {
      statusCode: 200,
      body: {
        id: '1',
        title: 'Build Login Page',
        description: 'Create a responsive login page with validation',
        status: 'completed',
        created_at: '2023-06-15T10:00:00Z',
        assigned_agents: ['agent1', 'agent2']
      }
    }).as('updateMission');

    // Click on a mission to view details
    cy.contains('Build Login Page').click();
    
    // Change status
    cy.get('select[name="status"]').select('completed');
    cy.contains('button', 'Update Status').click();
    
    // Wait for the request to complete
    cy.wait('@updateMission');
    
    // Verify status is updated
    cy.contains('Status: Completed').should('be.visible');
  });

  it('should assign agents to a mission', () => {
    // Mock agents list response
    cy.intercept('GET', '**/agents', {
      statusCode: 200,
      body: [
        { id: 'agent1', name: 'Code Generator', type: 'code' },
        { id: 'agent2', name: 'Test Runner', type: 'test' },
        { id: 'agent3', name: 'Documentation Writer', type: 'docs' }
      ]
    }).as('getAgents');

    // Mock mission update response for agent assignment
    cy.intercept('POST', '**/missions/2/assign', {
      statusCode: 200,
      body: {
        id: '2',
        title: 'Implement Dashboard',
        description: 'Design and implement user dashboard with metrics',
        status: 'in_progress',
        created_at: '2023-06-16T10:00:00Z',
        assigned_agents: ['agent3']
      }
    }).as('assignAgent');

    // Click on a mission to view details
    cy.contains('Implement Dashboard').click();
    
    // Assign an agent
    cy.contains('button', 'Assign Agents').click();
    cy.contains('Documentation Writer').click();
    cy.contains('button', 'Confirm').click();
    
    // Wait for the request to complete
    cy.wait('@assignAgent');
    
    // Verify agent is assigned
    cy.contains('Assigned Agents:').should('be.visible');
    cy.contains('Documentation Writer').should('be.visible');
  });

  it('should delete a mission', () => {
    // Mock delete mission response
    cy.intercept('DELETE', '**/missions/2', {
      statusCode: 204
    }).as('deleteMission');

    // Click on a mission to view details
    cy.contains('Implement Dashboard').click();
    
    // Delete the mission
    cy.contains('button', 'Delete Mission').click();
    cy.contains('button', 'Confirm Delete').click();
    
    // Wait for the request to complete
    cy.wait('@deleteMission');
    
    // Verify mission is removed from the list
    cy.contains('Implement Dashboard').should('not.exist');
  });
});