# Aeromedical Evidence Review Framework

A sophisticated **multi-agent AI framework** designed specifically for **aeromedical professionals** to conduct **rapid evidence reviews** and **risk assessments** based on scientific research. This advanced CLI system integrates **OpenAI's O3 models** with **Flowise cloud services** to provide comprehensive, evidence-based analysis for aerospace medicine and aviation safety.

## 🚁 Purpose

This framework enables **flight surgeons**, **aeromedical professionals**, and **aviation safety specialists** to:
- Conduct rapid literature reviews on aeromedical topics
- Assess risk factors in aviation medicine
- Analyze physiological effects of flight environments
- Access specialized medical knowledge bases (PubMed, NASA HRP, clinical references)
- Generate evidence-based recommendations for aviation safety
- Export comprehensive reports and documentation

## 🔬 Core Capabilities

### 🧠 **Multi-Agent Architecture**
- **Intelligent Agent Orchestration**: Multiple specialized agents work together using OpenAI's agent pattern
- **Smart Mode Detection**: Automatically selects the most appropriate AI system based on query analysis
- **Seamless Handoffs**: Smooth transitions between different processing flows for optimal results
- **Specialized Knowledge Routing**: Directs queries to domain-specific knowledge bases and chatflows

### 🔬 **O3 Deep Research Flow**
- **o3-deep-research-2025-06-26**: Advanced reasoning model for in-depth scientific synthesis
- **o3 with Web Search**: Enhanced with real-time information retrieval and high-level reasoning
- **Intelligent Classification**: Automatically selects the best O3 model based on query complexity
- **Perfect for**: Complex aeromedical research, technology analysis, multi-step reasoning tasks

### 🌐 **Flowise Medical RAG Integration**
- **Specialized Medical Knowledge Bases**: PubMed, clinical textbooks, physiology databases
- **NASA Human Research Program**: Access to space medicine and aerospace physiology data
- **Aeromedical Risk Assessment**: Specialized chatflow for aviation safety analysis
- **RAG-Enhanced Processing**: Retrieval-Augmented Generation with domain expertise
- **Multiple Specialized Chatflows**:
  - `physiology_rag`: Human physiology and medical questions
  - `nasa_hrp`: NASA Human Research Program and space medicine
  - `deep_research`: Comprehensive research analysis
  - `agentic_rag`: Multi-agent RAG processing
  - `aeromedical_risk`: Aviation medicine risk assessment

### 📝 **Advanced Input & Export System**
- **Multiline Input Support**: Perfect for pasting entire research papers, abstracts, or articles
- **Smart Input Detection**: Automatically detects and handles pasted academic content
- **Multiple Input Modes**: Type `>>>` for multiline mode or paste directly
- **Comprehensive Export Options**: Export responses, conversations, and structured reports to markdown
- **Professional Documentation**: Well-formatted outputs suitable for sharing and archiving

## 🎯 How It Works

1. **Ask Your Question** - The system uses smart auto-detection to choose the best AI
2. **Enhanced Processing** - Your query is analyzed and enhanced for optimal results
3. **Intelligent Routing** - Automatically routed to O3 models or Flowise specialized chatflows
4. **Comprehensive Response** - Get evidence-based analysis with option to export as markdown

## 📋 Requirements

- **Python 3.8+**
- **OpenAI API key** (required for O3 models and prompt enhancement)
- **Flowise API access** (optional - for specialized medical knowledge bases)
- **Google Custom Search API** (optional - for O3 web search capabilities)

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd textappv2
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
   
   Create a `.env` file in the project root:
   
   ```bash
   # Required: OpenAI API Configuration
   OPENAI_API_KEY=your_openai_api_key_here
   
   # Optional: Flowise Cloud Configuration (for specialized medical knowledge)
   FLOWISE_API_URL=https://cloud.flowiseai.com
   FLOWISE_API_KEY=your_flowise_api_key_here
   
   # Optional: Google Custom Search (for O3 web search)
   SEARCH_API_KEY=your_google_search_api_key_here
   SEARCH_ENGINE_ID=your_search_engine_id_here
   
   # Optional: Application Settings
   LOG_LEVEL=INFO
   TIMEOUT=60
   MAX_RETRIES=3
   ```
   
   **⚠️ Security Note**: The `.env` file is already in `.gitignore` to prevent accidental commits.

## 🚀 Usage

**Start the application:**
```bash
python run_app.py
```

**Simple workflow - just ask your question:**
```
🎯 Ask your question (auto-detection enabled)
>>> What are the cardiovascular effects of microgravity on pilots?

🎯 Auto-detected optimal mode: 🌐 Flowise Medical RAG (confidence: 87%)
🌐 Processing your request with Flowise Medical Agent...
```

## 💡 Quick Commands & Navigation

### 🎯 **Smart Mode (Recommended)**
- Just ask your question - the system automatically detects the best AI
- **Auto-detection** routes to O3 Research, Flowise Medical RAG, or Aeromedical Risk Assessment

### 🛠️ **Manual Mode Selection**
- **`/o3`** - Switch to O3 Deep Research (complex analysis, latest research)
- **`/flowise`** - Switch to Flowise Medical RAG (clinical knowledge, PubMed)
- **`/aero`** - Switch to Aeromedical Risk Assessment (aviation medicine)
- **`/smart`** - Return to smart auto-detection mode

### 📖 **Help & Information**
- **`?`** - Show contextual help for current mode
- **`/modes`** - View all available processing modes
- **`/status`** - Show current system status
- **`/history`** - View conversation history

### 📄 **Export & Documentation**
- **`/export`** - Export latest response to markdown
- **`/save`** - Export full conversation to markdown
- **`/report`** - Create structured research report
- **`/exports`** - List all exported files

### 🔧 **Utility Commands**
- **`>>>`** - Enter multiline mode for large text blocks
- **`/clear`** - Clear conversation history
- **`/quit`** or **`/exit`** - Exit the application

## 📄 Markdown Export System

The framework includes comprehensive export functionality for professional documentation:

### 📊 **Export Options**
- **Single Response Export**: Save the latest AI response with your question
- **Full Conversation Export**: Save complete conversation history
- **Structured Research Report**: Create formatted reports with executive summaries
- **File Management**: All exports saved in `exports/` directory with timestamps

### 🎯 **Export Features**
- **Professional Formatting**: Clean, shareable markdown suitable for documentation
- **Metadata Tracking**: Processing mode, agent used, timestamps, and system information
- **Multiple Formats**: Response exports, conversation logs, structured reports
- **Easy Sharing**: Generated files can be imported into documentation systems

## 🏗️ Architecture

### **Multi-Agent System**
```
User Input → Smart Detection → Agent Orchestrator → Specialized Agents → Enhanced Response
```

### **Agent Types**
- **O3 Prompt Enhancer**: Analyzes and enhances prompts for O3 models
- **O3 Processor**: Routes to o3-deep-research or o3+web search
- **Flowise Enhancer**: Optimizes prompts for Flowise RAG systems
- **Flowise Processor**: Routes to specialized medical chatflows

### **Processing Flows**
1. **O3 Deep Research**: Complex analysis → o3-deep-research-2025-06-26
2. **O3 + Web Search**: Current information → o3 with real-time web search
3. **Flowise Medical RAG**: Clinical questions → Specialized knowledge bases
4. **Aeromedical Risk**: Aviation safety → Conservative risk assessment

## 🔬 Technical Features

### **Smart Classification System**
- **Pattern Recognition**: Analyzes query content using regex patterns
- **Confidence Scoring**: Calculates confidence for mode suggestions
- **Intelligent Routing**: Routes to optimal AI based on question type
- **Fallback Logic**: Graceful handling when confidence is low

### **Advanced Input Processing**
- **Multiline Support**: Handles large research papers and articles
- **Paste Detection**: Automatically detects and processes pasted content
- **Progress Feedback**: Visual indicators for long-running operations
- **Context Preservation**: Maintains conversation state across sessions

### **Robust Error Handling**
- **Retry Logic**: Automatic retry with exponential backoff
- **Graceful Degradation**: Continues working if optional services fail
- **Detailed Logging**: Comprehensive logs for debugging and audit trails
- **User-Friendly Messages**: Clear error explanations with recovery suggestions

## 🎓 Use Cases

### **For Flight Surgeons**
- Rapid medical literature review for flight clearance decisions
- Assessment of medications and their effects on flight safety
- Analysis of medical conditions in relation to aviation regulations
- Risk assessment for specific flight environments

### **For Aeromedical Researchers**
- Comprehensive literature reviews on aerospace physiology
- Analysis of NASA Human Research Program data
- Evidence synthesis for aviation safety recommendations
- Multi-source research compilation and analysis

### **For Aviation Safety Specialists**
- Medical risk assessment for different flight environments
- Analysis of incident reports and safety data
- Development of evidence-based safety protocols
- Regulatory compliance guidance

## 🔧 Configuration

### **Environment Variables**
- **OpenAI Settings**: Model selection, temperature, token limits
- **Flowise Integration**: Chatflow IDs, session management, streaming
- **Web Search**: Google Custom Search API configuration
- **Application**: Timeouts, retry logic, logging levels

### **Chatflow Configuration**
The system supports multiple specialized Flowise chatflows:
- Medical and physiology knowledge bases
- NASA Human Research Program data
- PubMed medical literature
- Clinical reference materials
- Aviation medicine specializations

## ⚠️ Important Disclaimers

### 🧪 **Research and Development Tool**
This framework is in **active development** and designed for **research purposes**. While sophisticated, it should be used as a supplementary tool for evidence review and analysis.

### 🚫 **Not for Critical Decision Making**
**This software should NOT be used for critical aviation safety or medical decisions without expert validation.** The framework is intended for:
- Research and development purposes
- Educational and training scenarios
- Preliminary literature review assistance
- Hypothesis generation and exploration

### 👨‍⚕️ **Expert Validation Required**
**All outputs must be validated by qualified aerospace medicine experts** before application in operational scenarios. The system:
- Requires expert review and interpretation of results
- Should supplement, not replace, professional judgment
- Must undergo validation in controlled environments
- Should not be relied upon for clinical decisions without oversight

### 🔬 **Continuous Development**
- AI models and knowledge bases are continuously evolving
- Results may contain inaccuracies or incomplete information
- The system has not been validated for critical applications
- Performance may vary across different query types and contexts

## 📊 Project Structure

```
textappv2/
├── src/
│   ├── main.py                    # Enhanced CLI with smart mode detection
│   ├── agents.py                  # Multi-agent orchestration system
│   ├── o3_agents.py              # O3 model integration and routing
│   ├── flowise_agents.py         # Flowise chatflow integration
│   ├── openai_enhanced_client.py # Enhanced OpenAI client with web search
│   ├── flowise_client.py         # Flowise API client with error handling
│   ├── markdown_exporter.py      # Professional documentation export
│   ├── multiline_input.py        # Advanced input handling
│   └── config.py                 # Configuration management
├── exports/                       # Markdown export directory
├── requirements.txt              # Python dependencies
├── run_app.py                    # Application entry point
├── README.md                     # This file
└── IMPROVEMENTS.md               # Recent enhancements documentation
```

## 🤝 Contributing

Contributions are welcome from the aeromedical and aviation safety communities. Areas of particular interest:
- Additional specialized knowledge bases
- Enhanced risk assessment algorithms
- Integration with aviation medical databases
- Improvements to evidence synthesis capabilities

## 📄 License

MIT License - See LICENSE file for details.

## 🆘 Support

For technical support or questions about the framework:
- Check the logs in `prompt_enhancer.log` for detailed error information
- Refer to `IMPROVEMENTS.md` for recent enhancements and changes
- Ensure all required environment variables are properly configured

**⚠️ For questions about the research nature of this project or its limitations, please consult with qualified aerospace medicine professionals.**

---

*This framework represents ongoing research in AI-assisted evidence review for aerospace medicine. It is designed to augment, not replace, expert medical and safety judgment.* 