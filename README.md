# Aeromedical Evidence Review Framework

A sophisticated **multi-agent framework** designed specifically for **aeromedical staff** to conduct **rapid evidence reviews** based on scientific research. This CLI-based system integrates **deep research methods** using **OpenAI API** and **Flowise cloud services** to provide comprehensive, evidence-based analysis for aerospace medicine and aviation safety.

## 🚁 Purpose

This framework enables **flight surgeons**, **aeromedical professionals**, and **aviation safety specialists** to:
- Conduct rapid literature reviews on aeromedical topics
- Assess risk factors in aviation medicine
- Analyze physiological effects of flight environments
- Review NASA Human Research Program data
- Access specialized medical knowledge bases
- Generate evidence-based recommendations for aviation safety

## 🔬 Core Capabilities

### 🧠 **Multi-Agent Architecture**
- **Intelligent Agent Orchestration**: Multiple specialized agents work together to analyze and enhance queries
- **Context-Aware Processing**: Agents automatically select the most appropriate AI system based on query type
- **Seamless Handoffs**: Smooth transitions between different processing flows for optimal results
- **Specialized Knowledge Routing**: Directs queries to domain-specific knowledge bases

### 🔬 **O3 Deep Research Flow**
- **o3-deep-research-2025-06-26**: Optimized for in-depth scientific synthesis and research analysis
- **o3 with Web Search**: Enhanced with real-time information retrieval and high-level reasoning
- **Intelligent Classification**: Automatically selects the best O3 model based on query complexity
- **Perfect for**: Complex aeromedical research, technology analysis, multi-step reasoning tasks

### 🌐 **Flowise Cloud Integration**
- **Specialized Medical Knowledge Bases**: PubMed, clinical textbooks, physiology databases
- **NASA Human Research Program**: Access to space medicine and aerospace physiology data
- **Aeromedical Risk Assessment**: Specialized chatflow for aviation safety analysis
- **RAG-Enhanced Processing**: Retrieval-Augmented Generation with domain expertise
- **Multiple Specialized Chatflows**:
  - `physiology_rag`: Human physiology and medical questions
  - `nasa_hrp`: NASA Human Research Program and space medicine
  - `deep_research`: Comprehensive research analysis
  - `agentic_rag`: Multi-agent RAG processing
  - `pubmed`: Medical literature search
  - `aeromedical_risk`: Aviation medicine risk assessment
  - `clinical_textbooks`: Clinical reference materials
  - `flight_surgeon`: Aviation medicine specialist knowledge

### 📝 **Advanced Multiline Input Support**
- **Paste Large Research Papers**: Perfect for pasting entire abstracts, papers, or articles as context
- **Smart Input Detection**: Automatically detects and handles pasted academic content
- **Multiple Input Modes**: Type `>>>` for multiline mode or paste directly
- **Progress Tracking**: Visual feedback for large inputs with line counts
- **Intelligent Formatting**: Automatic handling of academic papers, DOIs, PMIDs
- **Context Preservation**: Maintains formatting and structure of pasted content

## 🎯 How It Works

1. **Choose Your Processing Flow** from the main menu based on your research needs
2. **Enter Your Research Question** - single line, multiline, or paste large context blocks
3. **Get Comprehensive Evidence-Based Results** from the most appropriate AI system

**The system provides granular control over which AI system processes your requests AND can easily handle extensive research context!**

## 📋 Requirements

- Python 3.8+
- OpenAI API key (required for both flows)
- Flowise API access (required for specialized medical knowledge bases)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd textappv2
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Required for both flows
export OPENAI_API_KEY="your-openai-api-key"

# Required for Flowise cloud integration
export FLOWISE_API_URL="https://cloud.flowiseai.com"
export FLOWISE_API_KEY="your-flowise-api-key"
```

## 🚀 Usage

Run the application:
```bash
python -m src.main
```

### Main Menu Options

1. **O3 Deep Research Flow** - For complex aeromedical research and analysis
2. **Flowise API Flow** - For medical questions and specialized domain expertise
3. **DeepResearch Flowise** - Comprehensive research with Flowise deep knowledge
4. **Aeromedical Risk** - Aerospace medicine risk assessment and analysis
5. **Help & Info** - Learn more about each processing flow
6. **Exit** - Quit the application

### Commands

- **Your research question** - Enter any request for evidence review and analysis
- **>>>** - Enter multiline mode for large text blocks (research papers, articles)
- **/menu** - Return to the main processing flow selection menu
- **/help** - Show help information
- **/status** - Show current agent status
- **/history** - Show conversation history
- **/clear** - Clear conversation history
- **/quit** or **/exit** - Exit the application

### 📝 Multiline Input Features

#### **How to Use Multiline Input:**

1. **Type `>>>`** - Enter dedicated multiline mode with instructions
2. **Paste directly** - Large text blocks are automatically detected
3. **Type `MULTILINE`** - Alternative way to enter multiline mode
4. **Type `END`** - Finish multiline input (or use Ctrl+D/Ctrl+Z)

#### **Perfect for:**
- **Research Papers**: Paste entire abstracts, papers, or articles as context
- **Large Data Blocks**: CSV data, JSON, XML, or other structured data
- **Multi-paragraph Questions**: Complex questions with extensive background
- **Code Snippets**: Programming code, configuration files, logs
- **Technical Documentation**: Manuals, specifications, requirements

#### **Smart Features:**
- **Automatic Detection**: System detects pasted academic content, DOIs, PMIDs
- **Progress Tracking**: Shows line counts for large inputs (every 10 lines)
- **Input Summary**: Displays statistics (lines, characters, words) after input
- **Preview Generation**: Shows formatted previews of large content in history
- **Context Preservation**: Maintains original formatting and structure

#### **Example Workflow:**
```
🔬 O3 MODE - Enter your prompt
Type your prompt, or use '>>>' for multiline mode:
>>> >>>

📝 Multiline Input Mode
Enter your text (press Ctrl+D or type 'END' on a new line to finish):
>>> [PASTE YOUR RESEARCH PAPER HERE]
... [ADDITIONAL LINES]
... END

✅ Input Received
- Lines: 45
- Characters: 2,847
- Words: 423

🤔 Processing your request (45 lines, 423 words) with O3 Prompt Enhancer...
```

## 🔬 O3 Deep Research Flow

**When to use:**
- Complex aeromedical or scientific questions
- Multi-step reasoning and analysis
- Current events (uses web search)
- General knowledge with deep analysis
- Technology comparisons and explanations
- **Large research papers as context**

**How it works:**
1. **O3 Prompt Enhancer** - Analyzes and enhances your prompt for O3 models
2. **O3 Processor** - Routes to either:
   - `o3-deep-research-2025-06-26` for complex analysis
   - `o3 with web search` for current information

**Example questions:**
- "What are the cardiovascular effects of microgravity on long-duration spaceflight?"
- "Analyze the latest developments in aviation medicine and their safety implications"
- "How does hypoxia affect pilot performance at high altitudes?"
- **[Paste research paper] + "Summarize the key findings and clinical implications for aviation medicine"**

## 🌐 Flowise API Flow

**When to use:**
- Medical and physiology questions
- NASA and space medicine research
- PubMed literature searches
- Clinical reference needs
- Aviation medicine questions
- **Medical literature with extensive context**

**How it works:**
1. **Flowise Prompt Enhancer** - Optimizes your prompt for RAG systems
2. **Flowise Processor** - Routes to specialized chatflows:
   - `physiology_rag` - Human physiology and medical questions
   - `nasa_hrp` - NASA Human Research Program
   - `pubmed` - Medical literature search
   - `deep_research` - Comprehensive research analysis
   - `agentic_rag` - Multi-agent RAG processing
   - `aeromedical_risk` - Aviation medicine risk assessment
   - `flight_surgeon` - Aviation medicine specialist knowledge

**Example questions:**
- "What are the cardiovascular effects of microgravity?"
- "Find recent research on diabetes treatment protocols in aviation"
- "Explain the physiological changes during space flight"
- **[Paste medical study] + "Analyze the clinical implications for flight safety"**

## 🚁 Aeromedical Risk Assessment

**Specialized capability for aviation medicine:**
- **Risk Factor Analysis**: Comprehensive assessment of medical conditions for flight
- **Regulatory Compliance**: Integration with aviation medical standards
- **Evidence-Based Recommendations**: Data-driven safety assessments
- **Multi-System Evaluation**: Cardiovascular, neurological, psychological factors

## 🏗️ Architecture

### Project Structure

```
textappv2/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Main application with menu system
│   ├── config.py                  # Configuration management
│   ├── agents.py                  # Base agent orchestration
│   ├── o3_agents.py              # O3 Deep Research flow agents
│   ├── flowise_agents.py         # Flowise API flow agents
│   ├── multiline_input.py        # Multiline input handler
│   ├── openai_enhanced_client.py # Enhanced OpenAI client
│   └── flowise_client.py         # Flowise API client
├── requirements.txt
├── run_app.py
└── README.md
```

### Agent Flow Architecture

The system uses a sophisticated multi-agent architecture:

1. **Agent Orchestrator**: Manages the overall flow and agent handoffs
2. **Prompt Enhancers**: Analyze and enhance user queries for optimal processing
3. **Specialized Processors**: Route queries to appropriate AI systems
4. **Knowledge Base Integrators**: Connect to specialized medical and research databases

### Key Features

- **Intelligent Routing**: Automatically selects the best AI system based on query type
- **Context Preservation**: Maintains conversation history and context across sessions
- **Error Handling**: Robust error handling with retry logic and graceful degradation
- **Streaming Support**: Real-time response streaming for better user experience
- **Logging**: Comprehensive logging for debugging and audit trails

## 🔧 Configuration

The system supports extensive configuration through environment variables:

- **OpenAI API**: Model selection, temperature, token limits
- **Flowise Integration**: Chatflow IDs, session management, streaming options
- **Application Settings**: Timeouts, retry logic, logging levels

## 📊 Use Cases

### For Flight Surgeons:
- Rapid review of medical literature for flight clearance decisions
- Assessment of new medications and their effects on flight safety
- Analysis of medical conditions in relation to aviation regulations

### For Aeromedical Researchers:
- Comprehensive literature reviews on aerospace physiology
- Analysis of NASA Human Research Program data
- Evidence synthesis for aviation safety recommendations

### For Aviation Safety Specialists:
- Risk assessment of medical conditions for different flight environments
- Analysis of incident reports and safety data
- Development of evidence-based safety protocols

## 🤝 Contributing

This framework is designed for the aeromedical community. Contributions are welcome, especially:
- Additional specialized knowledge bases
- Enhanced aeromedical risk assessment algorithms
- Integration with aviation medical databases
- Improvements to evidence synthesis capabilities

## ⚠️ Important Disclaimers

### 🧪 **Experimental Research Project**
This framework is currently in the **research and development phase**. It is designed as an experimental tool for exploring the potential of AI-assisted evidence review in aeromedical contexts.

### 🚫 **Not for Critical Decision Making**
**This software should NOT be used for critical decision-making scenarios in aviation or medical practice.** The framework is intended for:
- Research and development purposes
- Educational and training scenarios
- Preliminary literature review assistance
- Hypothesis generation and exploration

### 👨‍⚕️ **Expert Validation Required**
**All outputs from this framework must be validated by qualified aerospace medicine experts before any application in real-world scenarios.** The system:
- Requires expert review and interpretation of all results
- Should be used as a supplementary tool, not a replacement for professional judgment
- Must undergo thorough testing and validation in controlled environments
- Should not be relied upon for clinical or aviation safety decisions without expert oversight

### 🔬 **Research Phase Limitations**
- The AI models and knowledge bases are continuously evolving
- Results may contain inaccuracies or incomplete information
- The system has not been validated for clinical or aviation safety applications
- Performance may vary across different types of queries and contexts

## 📄 License

MIT License

Copyright (c) 2024 Aeromedical Evidence Review Framework

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## 🆘 Support

For support with aeromedical evidence reviews or technical issues, please refer to the documentation or contact the development team.

**⚠️ For questions about the experimental nature of this project or its limitations, please consult with qualified aerospace medicine professionals.** 