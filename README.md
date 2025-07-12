# Advanced Aeromedical Evidence Review System

A multi-agent AI framework for aeromedical research, systematic reviews, and risk assessments.

## Key Features

- **🔬 Multi-Agent Architecture**: Uses multiple AI agents to perform complex research tasks.
- **📊 PRISMA Systematic Reviews**: Automatically generates PRISMA 2020-compliant systematic reviews.
- **🎯 Smart Mode Detection**: Analyzes your question to select the best AI agent for the job.
- **🌐 Specialized Knowledge**: Integrates with medical and aerospace knowledge bases.
- **📝 Professional Export**: Exports conversations and research to clean Markdown files.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd textappv2
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up your environment:**
    Create a `.env` file in the root of the project and add your API keys. At a minimum, you need an `OPENAI_API_KEY`.

    ```env
    # Required for core functionality
    OPENAI_API_KEY="your_openai_api_key_here"

    # Required for the PRISMA systematic review feature
    PPLX_API_KEY="your_perplexity_api_key_here"
    XAI_API_KEY="your_grok_xai_api_key_here"
    
    # Required for specialized medical knowledge bases
    FLOWISE_API_KEY="your_flowise_api_key_here"
    ```

4.  **Run the application:**
    ```bash
    python src/main.py
    ```

## How to Use

### Quick Start

Simply start the application and ask your question. The system will automatically choose the best mode to answer it.

```
$ python src/main.py
🎯 Ask your question (auto-detection enabled)
>>> What are the effects of hypoxia on pilot performance?
```

### Commands

Here are some of the most common commands. Type `?` in the app for a full list.

| Command        | Description                               |
|----------------|-------------------------------------------|
| `?` or `/help` | Show the help message.                    |
| `/modes`       | List all available processing modes.      |
| `/history`     | Show the conversation history.            |
| `/export`      | Export the last response to a file.       |
| `/clear`       | Clear the conversation history.           |
| `/quit`        | Exit the application.                     |

### Processing Modes

You can manually switch to a specific mode using commands like `/prompt`, `/prisma`, etc.

-   **Smart Mode (default)**: Automatically selects the best mode for your query.
-   **Prompt Research (`/prompt`)**: For general and complex research questions.
-   **Deep Research (`/deep`)**: For comprehensive research using specialized models.
-   **Aeromedical Risk (`/aero`)**: For aviation medicine and risk assessment questions.
-   **Aerospace Medicine RAG (`/aerospace`)**: To query scientific articles and textbooks.
-   **PRISMA (`/prisma`)**: To start a full systematic review workflow.

## ⚠️ Disclaimer

This is a research tool and is **not intended for operational use**. The information provided is not a substitute for professional medical or safety advice. All outputs must be independently verified by a qualified expert. 