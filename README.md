# PRD Generator
AI Powered PRD Generator for AI Pair Programming

## Overview

PRD Generator is a tool that leverages AI models to automatically generate Product Requirements Documents based on simple inputs. This project follows the Semantic Seed Venture Studio Coding Standards with a focus on code quality, security, and test-driven development.

## Features

- **No-Auth Mode**: Run the server without authentication for easy testing and development
- **AI-Powered Generation**: Uses OpenAI GPT-4 and Anthropic Claude for high-quality PRD generation
- **Multiple Templates**: Choose from CRUD, AI Agent, SaaS, or Custom templates
- **Format Options**: Generate PRDs in Markdown or JSON format
- **Simple API**: RESTful API with clear endpoints and documentation
- **Basic Frontend**: Simple web interface for testing the API

## Quick Start

### Running the No-Auth Server

The no-auth server provides all API functionality without requiring authentication, making it perfect for development and testing.

```bash
# Activate virtual environment
source venv/bin/activate

# Run the no-auth server
python no_auth_server.py
```

The server will start on http://0.0.0.0:8888 with all endpoints accessible without authentication.

### Running the Frontend

```bash
# Start a simple HTTP server in the frontend directory
cd frontend
python -m http.server 8080
```

Access the frontend at http://localhost:8080

## API Endpoints

### Public Endpoints

- `GET /` - Root endpoint, returns health status
- `GET /api/v1/health` - Health check endpoint
- `POST /api/v1/auth/login` - Login endpoint (always succeeds in no-auth mode)
- `POST /api/v1/auth/register` - Registration endpoint (always succeeds in no-auth mode)
- `GET /api/v1/users/me` - Get current user info (returns default user in no-auth mode)
- `POST /api/v1/prd/generate` - Generate a new PRD
- `GET /api/v1/prd` - Get all generated PRDs

### Generating a PRD

To generate a PRD, send a POST request to `/api/v1/prd/generate` with the following JSON body:

```json
{
  "title": "Your PRD Title",
  "input_prompt": "Description of your product or feature",
  "template_type": "custom",  // Options: "crud", "ai_agent", "saas", "custom"
  "format": "markdown"  // Options: "markdown", "json"
}
```

## Environment Variables

The application uses the following environment variables from the `.env` file:

- `OPENAI_API_KEY` - Your OpenAI API key
- `ANTHROPIC_API_KEY` - Your Anthropic API key
- `DEFAULT_MODEL_PROVIDER` - Default AI provider to use (openai or anthropic)

## Development

### Project Structure

- `app/` - Main application code
  - `api/` - API endpoints and dependencies
  - `core/` - Core application configuration
  - `db/` - Database models and session management
  - `services/` - Service layer, including LLM integration
- `frontend/` - Simple web interface for testing
- `no_auth_server.py` - Standalone server without authentication
- `direct_server.py` - Alternative no-auth implementation

### Testing

Run tests with pytest:

```bash
pytest
```

## License

[MIT License](LICENSE)
