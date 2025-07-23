# Advanced Aeromedical Evidence Review & Research System

## Table of Contents

1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Installation Guide](#installation-guide)
4. [Configuration](#configuration)
5. [Usage Guide](#usage-guide)
6. [Features](#features)
7. [API Reference](#api-reference)
8. [Troubleshooting](#troubleshooting)
9. [Development](#development)
10. [Contributing](#contributing)

## Overview

The Advanced Aeromedical Evidence Review & Research System is a sophisticated multi-agent AI framework designed for:

- **Aeromedical Research**: Specialized analysis of aerospace medicine topics
- **Systematic Reviews**: Automated PRISMA 2020-compliant systematic literature reviews
- **Risk Assessments**: Specialized aeromedical risk evaluation for pilots and astronauts
- **Query Optimization**: Automatic enhancement of research queries for scientific accuracy

### Key Capabilities

- 🔬 **Multi-Agent Architecture**: Multiple specialized AI agents for different research tasks
- 🎯 **Smart Mode Detection**: Automatic selection of the most appropriate agent
- 📊 **PRISMA Compliance**: Full support for PRISMA 2020 systematic review methodology
- 🌐 **External Knowledge Integration**: Access to Perplexity, Grok, and custom Flowise instances
- ⚡ **Asynchronous Processing**: Background job handling for long-running research tasks
- 📝 **Professional Export**: Clean Markdown export of results and conversations

## System Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                      │
├─────────────────────────────────────────────────────────────┤
│                      Core Application                         │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Mode Manager│  │Query Optimizer│  │  Job Management  │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                      Agent Systems                            │
│  ┌────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  Prompt    │  │   Flowise    │  │     PRISMA        │  │
│  │Enhancement │  │   Agents     │  │  Agent System     │  │
│  └────────────┘  └──────────────┘  └───────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    External Services                          │
│  ┌────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  OpenAI    │  │  Perplexity  │  │      Grok         │  │
│  │    API     │  │     API      │  │      API          │  │
│  └────────────┘  └──────────────┘  └───────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Core Components

1. **Mode Manager** (`src/mode_manager.py`)
   - Handles mode switching and smart detection
   - Routes queries to appropriate agents

2. **Query Optimizer** (`src/core_agents/query_optimizer.py`)
   - Enhances queries with scientific methodology
   - Integrates current research context
   - Ensures proper citation requirements

3. **Agent Systems**
   - **Prompt Enhancement**: General-purpose query enhancement
   - **Flowise Agents**: Specialized research agents (Deep Research, Aeromedical Risk, Aerospace RAG)
   - **PRISMA System**: Multi-step systematic review workflow

4. **Job Management** (`src/jobs.py`)
   - Handles background processing for long-running tasks
   - Provides status tracking and result retrieval

## Installation Guide

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the project root:
   ```env
   # Core APIs (Required)
   OPENAI_API_KEY=your_openai_api_key
   FLOWISE_API_KEY=your_flowise_api_key
   
   # PRISMA Features (Required for PRISMA mode)
   PPLX_API_KEY=your_perplexity_api_key
   XAI_API_KEY=your_grok_api_key
   
   # Optional Flowise Configuration
   FLOWISE_API_URL=https://your.flowise.instance.com
   ```

## Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `OPENAI_API_KEY` | Yes | OpenAI API key for general AI features | - |
| `FLOWISE_API_KEY` | Yes | Flowise API key for specialized agents | - |
| `PPLX_API_KEY` | Yes* | Perplexity API key for research context | - |
| `XAI_API_KEY` | Yes* | Grok API key for PRISMA features | - |
| `FLOWISE_API_URL` | No | Custom Flowise instance URL | Cloud version |

*Required only for PRISMA and advanced research features

### Flowise Chatflow IDs

The system uses specific chatflow IDs for different agents. These can be overridden via environment variables:

- `CHATFLOW_AEROMEDICAL_RISK`: Aeromedical risk assessment agent
- `CHATFLOW_DEEP_RESEARCH`: Deep research agent
- `CHATFLOW_AEROSPACE_MEDICINE_RAG`: Aerospace medicine RAG agent

## Usage Guide

### Starting the Application

```bash
python run.py
```

### Command-Line Options

```bash
# Start in a specific mode
python run.py --mode prisma

# Run a single query
python run.py --mode prompt --query "Your research question"
```

### Interactive Commands

| Command | Description |
|---------|-------------|
| `?` or `/help` | Show contextual help |
| `/modes` | List all available modes |
| `/smart` | Switch to smart mode (default) |
| `/prompt` | Switch to prompt enhancement mode |
| `/deep` | Switch to deep research mode |
| `/aero` | Switch to aeromedical risk mode |
| `/aerospace` | Switch to aerospace medicine RAG mode |
| `/prisma` | Start PRISMA systematic review |
| `/transfer <mode>` | Re-run last query in different mode |
| `/history` | Show conversation history |
| `/jobs` | View background job status |
| `/export` | Export last response to Markdown |
| `/save` | Export entire conversation |
| `/clear` | Clear conversation history |
| `/quit` | Exit application |

### Query Optimization Pipeline

Every query automatically goes through optimization:

1. **Research Analysis**: Determines domain, complexity, and data requirements
2. **Source Gathering**: Retrieves current research context from reputable sources
3. **Query Enhancement**: Restructures with scientific methodology and citations

### PRISMA Systematic Reviews

The PRISMA mode provides a guided workflow:

1. **Define Research Question**: Formulate PICO/PICOS framework
2. **Search Strategy**: Develop comprehensive search terms
3. **Study Selection**: Apply inclusion/exclusion criteria
4. **Data Extraction**: Extract relevant data points
5. **Quality Assessment**: Evaluate study quality
6. **Synthesis**: Analyze and synthesize findings
7. **Report Generation**: Create PRISMA-compliant report

## Features

### Multi-Agent System

- **Prompt Enhancement Agent**: General-purpose query optimization
- **Deep Research Agent**: In-depth literature analysis (background job)
- **Aeromedical Risk Agent**: Specialized risk assessment (background job)
- **Aerospace Medicine RAG**: Query specialized knowledge base (background job)
- **PRISMA Agent System**: Multi-step systematic review workflow

### Background Jobs

Long-running tasks are handled asynchronously:

1. Job is submitted and ID is provided
2. Continue working while job processes
3. Check status with `/jobs` command
4. Results auto-saved to `exports/` directory

### Export Capabilities

- **Single Response**: Export last AI response
- **Full Conversation**: Export entire conversation history
- **PRISMA Reports**: Structured systematic review reports
- **Format**: Clean, well-formatted Markdown

## API Reference

### Core Classes

#### `AppConfig`
Configuration management for the application.

```python
class AppConfig:
    # API Keys
    OPENAI_API_KEY: str
    FLOWISE_API_KEY: str
    PPLX_API_KEY: str
    XAI_API_KEY: str
    
    # Model Settings
    OPENAI_MODEL: str = "gpt-4o"
    PPLX_MODEL: str = "llama-3.1-sonar-large-128k-online"
    XAI_MODEL: str = "grok-2-1212"
```

#### `ModeManager`
Handles mode switching and query routing.

```python
class ModeManager:
    def switch_mode(self, mode: str) -> bool
    def detect_optimal_mode(self, query: str) -> str
    def get_current_mode(self) -> str
```

#### `JobStore`
Manages background job processing.

```python
class JobStore:
    def create_job(self, job_type: str, query: str) -> str
    def get_job_status(self, job_id: str) -> Dict
    def get_all_jobs(self) -> List[Dict]
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

2. **API Key Errors**
   - Verify `.env` file exists and contains valid keys
   - Check API key permissions and quotas

3. **Flowise Connection Issues**
   - Verify Flowise API URL is correct
   - Check network connectivity
   - Ensure chatflow IDs are valid

4. **Unicode/Encoding Errors**
   - System automatically handles UTF-8 encoding
   - On Windows, may see console encoding messages (normal)

### Debug Mode

Enable debug logging by setting:
```env
LOG_LEVEL=DEBUG
```

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_mode_manager.py

# Run with coverage
python -m pytest tests/ --cov=src
```

### Code Style

The project uses:
- Black for code formatting
- Flake8 for linting
- Type hints throughout

### Project Structure

```
.
├── src/                    # Source code
│   ├── core_agents/        # Agent implementations
│   ├── custom_rich/        # Rich console stubs
│   ├── ui/                 # User interface components
│   └── *.py                # Core modules
├── tests/                  # Test suite
├── exports/                # Exported results
├── Docs/                   # Documentation
└── requirements.txt        # Dependencies
```

## Contributing

### Guidelines

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

### Code Standards

- Follow PEP 8 style guide
- Add type hints to all functions
- Document all public APIs
- Write comprehensive tests

### Bug Reports

When reporting bugs, please include:
- Python version
- Operating system
- Full error traceback
- Steps to reproduce

## License

[Specify your license here]

## Disclaimer

This is a research tool and is **not intended for operational use**. The information provided is not a substitute for professional medical or safety advice from qualified experts. All outputs must be independently verified.