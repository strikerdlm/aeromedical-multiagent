# Multi-Agent Prompt Enhancement System

A sophisticated prompt enhancement system with **two specialized processing flows** and **comprehensive multiline input support** for granular control over AI model selection and processing.

## 🚀 Features

### 🔬 **O3 Deep Research Flow**
- **o3-deep-research-2025-06-26**: Optimized for in-depth synthesis and research
- **o3 with Web Search**: Enhanced with real-time information and high reasoning
- **Intelligent Classification**: Automatically selects the best O3 model
- **Perfect for**: Scientific research, technology analysis, complex reasoning

### 🌐 **Flowise API Flow**  
- **Specialized Knowledge Bases**: Medical, NASA, PubMed, Clinical resources
- **RAG-Enhanced Processing**: Retrieval-Augmented Generation with domain expertise
- **Multiple Chatflows**: physiology_rag, nasa_hrp, deep_research, agentic_rag, pubmed
- **Perfect for**: Medical questions, research literature, specialized domain knowledge

### 📝 **Advanced Multiline Input Support**
- **Paste Large Text Blocks**: Perfect for research papers, articles, and extensive context
- **Smart Input Detection**: Automatically detects and handles pasted content
- **Multiple Input Modes**: Type `>>>` for multiline mode or paste directly
- **Progress Tracking**: Visual feedback for large inputs with line counts
- **Intelligent Formatting**: Automatic handling of academic papers, code, and data
- **Context Preservation**: Maintains formatting and structure of pasted content

## 🎯 How It Works

1. **Choose Your Processing Flow** from the main menu
2. **Enter Your Question** - single line, multiline, or paste large context blocks
3. **Get Comprehensive Results** from the most appropriate AI system

**You now have granular control over which AI system processes your requests AND can easily provide extensive context!**

## 📋 Requirements

- Python 3.8+
- OpenAI API key (required for both flows)
- Flowise API access (required for Flowise flow only)

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

# Required only for Flowise flow
export FLOWISE_API_URL="https://cloud.flowiseai.com"
export FLOWISE_API_KEY="your-flowise-api-key"
```

## 🚀 Usage

Run the application:
```bash
python -m src.main
```

### Main Menu Options

1. **O3 Deep Research Flow** - For scientific research and complex analysis
2. **Flowise API Flow** - For medical questions and domain expertise
3. **Help & Info** - Learn more about each processing flow
4. **Exit** - Quit the application

### Commands

- **Your question** - Enter any request for enhancement and processing
- **>>>** - Enter multiline mode for large text blocks
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
- Complex scientific or technical questions
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
- "Explain quantum computing and its applications in cryptography"
- "What are the latest developments in artificial intelligence?"
- "How does photosynthesis work at the molecular level?"
- **[Paste research paper] + "Summarize the key findings and methodology"**

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

**Example questions:**
- "What are the cardiovascular effects of microgravity?"
- "Find recent research on diabetes treatment protocols"
- "Explain the physiological changes during space flight"
- **[Paste medical study] + "Analyze the clinical implications"**

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

#### O3 Flow:
```
User Input (Multiline) → O3 Prompt Enhancer → O3 Processor → OpenAI o3 Models
```

#### Flowise Flow:
```
User Input (Multiline) → Flowise Prompt Enhancer → Flowise Processor → Flowise Chatflows
```

#### Multiline Input Flow:
```
User Types >>> → Multiline Mode → Paste/Type Content → END → Process with Selected Flow
```

## ⚙️ Configuration

### Environment Variables

```bash
# OpenAI Configuration (required for both flows)
OPENAI_API_KEY="your-openai-api-key"
OPENAI_MODEL="gpt-4o-mini"  # Default model for enhancement

# Flowise Configuration (required for Flowise flow)
FLOWISE_API_URL="https://cloud.flowiseai.com"
FLOWISE_API_KEY="your-flowise-api-key"

# Chatflow IDs (optional - defaults provided)
CHATFLOW_PHYSIOLOGY_RAG="your-physiology-rag-id"
CHATFLOW_NASA_HRP="your-nasa-hrp-id"
CHATFLOW_DEEP_RESEARCH="your-deep-research-id"
# ... other chatflow IDs
```

### Logging Configuration

```bash
LOG_LEVEL="INFO"  # DEBUG, INFO, WARNING, ERROR
```

## 🧪 Testing

Test the system components:

```bash
# Test system functionality (including multiline input)
python test_system.py

# Test O3 agents
python -c "from src.o3_agents import create_o3_enhancement_system; print('O3 agents:', list(create_o3_enhancement_system().keys()))"

# Test Flowise agents  
python -c "from src.flowise_agents import create_flowise_enhancement_system; print('Flowise agents:', list(create_flowise_enhancement_system().keys()))"

# Test multiline input
python -c "from src.multiline_input import detect_paste_input; print('Paste detection works:', detect_paste_input('Very long text...' * 100))"
```

## 📚 Multiline Input Use Cases

### 1. **Research Paper Analysis**
```
>>> >>>
>>> Abstract: This study investigates the effects of...
>>> Introduction: Recent advances in machine learning...
>>> [paste entire paper]
>>> END

Question: "Summarize the methodology and key findings"
```

### 2. **Code Analysis**
```
>>> >>>
>>> def complex_function():
>>>     # Large code block
>>>     return result
>>> END

Question: "Optimize this code and explain the improvements"
```

### 3. **Data Analysis**
```
>>> >>>
>>> Name,Age,Score
>>> John,25,85
>>> Jane,30,92
>>> [large CSV data]
>>> END

Question: "Analyze trends in this dataset"
```

### 4. **Medical Literature Review**
```
>>> >>>
>>> PMID: 12345678
>>> Title: Effects of Drug X on Condition Y
>>> [paste medical study]
>>> END

Question: "What are the clinical implications for treatment?"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable (especially for multiline functionality)
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the existing issues
2. Create a new issue with detailed information
3. Include logs and error messages when applicable
4. For multiline input issues, include the type and size of content being processed

---

**Enjoy having granular control over your AI processing flows with comprehensive multiline input support!** 🚀 