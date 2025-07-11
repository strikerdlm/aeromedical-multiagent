# Enhanced PRISMA System with Orchestrator-Worker Philosophy

## Overview

This document describes the enhanced PRISMA systematic review system that implements the fusion of Anthropic's orchestrator-worker philosophy with OpenAI's Agents SDK. The system is designed to create comprehensive, PRISMA-compliant systematic reviews using parallel SubAgents, external memory, and production guardrails.

## Architecture

### Core Components

1. **LeadResearcher Agent** - Main orchestrator
2. **SubAgents** - Parallel workers (SearchAgent, AnalysisAgent, CitationAgent)
3. **External Memory System** - Redis-based state management
4. **Enhanced Models** - o3, o3-deep-research, grok-4, perplexity deep research
5. **Production Guardrails** - JSON schema validation, error handling

### Implementation Files

- `src/enhanced_prisma_orchestrator.py` - Main implementation
- `src/config.py` - Model configurations (needs updating)
- `requirements.txt` - Dependencies (redis added)

## System Design Principles

### 1. Orchestrator-Worker Pattern

- **LeadResearcher** plans, writes to external memory, spawns specialized SubAgents
- **SubAgents** work in parallel with independent context windows
- **CitationAgent** ensures all claims are source-attributed
- **External Memory** maintains state across agent interactions

### 2. Prompt Engineering Heuristics

- Clear delegation with objectives, output schemas, tools, and stop conditions
- Effort scaling based on query complexity (simple ↔ complex)
- Start-wide-then-narrow search approach
- Parallel tool calls with 3-5 SubAgents
- Extended thinking for reasoning and self-critique

### 3. Production Guardrails

- Checkpoints and retries for stateful execution
- Observability via OpenAI traces
- JSON schema guardrails on tool calls
- Error handling and recovery mechanisms

## Model Configuration

### Enhanced Models to Use

```python
# Updated model configurations needed in config.py
ENHANCED_MODELS = {
    "o3_deep_research": {
        "model_name": "o3-deep-research",
        "max_tokens": 12000,
        "temperature": 0.3,
        "reasoning_effort": "high"
    },
    "o3_high_reasoning": {
        "model_name": "o3",
        "max_tokens": 8000,
        "temperature": 0.2,
        "reasoning_effort": "high"
    },
    "grok_4": {
        "model_name": "grok-4",
        "max_tokens": 4000,
        "temperature": 0.3,
        "reasoning_effort": "high"
    },
    "perplexity_deep_research": {
        "model_name": "llama-3.1-sonar-huge-128k-online",
        "max_tokens": 8000,
        "temperature": 0.2
    }
}
```

## System Templates

### LeadResearcher System Prompt

```
You are **LeadResearcher**, a scientific orchestrator agent.

Philosophy & Strategy:
• Think in explicit plans, save them to Memory after each modification
• Decompose the user query into focused research tasks; spawn ≤5 SubAgents IN PARALLEL
• Adopt "start-wide-then-narrow": begin with broad searches, iteratively refine
• Scale effort based on complexity heuristics (simple, comparative, complex)
• Synthesize SubAgent outputs into consolidated drafts
• Hand off to CitationAgent for final grounding

Tool Policy:
• Available tools: web_search, file_search, code_interpreter, memory_system
• Use extended thinking blocks for scratch-pad reasoning
• Monitor Memory for duplicate work and overlapping scopes

Output Schema:
{
  "summary": "Concise paragraph answer",
  "subagent_plans": [{"id": "S1", "role": "SearchAgent", "objective": "...", "tool_budget": 15}],
  "complete": true | false
}
```

### SubAgent Role Prompts

#### SearchAgent
```
Role = SearchAgent
Objective = {{OBJECTIVE}}
Allowed tools = web_search, file_search
Hard limits: ≤15 tool calls, finish within 300 seconds
Method:
1. Draft hypothesis of where info may reside
2. Issue broad searches; inspect quality
3. Iterate: narrow terms, switch tools as needed
4. Write THOUGHTS after each tool call
Stop when confidence ≥0.8 or budget exhausted
Return: {"findings": [...], "open_questions": [...], "confidence": 0.0-1.0}
```

#### AnalysisAgent
```
Role = AnalysisAgent
Tools = code_interpreter, file_search
Task: Statistical analysis and quality assessment
Return: {"analysis": "interpretation", "supporting_tables": "CSV", "code_refs": [...]}
```

#### CitationAgent
```
Role = CitationAgent
Input = full draft + raw sources
Task: attach precise citations for every claim using source offsets
Return: cleaned, cited answer in Markdown
```

## Execution Header Configuration

```json
{
  "model": "o3-deep-research",
  "temperature": 0.2,
  "tools": [
    {"type": "web_search", "user_location": "approximate"},
    {"type": "file_search"},
    {"type": "code_interpreter", "handler": "sandbox_python"}
  ],
  "guardrails": {
    "input_schema": "enhanced_prisma_input_v1.json",
    "output_schema": "enhanced_prisma_output_v1.json"
  },
  "session_backend": "redis://localhost:6379/0",
  "tracing": true,
  "max_parallel_agents": 5,
  "retry_policy": {"max_retries": 3, "backoff": 2}
}
```

## Workflow Phases

### 1. Planning Phase
- LeadResearcher analyzes query complexity
- Creates SubAgent plans with specific objectives
- Initializes external memory with workflow state

### 2. Parallel Search Phase
- Multiple SearchAgents work on different keyword groups
- Parallel web searches using ThreadPoolExecutor
- Results stored in external memory

### 3. Parallel Analysis Phase
- AnalysisAgents perform quality assessment and bias detection
- Statistical analysis and evidence synthesis
- Confidence scoring for each analysis

### 4. Citation Phase
- CitationAgent ensures all claims are source-attributed
- Proper citation formatting with source tracking
- Cross-referencing against available sources

### 5. Synthesis Phase
- LeadResearcher compiles all results
- Creates comprehensive PRISMA-compliant review
- Final validation and quality checks

## External Memory System

### Redis Implementation
```python
class ExternalMemorySystem:
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        # Redis client with fallback to in-memory
        # TTL support for session management
        # JSON serialization for complex data
        
    def store(self, key: str, value: Any, ttl: int = 3600) -> bool:
        # Store workflow state, results, checkpoints
        
    def retrieve(self, key: str) -> Optional[Any]:
        # Retrieve state for agent coordination
        
    def update_workflow_state(self, session_id: str, workflow) -> bool:
        # Update workflow progress and results
```

## Known Issues and Fixes Needed

### 1. API Method Compatibility
- **Issue**: Perplexity client `search` method doesn't exist
- **Fix**: Use existing `perplexity_client` methods from current implementation

### 2. Grok Client Methods
- **Issue**: Grok client `complete` method doesn't exist
- **Fix**: Use existing `grok_client` methods from current implementation

### 3. Type Annotations
- **Issue**: Several Optional type annotations need refinement
- **Fix**: Complete the type annotation fixes in dataclasses

### 4. Model Names
- **Issue**: Model names need validation against available models
- **Fix**: Update config.py with actual available model names

### 5. OpenAI Client Integration
- **Issue**: LeadResearcherAgent needs proper OpenAI client
- **Fix**: Add OpenAI client initialization similar to existing implementation

## Integration Steps

### 1. Update Configuration
```python
# Add to config.py
class EnhancedPRISMAConfig:
    # Enhanced model configurations
    # External memory settings
    # Orchestrator parameters
```

### 2. Fix API Methods
```python
# Update method calls to use existing client APIs
# Replace non-existent methods with working equivalents
# Maintain compatibility with current system
```

### 3. Complete Type Annotations
```python
# Fix all Optional type annotations
# Add proper field factories for mutable defaults
# Ensure type safety throughout
```

### 4. Integration Testing
```python
# Test with existing PRISMA workflow
# Validate parallel execution
# Verify external memory persistence
```

## Usage Example

```python
# Initialize enhanced orchestrator
orchestrator = create_enhanced_prisma_orchestrator()

# Create systematic review
result = orchestrator.create_enhanced_systematic_review(
    research_question="What is the effectiveness of ML in healthcare?",
    search_keywords=["machine learning", "healthcare", "effectiveness"],
    inclusion_criteria=["Peer-reviewed", "2020-2024", "English"],
    exclusion_criteria=["Case reports", "Opinion pieces"]
)

# Monitor workflow
status = orchestrator.get_workflow_status(result['session_id'])
```

## Benefits of Enhanced System

1. **Parallel Execution**: Multiple SubAgents work simultaneously
2. **External Memory**: Persistent state across agent interactions
3. **Production Ready**: Proper error handling and retries
4. **PRISMA Compliant**: Follows PRISMA 2020 guidelines
5. **Scalable**: Handles complex research questions effectively
6. **Observable**: Full tracing and monitoring capabilities

## Next Steps

1. **Fix API Compatibility**: Update method calls to use existing client methods
2. **Complete Type Safety**: Finish type annotation fixes
3. **Integration Testing**: Test with existing PRISMA workflows
4. **Performance Optimization**: Optimize parallel execution
5. **Documentation**: Create user guides and API documentation

This enhanced system represents a significant advancement in systematic review automation, combining the best of orchestrator-worker patterns with production-ready guardrails and PRISMA compliance.