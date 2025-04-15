# PRD Generator - Project Backlog

This document tracks the project backlog for the PRD Generator, following Semantic Seed Venture Studio Coding Standards V2.0.

## 📋 Completed Stories

### Features
- [x] **BE-01**: Set up FastAPI application foundation
  - Basic project structure
  - Configuration management
  - Health endpoint
  - Core dependencies
  - Points: 3

- [x] **BE-02**: Define PRD generation schemas
  - PRD input schemas
  - PRD response schemas
  - Template types enum
  - Format types enum
  - Points: 2

- [x] **BE-03**: Implement PRD generation endpoint
  - API route for PRD generation
  - Input validation
  - Basic response structure
  - Points: 3

- [x] **BE-04**: Implement LLM integration
  - OpenAI API integration
  - Anthropic API integration
  - Template system for different PRD types
  - Async processing implementation
  - Points: 5

- [x] **TEST-01**: Implement testing framework
  - BDD tests for PRD generation
  - TestClient setup
  - Test database configuration
  - Points: 3

### Bugs
- [x] **BUG-01**: Fix async handling in LLM service
  - Properly handle asynchronous calls to OpenAI and Anthropic APIs
  - Use thread pools for non-async client libraries
  - Points: 2

### Chores
- [x] **CHORE-01**: Set up project structure
  - Initialize repository
  - Set up virtual environment
  - Add core dependencies
  - Points: 1

- [x] **CHORE-02**: Configure testing environment
  - Set up pytest
  - Configure test database
  - Implement fixtures
  - Points: 1

## 📝 Current Sprint Backlog

### Features
- [ ] **BE-05**: Implement database models
  - SQLAlchemy models for PRDs
  - Migrations with Alembic
  - Repository pattern for data access
  - Points: 5

- [ ] **BE-06**: Add user authentication
  - User registration and login
  - JWT authentication
  - User-PRD association
  - Points: 8

- [ ] **BE-07**: Implement project persistence
  - Save generated PRDs to database
  - Retrieve user's PRDs
  - Delete and update operations
  - Points: 5

### Chores
- [ ] **CHORE-03**: Update Pydantic to V2 patterns
  - Replace orm_mode with from_attributes
  - Update config class to ConfigDict
  - Points: 2

- [ ] **CHORE-04**: Update SQLAlchemy imports
  - Replace deprecated imports
  - Update to SQLAlchemy 2.0 patterns
  - Points: 2

## 🔮 Future Backlog

### Features
- [ ] **FE-01**: Implement basic UI
  - Create form for PRD input
  - Display generated PRD
  - Basic navigation
  - Points: 8

- [ ] **BE-08**: Implement template management
  - CRUD operations for custom templates
  - Template versioning
  - Points: 5

- [ ] **BE-09**: Add export functionality
  - Export to PDF
  - Export to Word
  - Points: 3

### Chores
- [ ] **CHORE-05**: Set up CI/CD pipeline
  - GitHub Actions configuration
  - Automated testing
  - Deployment to cloud provider
  - Points: 3
