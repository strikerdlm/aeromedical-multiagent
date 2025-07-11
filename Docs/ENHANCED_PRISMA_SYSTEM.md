# Enhanced PRISMA System - Technical Documentation

## 📢 Documentation Consolidated

This technical documentation has been merged into a comprehensive, unified guide.

**📚 Please refer to the new comprehensive documentation:**
→ **[PRISMA_COMPREHENSIVE_GUIDE.md](PRISMA_COMPREHENSIVE_GUIDE.md)**

## What You'll Find in the Comprehensive Guide

The new documentation includes all technical details from this file plus:

### 🏗️ **System Architecture**
- Complete multi-agent workflow diagrams
- Orchestrator-worker pattern implementation
- External memory system details
- Model assignment by workflow phase

### 🧠 **Model Information**
- **Primary**: `o3-deep-research-2025-06-26` (OpenAI)
- **Fallback**: `o4-mini-deep-research-2025-06-26` (OpenAI)
- **Search**: `sonar-deep-research` (Perplexity)
- **Analysis**: `grok-beta` (X.AI)

### ⚙️ **Technical Features**
- Parallel SubAgent processing
- Redis-based external memory
- Production guardrails and error handling
- Intelligent fallback mechanisms

### 🔧 **Implementation Details**
- API configuration examples
- Code snippets for advanced usage
- Integration with existing systems
- Performance optimization tips

## Quick Technical Reference

```python
# Initialize enhanced PRISMA system
from src.enhanced_prisma_orchestrator import create_enhanced_prisma_orchestrator
orchestrator = create_enhanced_prisma_orchestrator()

# Create systematic review with orchestrator-worker pattern
result = orchestrator.create_enhanced_systematic_review(
    research_question="Your research question",
    search_keywords=["keyword1", "keyword2"],
    inclusion_criteria=["criteria1", "criteria2"],
    exclusion_criteria=["exclusion1", "exclusion2"]
)
```

For complete technical documentation, see **[PRISMA_COMPREHENSIVE_GUIDE.md](PRISMA_COMPREHENSIVE_GUIDE.md)**

---

*This file is maintained for backwards compatibility. All current technical documentation is in the comprehensive guide.*