# PRISMA Systematic Review System - Comprehensive Guide

## 🎯 Overview

The PRISMA Systematic Review System is a cutting-edge **multi-agent AI framework** that creates **PRISMA 2020-compliant systematic reviews** using advanced AI models. The system combines **OpenAI's latest models**, **Perplexity deep research**, **Grok's advanced reasoning**, and **Flowise specialized knowledge** to produce publication-ready systematic reviews.

### 🌟 Key Features

- **📊 Automated PRISMA 2020 Compliance**: Complete adherence to latest systematic review guidelines
- **🤖 Multi-Agent Architecture**: Orchestrated agents working in parallel for comprehensive coverage
- **🎯 Smart Model Selection**: Primary O3 models with intelligent fallback to O4 models
- **🔍 Multi-Source Literature Search**: PubMed, Google Scholar, Cochrane Library integration
- **📝 Publication-Ready Output**: 8,000-10,000 words with 50+ peer-reviewed citations
- **⚡ Parallel Processing**: Multiple agents working simultaneously for faster completion

## 🚀 Getting Started

### Prerequisites

Configure the following API keys in your `.env` file:

```bash
# Required API Keys
OPENAI_API_KEY=your_openai_api_key          # For O3/O4 models
PPLX_API_KEY=your_perplexity_api_key        # For literature search  
XAI_API_KEY=your_grok_api_key               # For critical analysis
FLOWISE_API_KEY=your_flowise_api_key        # For specialized knowledge (optional)
```

### Quick Start

1. **Switch to PRISMA Mode**:
   ```
   /prisma
   ```

2. **Ask Your Research Question**:
   ```
   What is the effectiveness of telemedicine in rural healthcare?
   ```

3. **The System Will Automatically**:
   - Initialize multi-agent workflow
   - Conduct comprehensive literature search
   - Screen and analyze studies
   - Generate complete systematic review
   - Validate PRISMA compliance

## 🧠 AI Models Used

### Primary Models

| Model | Purpose | Provider | Capabilities |
|-------|---------|----------|-------------|
| **o3-deep-research-2025-06-26** | Primary synthesis & analysis | OpenAI | High reasoning effort, web search, detailed summary |
| **o4-mini-deep-research-2025-06-26** | Fallback synthesis | OpenAI | High reasoning effort, detailed summary |
| **sonar-deep-research** | Literature search | Perplexity | Deep research, comprehensive search |
| **grok-beta** | Critical analysis | X.AI | Bias detection, quality assessment |

### Model Assignment by Workflow Phase

```
📚 Literature Search    → sonar-deep-research (Perplexity)
🔍 Study Screening     → grok-beta (X.AI)  
📊 Data Extraction     → o3-deep-research-2025-06-26 (OpenAI)
✍️ Review Writing      → o3-deep-research-2025-06-26 (OpenAI)
✅ Validation          → o3-deep-research-2025-06-26 (OpenAI)
```

### Fallback System

The system includes robust fallback mechanisms:
- If **O3 model fails** → Automatically switches to **O4-mini-deep-research**
- If **Primary search fails** → Uses alternative search strategies
- All transitions are seamless and logged for transparency

## 🏗️ System Architecture

### Multi-Agent Workflow

```
    User Research Question
            ↓
    ┌─────────────────────┐
    │   LeadResearcher    │ ← Main Orchestrator
    │     (Planning)      │
    └─────────┬───────────┘
              │
    ┌─────────┼─────────┐
    ↓         ↓         ↓
┌─────────┐ ┌─────────┐ ┌─────────┐
│ Search  │ │Analysis │ │Citation │ ← Parallel SubAgents
│ Agent   │ │ Agent   │ │ Agent   │
└─────────┘ └─────────┘ └─────────┘
    ↓         ↓         ↓
    └─────────┼─────────┘
              ↓
    ┌─────────────────────┐
    │  Final Synthesis    │
    │   & Validation      │
    └─────────────────────┘
              ↓
      PRISMA-Compliant
      Systematic Review
```

### Agent Responsibilities

1. **🧠 LeadResearcher Agent** (Orchestrator)
   - Plans workflow and delegates tasks
   - Analyzes query complexity
   - Synthesizes final results
   - Uses: `o3-deep-research-2025-06-26`

2. **🔍 Search Agent** (Parallel Workers)
   - Multi-database literature search
   - Keyword optimization
   - Source discovery and validation
   - Uses: `sonar-deep-research`

3. **📊 Analysis Agent** (Parallel Workers)  
   - Study quality assessment
   - Bias detection and analysis
   - Statistical evaluation
   - Uses: `grok-beta`

4. **📝 Citation Agent** (Sequential)
   - Ensures all claims are source-attributed
   - Citation formatting (APA style)
   - Reference validation
   - Uses: `o3-deep-research-2025-06-26`

## 📋 Usage Commands

### Navigation Commands
- **`/prisma`** - Switch to PRISMA systematic review mode
- **`/smart`** - Return to smart auto-detection mode
- **`/modes`** - View all available processing modes

### PRISMA-Specific Commands
- **`/prisma-status`** - Check system status and model information
- **`/prisma-reviews`** - List recent systematic reviews
- **`?`** - Show contextual help for PRISMA mode

### Export Commands
- **`/export`** - Export systematic review to markdown
- **`/save`** - Save complete session including workflow
- **`/report`** - Create structured research report

## 📊 Output Specifications

### PRISMA 2020 Requirements
- **📝 Word Count**: 8,000-10,000 words
- **📚 Citations**: Minimum 50 peer-reviewed sources in APA format
- **📋 Sections**: Complete PRISMA structure (Abstract, Introduction, Methods, Results, Discussion)
- **✅ Compliance**: Automatic adherence to PRISMA 2020 checklist

### Document Structure
1. **Abstract** - Structured summary (250-300 words)
2. **Introduction** - Background, rationale, objectives
3. **Methods** - Complete PRISMA methodology
4. **Results** - Study characteristics, findings synthesis
5. **Discussion** - Evidence summary, limitations, conclusions
6. **References** - APA-formatted citations throughout

### Quality Indicators
- ✅ PRISMA flow diagram description
- ✅ Risk of bias assessment
- ✅ Study characteristics tables
- ✅ Evidence grading when applicable
- ✅ Comprehensive citation coverage

## 🔍 Example Workflow

### Research Question Input
```
"What is the effectiveness of cognitive behavioral therapy for treating depression in adolescents?"
```

### Automatic Processing
The system will:

1. **🎯 Planning Phase** (30 seconds)
   - Extract keywords: ["cognitive behavioral therapy", "CBT", "depression", "adolescents"]
   - Define inclusion criteria: peer-reviewed, English, 2015-2024
   - Set exclusion criteria: case reports, opinion pieces

2. **🔍 Search Phase** (2-3 minutes)
   - Search PubMed, Google Scholar, Cochrane Library
   - Use Perplexity deep research for comprehensive coverage
   - Identify 100-200 potentially relevant studies

3. **📊 Analysis Phase** (2-3 minutes)
   - Screen studies using inclusion/exclusion criteria
   - Assess study quality and methodology
   - Detect potential biases and limitations

4. **✍️ Writing Phase** (5-8 minutes)
   - Generate comprehensive systematic review
   - Ensure PRISMA 2020 compliance
   - Include proper citations and formatting

5. **✅ Validation Phase** (1-2 minutes)
   - Verify PRISMA checklist completion
   - Validate citation accuracy
   - Confirm word count and quality standards

### Expected Output
A complete systematic review (8,000+ words) including:
- Structured abstract with key findings
- Comprehensive methodology section
- Results with study characteristics
- Discussion with clinical implications
- 50+ peer-reviewed citations

## ⚙️ Configuration & Settings

### Model Configuration
```python
# Primary Models
O3_PRIMARY = "o3-deep-research-2025-06-26"
O4_FALLBACK = "o4-mini-deep-research-2025-06-26"
PERPLEXITY_SEARCH = "sonar-deep-research"
GROK_ANALYSIS = "grok-beta"

# Quality Standards
TARGET_WORD_COUNT = 8000      # Minimum words
MAX_WORD_COUNT = 10000        # Maximum words  
MIN_CITATIONS = 50            # Minimum citations
PRISMA_COMPLIANCE_THRESHOLD = 0.8  # 80% checklist completion
```

### API Configuration
All models are configured with optimal settings:
- **Temperature**: 0.2-0.3 for consistent, reliable output
- **Reasoning Effort**: "high" for complex analysis tasks
- **Max Tokens**: Optimized per model capabilities
- **Retry Logic**: 3 attempts with exponential backoff

## 🛠️ Advanced Features

### Intelligent Fallback System
```python
try:
    # Use primary O3 model with full capabilities
    response = client.responses.create(
        model="o3-deep-research-2025-06-26",
        reasoning={"effort": "high", "summary": "detailed"},
        tools=[{"type": "web_search_preview"}]
    )
except Exception as e:
    # Automatic fallback to O4 model
    response = client.chat.completions.create(
        model="o4-mini-deep-research-2025-06-26",
        reasoning={"summary": "detailed"}
    )
```

### Parallel Processing
- **Multiple Search Agents**: 3-5 agents search different keyword combinations
- **Concurrent Analysis**: Quality assessment and bias detection in parallel
- **External Memory**: Redis-based state management across agents
- **Load Balancing**: Intelligent distribution of tasks

### Quality Assurance
- **Automatic PRISMA Validation**: Real-time checklist compliance
- **Citation Verification**: Cross-reference all claims with sources
- **Bias Detection**: Systematic identification of publication bias
- **Expert Review Recommendations**: Guidance for human validation

## 📊 Performance Metrics

### Typical Processing Time
| Phase | Duration | Description |
|-------|----------|-------------|
| Planning | 30 seconds | Query analysis and workflow setup |
| Literature Search | 2-3 minutes | Multi-database search execution |
| Study Analysis | 2-3 minutes | Quality assessment and screening |
| Review Generation | 5-8 minutes | Writing and synthesis |
| Validation | 1-2 minutes | PRISMA compliance checking |
| **Total** | **10-16 minutes** | Complete systematic review |

### Resource Usage
- **API Calls**: 15-25 total across all services
- **Token Usage**: 50,000-100,000 tokens (varies by complexity)
- **Output Size**: 50-150KB markdown files
- **Accuracy**: 80%+ PRISMA 2020 compliance

## 🚨 Important Guidelines

### 🔬 Research Tool Purpose
This system is designed for **research and educational purposes**. It serves as a sophisticated tool to **accelerate systematic review development**, not replace expert judgment.

### 👨‍🔬 Expert Validation Required
**All outputs must be validated by qualified researchers** before use in:
- ✅ Publication submissions
- ✅ Clinical decision-making  
- ✅ Policy development
- ✅ Grant applications

### 📋 Quality Assurance Steps
1. **Verify Citations**: Check all references for accuracy
2. **Review Methodology**: Ensure search strategy appropriateness
3. **Validate Conclusions**: Confirm findings align with evidence
4. **Check Compliance**: Review PRISMA checklist completion

## 🔧 Troubleshooting

### Common Issues & Solutions

**🚫 PRISMA Mode Unavailable**
```bash
# Check API configuration
/prisma-status

# Verify environment variables
echo $OPENAI_API_KEY
echo $PPLX_API_KEY
echo $XAI_API_KEY
```

**⚠️ Low Quality Output**
- Provide more specific research questions
- Ensure sufficient literature exists for the topic
- Check that inclusion criteria aren't too restrictive

**🐌 Slow Processing**
- Verify stable internet connection
- Check API rate limits and quotas
- Simplify research question if overly complex

### Model Status Check
Use `/prisma-status` to see:
- 🔗 API connectivity for all services
- 🎯 Current models in use
- 📊 System capabilities and limitations
- 📈 Recent workflow statistics

## 📚 Example Use Cases

### Clinical Research
```
Research Question: "Effectiveness of mindfulness-based interventions for anxiety in healthcare workers"
→ Comprehensive review of 40+ studies
→ Risk of bias assessment included
→ Clinical implications discussed
```

### Public Health
```
Research Question: "Impact of vaccination campaigns on disease prevention in low-income countries"
→ Multi-database search across global literature
→ Quality assessment of intervention studies
→ Policy recommendations included
```

### Technology Assessment
```
Research Question: "Artificial intelligence applications in medical diagnosis accuracy"
→ Recent literature from 2020-2024
→ Comparative analysis of AI vs traditional methods
→ Future research directions identified
```

## 🚀 Advanced Usage

### Custom Research Parameters
For advanced users, the system supports detailed customization:

```python
# Example: Custom systematic review
result = orchestrator.create_systematic_review(
    research_question="Your specific research question",
    search_keywords=["keyword1", "keyword2", "keyword3"],
    inclusion_criteria=[
        "Randomized controlled trials",
        "Published 2020-2024", 
        "English language",
        "Adult participants"
    ],
    exclusion_criteria=[
        "Case studies",
        "Opinion articles",
        "Animal studies"
    ],
    additional_context="Focus on high-quality evidence with low risk of bias"
)
```

## 📈 Future Enhancements

### Planned Features
- 🌐 **Multi-language Support**: Systematic reviews in multiple languages
- 📊 **Advanced Statistics**: Integrated meta-analysis capabilities
- 🏥 **Domain Templates**: Specialized templates for different research areas
- 🔗 **Database Integration**: Direct API connections to major databases
- 📱 **Web Interface**: Browser-based systematic review creation

### Research Opportunities
- Integration with systematic review software (RevMan, Covidence)
- Real-time collaboration features for research teams
- Enhanced bias detection algorithms
- Automated GRADE evidence assessment

## 🤝 Contributing

Areas where contributions are welcome:
- **Database Integrations**: Additional literature databases
- **Quality Metrics**: Enhanced assessment algorithms  
- **Domain Expertise**: Subject-specific templates and criteria
- **Citation Management**: Advanced reference handling
- **User Interface**: Improved accessibility and usability

---

## 📞 Support & Resources

### Technical Support
- 📋 Run system diagnostics: `/prisma-status`
- 📊 Check recent reviews: `/prisma-reviews`
- 🔍 Review application logs for detailed error information
- 📚 Consult this comprehensive guide for usage questions

### Best Practices
1. **Start with specific research questions** for better results
2. **Review and validate all outputs** before use
3. **Check PRISMA compliance** using the built-in validation
4. **Export and backup** systematic reviews regularly
5. **Collaborate with domain experts** for quality assurance

---

**The PRISMA Systematic Review System represents the cutting edge of AI-assisted research methodology, combining multiple frontier models to create comprehensive, publication-quality systematic reviews while maintaining the highest standards of scientific rigor.**

*Version: 2.0 | Last Updated: January 2025 | Status: Production Ready* 