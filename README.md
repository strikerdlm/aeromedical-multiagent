# Advanced Aeromedical Evidence Review System

A sophisticated **multi-agent AI framework** designed for **aeromedical professionals** to conduct **comprehensive evidence reviews**, **systematic reviews**, and **risk assessments** based on scientific research. This advanced system integrates **OpenAI's latest O3 models**, **Perplexity deep research**, **Grok's advanced reasoning**, and **Flowise specialized knowledge bases** to provide evidence-based analysis for aerospace medicine and aviation safety.

## 🚀 Overview

The Advanced Aeromedical Evidence Review System is a cutting-edge CLI application that combines multiple AI agents to provide comprehensive research and analysis capabilities. It features **smart mode detection**, **automated PRISMA-compliant systematic reviews**, and **specialized knowledge routing** to deliver professional-grade research outputs.

### 🌟 Key Features

- **🔬 Multi-Agent Architecture**: Orchestrated agents using OpenAI Agents SDK
- **📊 PRISMA Systematic Reviews**: Automated PRISMA 2020-compliant systematic reviews
- **🎯 Smart Mode Detection**: Automatically selects optimal AI based on query analysis
- **🌐 Specialized Knowledge Bases**: Medical RAG, NASA HRP, PubMed integration
- **📝 Professional Export System**: Markdown reports, structured documentation
- **🚁 Aeromedical Risk Assessment**: Aviation medicine-specific analysis
- **💡 Enhanced CLI Interface**: Intuitive navigation and multiline input support

## 🎯 Target Users

### **Flight Surgeons & Aeromedical Professionals**
- Rapid medical literature review for flight clearance decisions
- Assessment of medications and their effects on flight safety
- Analysis of medical conditions in relation to aviation regulations
- Risk assessment for specific flight environments

### **Aerospace Medicine Researchers**
- Comprehensive literature reviews on aerospace physiology
- Analysis of NASA Human Research Program data
- Evidence synthesis for aviation safety recommendations
- Multi-source research compilation and analysis

### **Aviation Safety Specialists**
- Medical risk assessment for different flight environments
- Analysis of incident reports and safety data
- Development of evidence-based safety protocols
- Regulatory compliance guidance

## 🔬 Core Capabilities

### 📊 **PRISMA Systematic Review Engine**
A comprehensive **multi-agent workflow** that produces **publication-ready systematic reviews**:

- **🔍 Literature Search Agent**: Multi-database search across PubMed, Google Scholar, Cochrane Library
- **📋 Study Reviewer Agent**: Automated screening, quality assessment, and bias detection
- **✍️ Review Writer Agent**: Generates 8,000-10,000 word PRISMA-compliant documents
- **✅ Validation Agent**: Ensures compliance with PRISMA 2020 guidelines
- **📈 Meta-Analysis Support**: Statistical analysis and evidence synthesis
- **📚 Citation Management**: ≥50 peer-reviewed citations in APA format

**AI Models Used**: O3 Deep Research (o3-deep-research-2025-06-26), O4 Mini Fallback (o4-mini-deep-research-2025-06-26), Perplexity Deep Research (sonar-deep-research), Grok Advanced Reasoning (grok-beta), Flowise (specialized knowledge)

### 🧠 **Smart Mode Detection System**
Intelligent **automatic routing** based on query analysis:

- **Pattern Recognition**: Analyzes query content using advanced regex patterns
- **Confidence Scoring**: Calculates confidence scores for optimal mode selection
- **Domain Classification**: Routes to specialized knowledge bases
- **Fallback Logic**: Graceful handling when confidence is low
- **Learning System**: Improves routing based on user interactions

**Detection Categories**:
- Medical/Clinical queries → Flowise Medical RAG
- Complex research → O3 Deep Research
- Aviation safety → Aeromedical Risk Assessment
- Systematic reviews → PRISMA workflow

### 🔬 **O3 Deep Research Flow**
Advanced reasoning with **OpenAI's O3 models**:

- **O3 with High Reasoning**: Complex analysis and multi-step reasoning
- **O3 + Web Search**: Real-time information retrieval with advanced synthesis
- **Intelligent Classification**: Automatically selects optimal O3 configuration
- **Context Preservation**: Maintains conversation state across complex analyses

**Perfect for**: Complex aeromedical research, technology analysis, comparative studies, regulatory analysis

### 🌐 **Flowise Medical RAG Integration**
Specialized **knowledge bases** with domain expertise:

- **Medical Literature**: PubMed, clinical textbooks, physiology databases
- **NASA Human Research Program**: Space medicine and aerospace physiology data
- **Aviation Medicine**: Flight safety, medical certification, regulations
- **Multi-Agent RAG**: Complex retrieval with multiple knowledge sources

**Specialized Chatflows**:
- `physiology_rag`: Human physiology and medical questions
- `nasa_hrp`: NASA Human Research Program and space medicine
- `deep_research`: Comprehensive research synthesis
- `agentic_rag`: Multi-agent RAG processing
- `aeromedical_risk`: Aviation medicine risk assessment

### 🚁 **Aeromedical Risk Assessment**
Specialized **aviation medicine analysis**:

- **Conservative Risk Evaluation**: Safety-first approach to medical assessments
- **Regulatory Compliance**: Integration with aviation medical standards
- **Flight Environment Analysis**: Altitude, G-forces, spatial disorientation
- **Medication Impact Assessment**: Drug effects on flight performance
- **Physiological Stress Analysis**: Cardiovascular, respiratory, neurological impacts

## 🛠️ Installation & Setup

### **System Requirements**
- **Python 3.8+**
- **OpenAI API key** (required for O3 models)
- **Perplexity API key** (required for PRISMA feature)
- **Grok (XAI) API key** (required for PRISMA feature)
- **Flowise API access** (optional - for specialized medical knowledge)

### **Installation Steps**

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd textappv2
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration:**
   Create a `.env` file in the project root:
   ```bash
   # Required: OpenAI API Configuration
   OPENAI_API_KEY=your_openai_api_key_here

   # Required for PRISMA Feature
   PPLX_API_KEY=your_perplexity_api_key_here
   XAI_API_KEY=your_grok_xai_api_key_here

   # Optional: Flowise Cloud Configuration
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

4. **Launch the application:**
   ```bash
   python run_app.py
   ```

## 🚀 Usage Guide

### **Getting Started**
The system features an **intuitive CLI interface** with smart auto-detection:

1. **Start the application** and you'll see the welcome screen
2. **Ask your question directly** - the system automatically detects the best processing method
3. **Review the response** and export if needed
4. **Use commands** for advanced navigation and control

### **Smart Mode (Recommended)**
Just ask your question! The system automatically routes to:
- **Medical/Aviation Questions** → Flowise Medical RAG
- **Complex Research** → O3 Deep Research
- **Risk Assessment** → Aeromedical Risk Assessment
- **Systematic Reviews** → PRISMA workflow

### **Manual Mode Selection**
Force specific processing modes:
- **`/prisma`** - PRISMA Systematic Review workflow
- **`/o3`** - O3 Deep Research (complex analysis, latest research)
- **`/flowise`** - Flowise Medical RAG (clinical knowledge, PubMed)
- **`/deep`** - DeepResearch RAG (comprehensive synthesis)
- **`/aero`** - Aeromedical Risk Assessment (aviation medicine)
- **`/smart`** - Return to smart auto-detection mode

### **Navigation & Help**
- **`?`** - Show contextual help for current mode
- **`/modes`** - View all available processing modes
- **`/status`** - Show current system status
- **`/history`** - View conversation history
- **`/prisma-status`** - Check PRISMA system status and API connectivity

### **Advanced Input Features**
- **Multiline Mode**: Type `>>>` for large text blocks
- **Paste Detection**: Automatically handles pasted academic content
- **Context Preservation**: Maintains conversation state across sessions
- **Progress Feedback**: Visual indicators for long-running operations

### **Export & Documentation**
- **`/export`** - Export latest response to markdown
- **`/save`** - Export full conversation to markdown
- **`/report`** - Create structured research report
- **`/exports`** - List all exported files

### **Utility Commands**
- **`/clear`** - Clear conversation history
- **`/settings`** - View/modify user preferences
- **`/quit`** or **`/exit`** - Exit the application

## 📄 Professional Export System

### **Export Options**
- **Single Response Export**: Latest AI response with metadata
- **Full Conversation Export**: Complete session history
- **Structured Research Report**: Formatted reports with executive summaries
- **PRISMA Review Export**: Publication-ready systematic reviews

### **Export Features**
- **Professional Formatting**: Clean, shareable markdown
- **Metadata Tracking**: Processing mode, AI models used, timestamps
- **Citation Management**: Proper academic citation formatting
- **File Organization**: Timestamped files in organized directory structure

### **Export Formats**
- **Markdown (.md)**: Compatible with documentation systems
- **Structured Reports**: Executive summaries, findings, recommendations
- **Research Documentation**: Academic-style reports with proper citations
- **PRISMA Compliance**: Systematic reviews following PRISMA 2020 guidelines

## 🏗️ Technical Architecture

### **Multi-Agent System Design**
```
User Input → Smart Detection → Agent Orchestrator → Specialized Agents → Response Generation
     ↓              ↓                    ↓                    ↓               ↓
Query Analysis → Mode Selection → Agent Routing → Processing → Export Options
```

### **Agent Architecture**
- **LeadResearcher Agent**: Main orchestrator with explicit planning
- **SearchAgent**: Parallel literature search with confidence thresholds
- **AnalysisAgent**: Quality assessment and bias detection
- **CitationAgent**: Ensures all claims are properly source-attributed
- **ValidationAgent**: PRISMA compliance and quality assurance

### **AI Model Integration**
- **O3 Deep Research (o3-deep-research-2025-06-26)**: Primary synthesis and analysis with high reasoning effort
- **O4 Mini Fallback (o4-mini-deep-research-2025-06-26)**: Fallback model for synthesis and analysis 
- **Perplexity Deep Research (sonar-deep-research)**: Literature search and data extraction
- **Grok Advanced Reasoning (grok-beta)**: Critical analysis and bias detection
- **Flowise Specialized RAG**: Domain-specific knowledge retrieval

### **Processing Flows**
1. **PRISMA Systematic Review**: Multi-agent workflow (Search → Review → Write → Validate)
2. **O3 Deep Research**: Complex analysis with high reasoning effort
3. **O3 + Web Search**: Real-time information with advanced synthesis
4. **Flowise Medical RAG**: Specialized knowledge base queries
5. **Aeromedical Risk Assessment**: Aviation medicine-specific analysis

### **Smart Classification System**
- **Pattern Recognition**: Advanced regex analysis of query content
- **Confidence Scoring**: Statistical confidence for mode suggestions
- **Domain Expertise**: Medical, aviation, research pattern detection
- **Adaptive Learning**: Improves routing based on user feedback

## 📊 Project Structure

```
textappv2/
├── src/
│   ├── main.py                         # Enhanced CLI with smart mode detection
│   ├── agents.py                       # Multi-agent orchestration (OpenAI Agents SDK)
│   ├── prisma_orchestrator.py          # PRISMA workflow orchestration
│   ├── prisma_agents.py                # PRISMA agent definitions and tools
│   ├── enhanced_prisma_orchestrator.py # Enhanced orchestrator-worker pattern
│   ├── enhanced_prisma_integration.py  # Integration bridge for compatibility
│   ├── o3_agents.py                    # O3 model integration and routing
│   ├── flowise_agents.py               # Flowise chatflow integration
│   ├── perplexity_client.py            # Perplexity API client
│   ├── grok_client.py                  # Grok (XAI) API client
│   ├── openai_enhanced_client.py       # Enhanced OpenAI client with web search
│   ├── flowise_client.py               # Flowise API client with error handling
│   ├── markdown_exporter.py            # Professional documentation export
│   ├── multiline_input.py              # Advanced input handling
│   └── config.py                       # Configuration management
├── exports/                            # Markdown export directory
├── PRISMA/                             # PRISMA documentation and checklists
├── requirements.txt                    # Python dependencies
├── run_app.py                          # Application entry point
├── README.md                           # This file
├── PRISMA_FEATURE.md                   # Detailed PRISMA documentation
├── ENHANCED_PRISMA_SYSTEM.md           # Enhanced system architecture
├── IMPROVEMENTS.md                     # Recent enhancements documentation
└── OPENAI_AGENTS_FIXES.md              # OpenAI agents integration fixes
```

## 🔧 Advanced Configuration

### **Environment Variables**
- **OpenAI Settings**: Model selection, temperature, reasoning effort
- **Flowise Integration**: Chatflow IDs, session management, streaming
- **PRISMA Configuration**: Multi-model settings, validation thresholds
- **Web Search**: Google Custom Search API configuration
- **Application Settings**: Timeouts, retry logic, logging levels

### **Model Configuration**
```python
# Enhanced model configurations
ENHANCED_MODELS = {
         "o3_high_reasoning": {
         "model_name": "o3-deep-research-2025-06-26",
         "temperature": 0.2,
         "reasoning_effort": "high"
     },
     "o4_mini_fallback": {
         "model_name": "o4-mini-deep-research-2025-06-26",
         "temperature": 0.3,
         "reasoning_effort": "high"
     },
         "perplexity_deep_research": {
         "model_name": "sonar-deep-research",
         "temperature": 0.2
     },
    "grok_advanced": {
        "model_name": "grok-4",
        "temperature": 0.3
    }
}
```

### **PRISMA Configuration**
- **Target Word Count**: 8,000-10,000 words
- **Citation Requirements**: ≥50 peer-reviewed sources
- **Validation Thresholds**: PRISMA 2020 compliance (≥80% checklist)
- **Parallel Processing**: Up to 5 concurrent agents
- **Quality Assurance**: Multi-stage validation and review

## 🔬 Research & Development Features

### **Experimental Capabilities**
- **Enhanced Orchestrator-Worker Pattern**: Fusion of Anthropic's orchestrator philosophy with OpenAI Agents SDK
- **Parallel SubAgent Processing**: Multiple agents working simultaneously
- **External Memory System**: Redis-based state management
- **Production Guardrails**: Comprehensive error handling and retry logic

### **Advanced Workflows**
- **Multi-Phase Processing**: Planning → Search → Analysis → Writing → Validation
- **Confidence-Based Routing**: Adaptive agent selection based on query complexity
- **Citation Validation**: Automated source verification and attribution
- **Quality Scoring**: Automated assessment of output quality

## ⚠️ Important Disclaimers

### 🧪 **Research and Development Tool**
This framework is designed for **research purposes** and should be used as a **supplementary tool** for evidence review and analysis.

### 🚫 **Not for Critical Decision Making**
**This software should NOT be used for critical aviation safety or medical decisions without expert validation.**

### 👨‍⚕️ **Expert Validation Required**
**All outputs must be validated by qualified aerospace medicine experts** before application in operational scenarios.

### 🔬 **Continuous Development**
- AI models and knowledge bases are continuously evolving
- Results may contain inaccuracies or incomplete information
- The system has not been validated for critical applications
- Performance may vary across different query types and contexts

## 🎓 Example Use Cases

### **Clinical Scenario: Medication Assessment**
```
Query: "Assess the safety of selective serotonin reuptake inhibitors (SSRIs) for commercial pilots"
→ Auto-routes to Aeromedical Risk Assessment
→ Provides comprehensive risk analysis with aviation medical standards
→ Includes regulatory compliance information
```

### **Research Scenario: Systematic Review**
```
Query: "Effectiveness of counterpressure suits in preventing G-induced loss of consciousness"
→ Auto-routes to PRISMA workflow
→ Conducts comprehensive literature search
→ Generates publication-ready systematic review
```

### **Complex Analysis: Physiological Effects**
```
Query: "Compare cardiovascular adaptations between short-duration and long-duration spaceflight"
→ Auto-routes to O3 Deep Research
→ Provides comprehensive comparative analysis
→ Includes latest research and web sources
```

## 🤝 Contributing

Contributions are welcome from the aeromedical and aviation safety communities:

- **Knowledge Base Expansion**: Additional specialized databases
- **Agent Enhancement**: Improved risk assessment algorithms
- **Integration**: Aviation medical database connections
- **Validation**: Quality assurance and testing improvements

## 📞 Support

For technical support:
- Check `prompt_enhancer.log` for detailed error information
- Refer to documentation in `PRISMA_FEATURE.md` and `IMPROVEMENTS.md`
- Ensure all required environment variables are configured
- Verify API key permissions and quotas

## 📄 License

MIT License - See LICENSE file for details.

---

*This framework represents ongoing research in AI-assisted evidence review for aerospace medicine. It is designed to augment, not replace, expert medical and safety judgment.*

**⚠️ Always consult with qualified aerospace medicine professionals for critical decisions.** 