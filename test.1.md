# SuperMean Testing Guide
at
This document provides comprehensive instructions for testing the SuperMean system, covering both backend and frontend components as well as system integration testing.

## Backend Testing

The SuperMean backend includes a robust test runner that can discover and execute all tests across different modules. The testing framework is designed to ensure code quality, functionality, and reliability.

### Running Backend Tests

The backend testing is managed through the `run.py` script located in the `SuperMean/backend` directory.

```bash
# Navigate to the backend directory
cd SuperMean/backend

# Run all tests
python run.py

# Run tests for specific modules
python run.py --modules agents memory super_agent

# Run tests for a single module
python run.py --modules memory

# Run tests with detailed output
python run.py --verbose

# Run tests with code coverage reporting
python run.py --coverage

# Run tests with specific tags
python run.py --tags critical security
```

The test runner will:
- Discover and execute all test files across the project
- Support running tests for specific modules (agents, memory, super_agent)
- Provide detailed test reporting with success/failure information
- Handle Python path configuration for proper imports
- Include error handling and verbose output options
- Generate code coverage reports when requested
- Support test filtering by tags for targeted testing

### Test Configuration

The test runner uses a configuration file located at `SuperMean/backend/tests/config.yaml` that can be customized for different testing environments:

```yaml
# Example test configuration
test:
  timeout: 30  # Default timeout in seconds for each test
  retry_count: 2  # Number of retries for flaky tests
  parallel: true  # Run tests in parallel when possible

environment:
  test_db_path: "./test_db"  # Path for test databases
  mock_llm: true  # Use mock LLM responses for faster testing
  api_keys_path: "./test_keys.env"  # Test API keys
```

## Module-Specific Tests

The SuperMean system is organized into several key modules, each with its own test suite. Below is a detailed breakdown of the tests available for each module.

### Memory Module Tests

The memory module provides different storage implementations for agent and system data. Run memory tests with:

```bash
python run.py --modules memory
```

#### Available Memory Tests

1. **BaseMemory Tests** (`base_memory_test.py`)
   - Verifies that the abstract base class cannot be instantiated directly
   - Confirms that subclasses must implement all abstract methods
   - Tests that complete implementations can be instantiated
   - Expected output: All assertions pass, confirming the contract enforcement
   - Common failures: Missing abstract method implementations, incorrect method signatures

2. **AgentMemory Tests** (`agent_memory_test.py`)
   - Tests in-memory storage and retrieval with and without metadata
   - Verifies key overwriting, deletion, and search functionality
   - Tests listing keys and clearing memory
   - Expected output: Successful storage/retrieval operations, proper metadata handling
   - Performance benchmarks: Storage operations < 5ms, retrieval operations < 2ms

3. **GlobalMemory Tests** (`global_memory_test.py`)
   - Tests ChromaDB-backed persistent vector storage
   - Verifies proper initialization with configuration parameters
   - Tests vector-based similarity search functionality
   - Expected output: Successful database operations, proper similarity rankings
   - Stress tests: Handles up to 10,000 concurrent entries with < 100ms retrieval time

4. **VectorMemory Tests** (`vector_memory_test.py`)
   - Tests multi-agent isolation in vector storage
   - Verifies global namespace access across agents
   - Tests shared context creation between agents
   - Expected output: Proper isolation between agent memories, successful sharing when intended
   - Security tests: Verifies memory isolation prevents unauthorized access

### Agents Module Tests

The agents module contains various specialized AI agents. Run agent tests with:

```bash
python run.py --modules agents
```

#### Available Agent Tests

1. **BaseAgent Tests** (`base_agent_test.py`)
   - Verifies the BaseAgent abstraction cannot be instantiated directly
   - Tests helper methods for LLM calls, skill usage, and memory operations
   - Expected output: Successful helper method calls, proper error handling
   - Mock testing: Uses LLM response mocks to test behavior without API calls

2. **ResearchAgent Tests** (`research_agent_test.py`)
   - Tests search and summarization workflows
   - Verifies proper handling of search results
   - Tests error handling for failed searches
   - Expected output: Successful search operations, proper summarization
   - Integration tests: Verifies integration with external search APIs

3. **DesignAgent Tests** (`design_agent_test.py`)
   - Tests UI/UX design proposal generation
   - Verifies design revision capabilities
   - Expected output: Valid design proposals in expected format
   - Visual regression tests: Ensures generated designs meet quality standards

4. **MedicalAgent Tests** (`medical_agent_test.py`)
   - Tests medical information retrieval and analysis
   - Verifies proper citation of medical sources
   - Expected output: Accurate medical information with proper citations
   - Compliance tests: Ensures all medical information includes required disclaimers

### Super Agent Module Tests

The super_agent module orchestrates multiple agents to solve complex tasks. Run super_agent tests with:

```bash
python run.py --modules super_agent
```

#### Available Super Agent Tests

1. **Planner Tests** (`planner_test.py`)
   - Tests plan creation with and without context
   - Verifies error handling for invalid plan formats
   - Expected output: Valid plan structures with proper step sequencing
   - Complexity tests: Verifies planning capability for tasks of varying complexity

2. **MetaPlanner Tests** (`meta_planner_test.py`)
   - Tests reflection and adaptation logic
   - Verifies handling of execution failures
   - Tests decision-making based on evaluation results
   - Expected output: Appropriate adaptation decisions based on execution outcomes
   - Resilience tests: Verifies recovery from various failure scenarios

3. **Evaluator Tests** (`evaluator_test.py`)
   - Tests goal achievement evaluation
   - Verifies suggestion generation for improvement
   - Expected output: Accurate evaluation scores and actionable suggestions
   - Consistency tests: Ensures consistent evaluation across similar inputs

4. **ToolCreator Tests** (`tool_creator_test.py`)
   - Tests dynamic tool/skill creation
   - Verifies proper code generation for new tools
   - Expected output: Valid, executable tool implementations
   - Security tests: Ensures generated tools follow security best practices

5. **Builder Tests** (`builder_test.py`)
   - Tests integration of planning, execution, and evaluation
   - Verifies end-to-end task completion
   - Expected output: Successful task completion with proper coordination
   - Performance tests: Measures end-to-end task completion time

## Interpreting Test Results

The test runner provides detailed output about test execution. Here's how to interpret the results:

### Success Indicators

- ✅ **PASS**: The test completed successfully with all assertions passing
- ❌ **FAIL**: One or more assertions failed during the test
- ⚠️ **ERROR**: An unexpected error occurred during test execution
- 🔄 **RETRY**: The test failed but will be retried (flaky test handling)
- ⏩ **SKIP**: The test was skipped due to dependencies or configuration

### Common Test Failures

1. **Memory Tests**:
   - Persistence failures: Check database configuration and permissions
   - Search inconsistencies: Verify vector dimensions and similarity thresholds
   - Transaction errors: Check for proper transaction handling and rollbacks

2. **Agent Tests**:
   - LLM connection failures: Verify API keys and network connectivity
   - Skill execution errors: Check skill implementations and dependencies
   - Timeout issues: Adjust timeout settings for complex operations

3. **Super Agent Tests**:
   - Plan parsing errors: Verify LLM output format compliance
   - Coordination failures: Check inter-agent communication channels
   - Resource contention: Verify proper resource allocation and locking

### Verbose Output

When running with the `--verbose` flag, the test runner provides additional information:

- Detailed error messages and stack traces
- Input/output values for failed assertions
- Timing information for performance analysis
- Memory usage statistics for resource monitoring
- API call logs for external service interactions

### Coverage Reports

When running with the `--coverage` flag, the test runner generates detailed code coverage reports:

```bash
# Generate HTML coverage report
python run.py --coverage --coverage-report html

# Open the coverage report
open htmlcov/index.html
```

The coverage report includes:
- Line-by-line coverage highlighting
- Branch coverage analysis
- Module and package-level statistics
- Uncovered code identification

## Frontend Testing

The SuperMean frontend uses Cypress for end-to-end testing of components and user interactions.

### Running Cypress Tests

```bash
# Navigate to the frontend directory
cd SuperMean/frontend

# Run Cypress tests in headless mode
npm run cypress:run

# Open Cypress Test Runner for interactive testing
npm run cypress:open

# Run specific test file
npm run cypress:run -- --spec "cypress/e2e/userSettingsPanel.cy.ts"

# Run tests with specific browser
npm run cypress:run -- --browser chrome

# Run tests with tags
npm run cypress:run -- --env grepTags=@smoke
```

### Component Testing

In addition to E2E tests, the frontend includes component-level tests:

```bash
# Run component tests
npm run test:components

# Run with coverage
npm run test:components:coverage
```

Component tests verify individual UI components in isolation, ensuring they:
- Render correctly with different props
- Handle user interactions properly
- Manage state correctly
- Display appropriate loading and error states

### UserSettingsPanel Tests

The `userSettingsPanel.cy.ts` file contains comprehensive tests for the User Settings Panel component. These tests verify:

1. **Theme Selection**
   - Selecting different themes (light/dark)
   - Verifying theme changes are applied to the UI
   - Confirming theme persistence after reopening the panel
   - Testing system theme detection and automatic switching

2. **Notifications Toggle**
   - Toggling notifications on/off
   - Verifying the checkbox state changes correctly
   - Testing permission requests on enabling notifications
   - Verifying notification delivery after enabling

3. **Session Timeout Settings**
   - Testing validation for invalid values (too low/high)
   - Verifying error messages appear appropriately
   - Confirming valid values are accepted
   - Testing actual session timeout behavior

4. **Auto Save Toggle**
   - Toggling auto save on/off
   - Verifying the checkbox state changes correctly
   - Testing auto save functionality with content changes
   - Measuring performance impact of auto save

5. **Language Selection**
   - Selecting different language options
   - Verifying the selection is applied correctly
   - Testing UI text changes after language switch
   - Verifying RTL layout for appropriate languages

6. **Panel Interactions**
   - Testing Save Settings functionality
   - Verifying Cancel button closes the panel without saving
   - Testing Logout functionality and redirection
   - Verifying unsaved changes warnings

### Test Setup

The tests use Cypress interceptors to mock API responses:

```javascript
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
```

## System Integration Testing

System integration tests verify that all components work together correctly. These tests span both backend and frontend components.

### Running Integration Tests

```bash
# Start the full system in test mode
cd SuperMean
./scripts/start_test_environment.sh

# Run integration test suite
python -m tests.integration.run_tests
```

### Integration Test Scenarios

1. **End-to-End Task Completion**
   - Tests complete task lifecycle from user input to final output
   - Verifies all components communicate correctly
   - Expected output: Successful task completion with proper UI updates

2. **Multi-Agent Collaboration**
   - Tests complex tasks requiring multiple specialized agents
   - Verifies proper task delegation and result aggregation
   - Expected output: Coordinated task completion with efficient resource usage

3. **Error Recovery**
   - Tests system behavior when components fail
   - Verifies graceful degradation and recovery mechanisms
   - Expected output: Appropriate error handling and recovery where possible

4. **Performance Under Load**
   - Tests system behavior with multiple concurrent users
   - Verifies resource allocation and request prioritization
   - Expected output: Consistent performance within defined SLAs

### Integration Test Monitoring

The integration test suite includes monitoring tools that track:

- API response times across system boundaries
- Memory usage patterns during complex operations
- Database query performance and connection pool usage
- Message queue depths and processing latencies
- UI rendering and interaction response times

## Advanced Testing Scenarios

### Testing Multiple Modules Together

For testing interactions between modules, you can specify multiple modules in a single command:

```bash
# Test memory and agents together
python run.py --modules memory agents

# Test all components of the super_agent module with agents
python run.py --modules super_agent agents
```

This is particularly useful for testing integration points between:
- Memory persistence and agent recall capabilities
- Super agent planning and individual agent execution
- Cross-agent communication via shared memory contexts

### Testing with Custom Configuration

You can provide custom configuration for tests by setting environment variables:

```bash
# Use a specific model for LLM tests
MODEL_PROVIDER=openai MODEL_NAME=gpt-4 python run.py --modules agents

# Use a test database for memory tests
TEST_DB_PATH=./test_db python run.py --modules memory

# Set custom timeout for long-running tests
TEST_TIMEOUT=120 python run.py --modules super_agent
```

### Testing Edge Cases

The test suite includes specific edge case tests that can be run with tags:

```bash
# Run only error handling tests
python run.py --tags error_handling

# Run only performance tests
python run.py --tags performance

# Run only security tests
python run.py --tags security

# Run tests for specific scenarios
python run.py --tags "high_load concurrent_access"
```

Edge case tests verify system behavior under extreme conditions:
- Very large input data
- Concurrent access patterns
- Network partitioning scenarios
- Resource exhaustion conditions
- Malformed input handling

### Troubleshooting Test Failures

#### Memory Module Issues

1. **VectorMemory Test Failures**
   - **Symptom**: `IndexError` or dimension mismatch errors
   - **Solution**: Check vector dimensions in configuration match the model output dimensions
   - **Command**: `python -m backend.memory.vector_memory_test --debug`
   - **Logs**: Check `logs/vector_memory_debug.log` for detailed error information

2. **GlobalMemory Persistence Issues**
   - **Symptom**: Failed retrievals after storage
   - **Solution**: Verify ChromaDB installation and permissions
   - **Command**: `python -m backend.memory.global_memory_test --reset-db`
   - **Database**: Inspect `test_db/chroma` directory for corruption

#### Agents Module Issues

1. **LLM Connection Failures**
   - **Symptom**: Timeout errors in agent tests
   - **Solution**: Check API keys and network connectivity
   - **Command**: `python -m backend.agents.base_agent_test --mock-llm`
   - **Environment**: Verify `.env` file contains valid API keys

2. **Skill Execution Errors**
   - **Symptom**: `SkillError` exceptions
   - **Solution**: Verify skill dependencies are installed
   - **Command**: `python -m backend.agents.research_agent_test --list-dependencies`
   - **Dependencies**: Run `pip install -r requirements-dev.txt` to ensure all dependencies

#### Super Agent Module Issues

1. **Plan Parsing Errors**
   - **Symptom**: `PlanningError` with JSON parsing failures
   - **Solution**: Check LLM output format compliance
   - **Command**: `python -m backend.super_agent.planner_test --show-raw-output`
   - **Templates**: Verify prompt templates in `backend/prompts/planning/`

2. **Coordination Failures**
   - **Symptom**: Tasks stuck in "pending" state
   - **Solution**: Check event bus and message passing
   - **Command**: `python -m backend.super_agent.builder_test --trace-events`
   - **Monitoring**: Check `logs/event_bus.log` for message delivery issues

## Test Best Practices

1. **Isolation**: Each test should be independent and not rely on the state from previous tests.

2. **Mocking**: Use API mocks to isolate frontend testing from backend dependencies.

3. **Selectors**: Use data-testid attributes for reliable element selection.

4. **Assertions**: Make specific assertions about the expected state after actions.

5. **Wait for Async Operations**: Always wait for API calls and animations to complete before making assertions.

6. **Test Coverage**: Aim for at least 80% code coverage across all modules.

7. **Performance Benchmarks**: Include performance assertions for critical operations.

8. **Security Testing**: Verify authentication and authorization in integration tests.

9. **Deterministic Tests**: Ensure tests produce consistent results across multiple runs.

10. **Test Data Management**: Use fixtures and factories to generate test data consistently.

## Continuous Integration

Both backend and frontend tests can be integrated into CI/CD pipelines to ensure code quality before deployment.

```bash
# Example CI command for running all tests
cd SuperMean/backend && python run.py && cd ../frontend && npm run cypress:run
```

The CI pipeline includes:

1. **Linting and Static Analysis**
   - Python: flake8, mypy, black
   - JavaScript/TypeScript: ESLint, Prettier

2. **Unit and Integration Tests**
   - Backend: pytest with coverage reporting
   - Frontend: Jest and Cypress with coverage reporting

3. **Security Scanning**
   - Dependency vulnerability scanning
   - Static application security testing (SAST)
   - Secret detection in code

4. **Performance Testing**
   - Load testing critical endpoints
   - Memory leak detection
   - UI rendering performance

5. **Deployment Verification**
   - Smoke tests after deployment
   - Canary testing for gradual rollout
   - Rollback automation for failed deployments

## Test-Driven Development Workflow

The SuperMean project follows a test-driven development (TDD) approach:

1. **Write Tests First**: Define expected behavior before implementation
2. **Run Tests (They Should Fail)**: Verify tests correctly detect missing functionality
3. **Implement Functionality**: Write minimal code to make tests pass
4. **Run Tests Again**: Verify implementation meets requirements
5. **Refactor**: Improve code quality while maintaining passing tests

This approach ensures high test coverage and helps prevent regressions during development.