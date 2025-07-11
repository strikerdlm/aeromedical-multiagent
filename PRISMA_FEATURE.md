# PRISMA Systematic Review Feature

## Overview

The PRISMA Systematic Review feature is a comprehensive multi-agent framework that creates PRISMA 2020-compliant systematic reviews and meta-analyses using cutting-edge AI models. This feature integrates OpenAI's O3 deep research models, Perplexity's deep research capabilities, Grok's advanced reasoning, and specialized Flowise chatflows to produce publication-ready systematic reviews.

## 🌟 Key Features

### **Multi-Agent Architecture**
- **O4 Deep Research**: Uses `o4-mini` with high reasoning effort for comprehensive analysis
- **Perplexity Deep Research**: Leverages `llama-3.1-sonar-large-128k-online` for literature search
- **Grok Advanced Reasoning**: Employs `grok-beta` for critical analysis and bias detection
- **Flowise Integration**: Connects to specialized chatflows for domain-specific knowledge

### **PRISMA 2020 Compliance**
- Follows complete PRISMA 2020 guidelines
- Generates 8,000-10,000 word systematic reviews
- Includes ≥50 peer-reviewed citations in APA format
- Complete workflow: Planning → Search → Screening → Extraction → Analysis → Writing → Validation

### **Automated Workflow**
- **Literature Search**: Multi-source search across PubMed, Google Scholar, Cochrane Library
- **Study Screening**: Automated inclusion/exclusion criteria application
- **Quality Assessment**: Risk of bias evaluation and methodology review
- **Data Extraction**: Structured data extraction using standardized templates
- **Evidence Synthesis**: Advanced reasoning for meta-analysis and narrative synthesis
- **Validation**: PRISMA compliance checking and quality assurance

## 🚀 Getting Started

### Prerequisites

The PRISMA feature requires multiple API keys for full functionality:

```bash
# Required API Keys (add to .env file)
OPENAI_API_KEY=your_openai_api_key          # For O3 models
FLOWISE_API_KEY=your_flowise_api_key        # For specialized chatflows
PPLX_API_KEY=your_perplexity_api_key        # For deep research
XAI_API=your_grok_api_key                   # For advanced reasoning
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

3. **The system will automatically**:
   - Initialize multi-agent workflow
   - Conduct comprehensive literature search
   - Screen and filter studies
   - Extract and analyze data
   - Generate complete systematic review
   - Validate PRISMA compliance

## 📋 Usage Commands

### Mode Commands
- `/prisma` - Switch to PRISMA systematic review mode
- `/smart` - Return to smart auto-detection mode

### PRISMA-Specific Commands
- `/prisma-status` - Check system status and API connectivity
- `/prisma-reviews` - List recent systematic reviews
- `/export` - Export systematic review to markdown
- `/save` - Save complete session including workflow
- `/report` - Create structured research report

### Quick Help
- `?` - Show contextual help for current mode
- `/modes` - View all available processing modes

## 🏗️ Architecture

### Agent Workflow

```
Planner Agent → Searcher Agent → Reviewer Agent → Writer Agent → Validator Agent
     ↓              ↓              ↓               ↓              ↓
Initialize      Literature     Screening &     Generate      Validate &
Workflow        Search         Quality         Review         Finalize
                              Assessment
```

### AI Model Integration

- **O4 High Reasoning** (`o4-mini`): Final review generation and synthesis
- **Perplexity Research** (`llama-3.1-sonar-large-128k-online`): Literature search and data extraction
- **Grok Reasoning** (`grok-beta`): Critical analysis, bias detection, quality assessment
- **Flowise Chatflows**: Specialized domain knowledge and additional research sources

### Chatflow Integration

The system automatically calls these Flowise chatflows:
- `43677137-d307-4ff4-96c9-5019b6e10879` - Primary research chatflow
- `d0bf0d84-1343-4f3b-a887-780d20f9e3c6` - Secondary research chatflow

## 📊 Output Specifications

### PRISMA Requirements
- **Word Count**: 8,000-10,000 words
- **Citations**: Minimum 50 peer-reviewed sources
- **Format**: Markdown with proper academic structure
- **Compliance**: PRISMA 2020 checklist adherence

### Document Structure
1. **Abstract** - Structured summary with background, methods, results, conclusions
2. **Introduction** - Background, rationale, and research objectives
3. **Methods** - Complete PRISMA methodology including search strategy, screening, data extraction
4. **Results** - Study characteristics, risk of bias assessment, synthesis of findings
5. **Discussion** - Summary of evidence, limitations, conclusions, implications

### Quality Indicators
- APA-formatted citations throughout
- PRISMA flow diagram description
- Risk of bias assessment tables
- Study characteristics tables
- Evidence grading (GRADE approach when applicable)

## 🔍 Example Workflow

### 1. Research Question Input
```
"What is the effectiveness of cognitive behavioral therapy for treating depression in adolescents?"
```

### 2. Automatic Processing
The system automatically:
- Extracts keywords: ["cognitive behavioral therapy", "CBT", "depression", "adolescents", "teenagers"]
- Defines inclusion criteria: peer-reviewed, English, 2010-2024, relevant population
- Sets exclusion criteria: case reports, opinion pieces, non-peer reviewed
- Searches multiple databases
- Screens studies for relevance
- Extracts data using standardized templates
- Assesses study quality and bias
- Synthesizes evidence
- Generates complete systematic review

### 3. Output Example
A complete 8,000+ word systematic review including:
- Structured abstract (250-300 words)
- Comprehensive introduction with background
- Detailed methodology following PRISMA guidelines
- Results with study characteristics and findings
- Discussion with implications and limitations
- 50+ peer-reviewed citations in APA format

## ⚙️ Configuration

### PRISMA Configuration (`PRISMAConfig`)
```python
# Model specifications
O3_HIGH_REASONING = "o4-mini"               # Primary synthesis model
PERPLEXITY_MODEL = "llama-3.1-sonar-large-128k-online"  # Research model
GROK_MODEL = "grok-beta"                     # Reasoning model

# Output requirements
TARGET_WORD_COUNT = 8000                     # Minimum words
MAX_WORD_COUNT = 10000                       # Maximum words
MIN_CITATIONS = 50                           # Minimum citations

# Chatflow IDs
PRISMA_CHATFLOWS = {
    "research_1": "43677137-d307-4ff4-96c9-5019b6e10879",
    "research_2": "d0bf0d84-1343-4f3b-a887-780d20f9e3c6"
}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_prisma.py
```

This tests:
- Module imports
- Configuration validation
- Client initialization
- Agent system functionality
- Orchestrator integration
- Main application integration

## 📈 Performance Metrics

### Typical Processing Time
- **Literature Search**: 2-3 minutes
- **Study Screening**: 1-2 minutes
- **Quality Assessment**: 2-3 minutes
- **Review Generation**: 5-10 minutes
- **Total Process**: 10-18 minutes

### Resource Usage
- **API Calls**: ~15-25 total across all services
- **Token Usage**: 50,000-100,000 tokens (varies by complexity)
- **Memory**: ~500MB peak during processing
- **Storage**: Generated reviews typically 50-150KB

## 🚨 Important Disclaimers

### 🧪 Research Tool
This feature is designed for **research and educational purposes**. While sophisticated, it should be used as a supplementary tool for systematic review development.

### 👨‍⚕️ Expert Validation Required
**All outputs must be validated by qualified researchers and subject matter experts** before use in:
- Publication submissions
- Clinical decision-making
- Policy development
- Grant applications

### 📋 Quality Assurance
- AI-generated content may contain inaccuracies
- Citations and references require verification
- Methodology may need expert refinement
- Results interpretation requires domain expertise

## 🔧 Troubleshooting

### Common Issues

1. **PRISMA Mode Unavailable**
   - Check all required API keys are configured
   - Verify environment variables in `.env` file
   - Run `/prisma-status` to check connectivity

2. **Processing Failures**
   - Ensure stable internet connection
   - Check API key quotas and limits
   - Simplify research question if too complex

3. **Low Quality Output**
   - Provide more specific research questions
   - Check that topic has sufficient literature
   - Verify domain expertise for interpretation

### API Key Issues
- **OpenAI**: Required for O3 models and orchestration
- **Perplexity**: Required for comprehensive literature search
- **Grok**: Required for critical analysis and reasoning
- **Flowise**: Required for specialized domain knowledge

## 🚀 Advanced Usage

### Custom Research Parameters
```python
# For advanced users - customize search strategy
orchestrator.create_systematic_review(
    research_question="Your research question",
    search_keywords=["keyword1", "keyword2", "keyword3"],
    inclusion_criteria=[
        "Peer-reviewed articles",
        "Published 2015-2024",
        "English language",
        "Adult population"
    ],
    exclusion_criteria=[
        "Case reports",
        "Opinion pieces",
        "Non-human studies"
    ],
    additional_context="Focus on randomized controlled trials"
)
```

### Export Options
- **Markdown**: Standard academic format for documentation
- **JSON**: Complete metadata including workflow details
- **Structured Report**: Enhanced formatting with executive summary

## 🤝 Contributing

Areas for enhancement:
- Additional database integrations
- Enhanced citation management
- Advanced statistical analysis
- Domain-specific templates
- Multi-language support

## 📞 Support

For technical issues:
1. Check the application logs
2. Run the test suite (`python test_prisma.py`)
3. Verify API configurations
4. Review PRISMA feature documentation

---

**The PRISMA Systematic Review feature represents the cutting edge of AI-assisted research methodology, combining multiple frontier models to create comprehensive, publication-quality systematic reviews while maintaining the highest standards of scientific rigor.** 