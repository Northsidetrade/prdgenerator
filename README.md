# PRD Generator
AI Powered PRD Generator for AI Pair Programming

## Overview

PRD Generator is a tool that leverages AI models (OpenAI GPT-4 and Anthropic Claude) to automatically generate Product Requirements Documents based on simple inputs. This project follows the Semantic Seed Venture Studio Coding Standards with a focus on code quality, security, and test-driven development.

## Features

- **No-Auth Mode**: Run the server without authentication for easy testing and development
- **AI-Powered Generation**: Uses OpenAI GPT-4 and Anthropic Claude for high-quality PRD generation
- **Multiple Templates**: Choose from CRUD, AI Agent, SaaS, or Custom templates
- **Format Options**: Generate PRDs in Markdown or JSON format
- **Simple API**: RESTful API with clear endpoints and documentation
- **Basic Frontend**: Modern web interface with Bootstrap 5 and EasyMDE for Markdown editing

## Project Structure

```
prdgenerator/
├── frontend/                 # Static frontend files
│   ├── css/                 # Custom styles
│   ├── js/                  # JavaScript modules
│   └── templates/           # HTML templates
├── no_auth_server.py        # No-auth FastAPI server
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables
```

## API Endpoints

### No-Auth Server (Port 8888)

- `GET /api/v1/health` - Health check endpoint
- `POST /api/v1/prd/generate` - Generate a new PRD
- `GET /api/v1/prd` - List all generated PRDs

#### PRD Generation Payload
```json
{
    "title": "Product Name",
    "input_prompt": "Product Description",
    "template_type": "crud_application|ai_agent|saas_platform|custom",
    "format": "markdown|json"
}
```

## Frontend Components

- **Navigation**: Responsive navbar with links to main features
- **PRD Generation Form**: 
  - Product Title input
  - Product Description textarea
  - Template Type selector
  - Output Format selector
- **Result Display**:
  - Markdown editor for viewing generated PRD
  - Copy to clipboard functionality
  - Download options (Markdown/JSON)

## Quick Start

### Prerequisites

1. Python 3.8 or higher
2. Node.js 14 or higher (optional, for development)
3. OpenAI API key
4. Anthropic API key

### Environment Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd prdgenerator
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```env
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
DEFAULT_MODEL_PROVIDER=openai
```

### Running the Application

1. Start the No-Auth Server:
```bash
python no_auth_server.py
```
The server will start on http://0.0.0.0:8888

2. Start the Frontend:
```bash
cd frontend
python -m http.server 3001
```
Access the frontend at http://localhost:3001

### Using the Application

1. Navigate to http://localhost:3001/templates/generate.html
2. Fill out the PRD generation form:
   - Enter product title
   - Provide detailed product description
   - Select template type
   - Choose output format
3. Click "Generate PRD"
4. View, copy, or download the generated PRD

## Development

### Key Dependencies

- **Backend**:
  - FastAPI: Web framework
  - Pydantic: Data validation
  - OpenAI & Anthropic: AI providers
  - python-dotenv: Environment management

- **Frontend**:
  - Bootstrap 5: UI framework
  - EasyMDE: Markdown editor
  - Native Fetch API: HTTP requests

## Testing

Run the test suite:
```bash
pytest
```

## Contributing

1. Follow the Semantic Seed Venture Studio Coding Standards
2. Write tests for new features
3. Update documentation as needed
4. Submit pull requests with clear descriptions

## License

[MIT License](LICENSE)
