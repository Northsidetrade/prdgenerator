# PRD Generator (Ollama + Mistral Edition)

This is a fork of Northsidetrade/prdgenerator, modified to run entirely locally using Ollama and the Mistral-7B-Instruct model — no OpenAI or Anthropic APIs needed.

## Features

- Generates full Product Requirements Documents (PRDs)
- Powered by local LLM (no API keys required)
- Easy to run offline
- Supports multiple template types: crud, ai_agent, saas, custom

## Requirements

- Python 3.10 or newer
- Ollama installed (https://ollama.com/download)
- Git
- curl or Postman

## Quick Setup

1. Install Ollama  
   Download and install Ollama for your operating system:  
   https://ollama.com/download

2. Pull the Mistral model  

        ollama pull mistral

3. Clone this repository  
- git clone https://github.com/Northsidetrade/prdgenerator.git
- cd prdgenerator


4. Set up and activate the virtual environment  
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt


5. Run the FastAPI server  
    python no_auth_server.py


6. Test the API using curl  

    curl -s -X POST http://localhost:8888/api/v1/prd/generate
    -H "Content-Type: application/json"
    -d '{
    "title": "Mindful Habits App",
    "input_prompt": "an app that helps users stay mindful through journaling and reminders",
    "template_type": "saas",
    "format": "markdown"
    }' | jq -r .content


## Template Types

- crud: Standard create/read/update/delete apps
- ai_agent: AI-powered tools and assistants
- saas: Cloud platforms or subscription-based services
- custom: General-purpose PRD structure

## License and Credits

This is a community-driven fork of Northsidetrade/prdgenerator.  
Created to enable fast, local prototyping using open-source language models.

## Contact

Maintained by: Northsidetrade  
GitHub: https://github.com/Northsidetrade
