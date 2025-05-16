/// <reference types="cypress" />

describe('SuperAgent Management', () => {
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

    // Navigate to agents page
    cy.contains('Agents').click();
    cy.url().should('include', '/agents');
  });

  it('should display agents list', () => {
    // Mock agents list response
    cy.intercept('GET', '**/agents', {
      statusCode: 200,
      body: [
        {
          id: 'agent1',
          name: 'Code Generator',
          type: 'code',
          capabilities: ['generate_code', 'refactor_code'],
          status: 'available'
        },
        {
          id: 'agent2',
          name: 'Test Runner',
          type: 'test',
          capabilities: ['run_tests', 'generate_test_cases'],
          status: 'busy'
        },
        {
          id: 'agent3',
          name: 'Documentation Writer',
          type: 'docs',
          capabilities: ['generate_docs', 'update_readme'],
          status: 'available'
        }
      ]
    }).as('getAgents');

    // Verify agents are displayed
    cy.contains('h1', 'SuperAgents').should('be.visible');
    cy.contains('Code Generator').should('be.visible');
    cy.contains('Test Runner').should('be.visible');
    cy.contains('Documentation Writer').should('be.visible');
    cy.contains('Available').should('be.visible');
    cy.contains('Busy').should('be.visible');
  });

  it('should view agent details', () => {
    // Mock agent details response
    cy.intercept('GET', '**/agents/agent1', {
      statusCode: 200,
      body: {
        id: 'agent1',
        name: 'Code Generator',
        type: 'code',
        description: 'Generates and refactors code based on requirements',
        capabilities: ['generate_code', 'refactor_code'],
        status: 'available',
        created_at: '2023-05-10T08:00:00Z',
        metrics: {
          tasks_completed: 42,
          success_rate: 0.95,
          average_completion_time: 120
        },
        current_assignments: []
      }
    }).as('getAgentDetails');

    // Click on an agent to view details
    cy.contains('Code Generator').click();
    
    // Verify agent details are displayed
    cy.contains('h2', 'Code Generator').should('be.visible');
    cy.contains('Generates and refactors code based on requirements').should('be.visible');
    cy.contains('Status: Available').should('be.visible');
    cy.contains('Tasks Completed: 42').should('be.visible');
    cy.contains('Success Rate: 95%').should('be.visible');
  });

  it('should create a new agent', () => {
    // Mock create agent response
    cy.intercept('POST', '**/agents', {
      statusCode: 201,
      body: {
        id: 'agent4',
        name: 'New Test Agent',
        type: 'utility',
        description: 'This is a test agent created via Cypress',
        capabilities: ['test_capability'],
        status: 'available',
        created_at: '2023-06-17T10:00:00Z'
      }
    }).as('createAgent');

    // Click create agent button
    cy.contains('button', 'Create Agent').click();
    
    // Fill out the form
    cy.get('input[name="name"]').type('New Test Agent');
    cy.get('select[name="type"]').select('utility');
    cy.get('textarea[name="description"]').type('This is a test agent created via Cypress');
    cy.get('input[name="capabilities"]').type('test_capability');
    cy.contains('button', 'Submit').click();
    
    // Wait for the request to complete
    cy.wait('@createAgent');
    
    // Verify the new agent appears in the list
    cy.contains('New Test Agent').should('be.visible');
  });

  it('should update agent status', () => {
    // Mock agent update response
    cy.intercept('PATCH', '**/agents/agent3', {
      statusCode: 200,
      body: {
        id: 'agent3',
        name: 'Documentation Writer',
        type: 'docs',
        capabilities: ['generate_docs', 'update_readme'],
        status: 'maintenance'
      }
    }).as('updateAgent');

    // Click on an agent to view details
    cy.contains('Documentation Writer').click();
    
    // Change status
    cy.get('select[name="status"]').select('maintenance');
    cy.contains('button', 'Update Status').click();
    
    // Wait for the request to complete
    cy.wait('@updateAgent');
    
    // Verify status is updated
    cy.contains('Status: Maintenance').should('be.visible');
  });

  it('should test agent capabilities', () => {
    // Mock agent test response
    cy.intercept('POST', '**/agents/agent1/test', {
      statusCode: 200,
      body: {
        success: true,
        capability: 'generate_code',
        result: 'function testFunction() { return "Hello World"; }',
        execution_time: 1.5
      }
    }).as('testAgent');

    // Click on an agent to view details
    cy.contains('Code Generator').click();
    
    // Test a capability
    cy.contains('button', 'Test Capabilities').click();
    cy.get('select[name="capability"]').select('generate_code');
    cy.get('textarea[name="test_input"]').type('Create a simple hello world function');
    cy.contains('button', 'Run Test').click();
    
    // Wait for the request to complete
    cy.wait('@testAgent');
    
    // Verify test results are displayed
    cy.contains('Test Successful').should('be.visible');
    cy.contains('function testFunction()').should('be.visible');
    cy.contains('Execution Time: 1.5s').should('be.visible');
  });

  it('should view agent activity history', () => {
    // Mock agent history response
    cy.intercept('GET', '**/agents/agent2/history', {
      statusCode: 200,
      body: [
        {
          id: 'activity1',
          timestamp: '2023-06-15T14:30:00Z',
          action: 'run_tests',
          details: 'Executed 15 test cases for Login Component',
          result: 'success',
          mission_id: 'mission1'
        },
        {
          id: 'activity2',
          timestamp: '2023-06-14T10:15:00Z',
          action: 'generate_test_cases',
          details: 'Generated 8 test cases for API endpoints',
          result: 'success',
          mission_id: 'mission2'
        }
      ]
    }).as('getAgentHistory');

    // Click on an agent to view details
    cy.contains('Test Runner').click();
    
    // View history
    cy.contains('button', 'View Activity History').click();
    
    // Wait for the request to complete
    cy.wait('@getAgentHistory');
    
    // Verify history is displayed
    cy.contains('h3', 'Activity History').should('be.visible');
    cy.contains('Executed 15 test cases for Login Component').should('be.visible');
    cy.contains('Generated 8 test cases for API endpoints').should('be.visible');
  });

  it('should delete an agent', () => {
    // Mock delete agent response
    cy.intercept('DELETE', '**/agents/agent3', {
      statusCode: 204
    }).as('deleteAgent');

    // Click on an agent to view details
    cy.contains('Documentation Writer').click();
    
    // Delete the agent
    cy.contains('button', 'Delete Agent').click();
    cy.contains('button', 'Confirm Delete').click();
    
    // Wait for the request to complete
    cy.wait('@deleteAgent');
    
    // Verify agent is removed from the list
    cy.contains('Documentation Writer').should('not.exist');
  });
});