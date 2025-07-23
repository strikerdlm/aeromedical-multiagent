# Model Support Documentation

## Overview

This document outlines the AI models supported by the system and their capabilities.

## Grok Models (xAI)

### Available Models

1. **grok-4** (Default - Recommended)
   - Latest and most powerful model from xAI
   - Superior reasoning capabilities
   - Context window: 256,000 tokens
   - Best for complex reasoning, mathematics, and coding tasks
   - Released: July 2025

2. **grok-3**
   - Previous generation model
   - Context window: 131,072 tokens
   - Good balance of performance and cost

3. **grok-3-beta**
   - Beta version with experimental features
   - Enhanced reasoning capabilities
   - Context window: 131,072 tokens

4. **grok-beta** (Legacy)
   - Original model, maintained for backward compatibility
   - Basic reasoning capabilities

5. **grok-vision-beta**
   - Multimodal model with vision capabilities
   - Can process images alongside text

### Configuration

Set the model via environment variable:
```bash
GROK_MODEL=grok-4  # Options: grok-4, grok-3, grok-3-beta, grok-beta, grok-vision-beta
```

## Perplexity Models

### Available Models

1. **sonar-deep-research** (Default - Recommended)
   - Best for comprehensive research tasks
   - Optimized for academic and scholarly sources
   - Excellent citation capabilities
   - Ideal for systematic reviews and literature searches

2. **sonar-pro**
   - Balanced performance model
   - Good for general-purpose queries
   - Faster response times

3. **sonar-reasoning-pro**
   - Advanced reasoning capabilities
   - Better for complex logical tasks
   - Enhanced problem-solving abilities

4. **sonar**
   - Basic model for simple queries
   - Most cost-effective option

### Configuration

Set the model via environment variable:
```bash
PERPLEXITY_MODEL=sonar-deep-research  # Options: sonar-deep-research, sonar-pro, sonar-reasoning-pro, sonar
```

## Model Selection Guidelines

### For PRISMA Systematic Reviews
- **Grok**: Use `grok-4` for critical analysis and bias detection
- **Perplexity**: Use `sonar-deep-research` for literature searches

### For General Research
- **Grok**: Use `grok-3` or `grok-4` for reasoning tasks
- **Perplexity**: Use `sonar-pro` for balanced performance

### For Quick Queries
- **Grok**: Use `grok-beta` for basic tasks
- **Perplexity**: Use `sonar` for simple searches

## API Pricing

### Grok Models
- **grok-4**: $3.00/1M input tokens, $15.00/1M output tokens
- **grok-3**: $2.00/1M input tokens, $10.00/1M output tokens
- Other models: Check xAI documentation for current pricing

### Perplexity Models
- Pricing varies by model and usage
- Check Perplexity API documentation for current rates

## Migration from Legacy Models

If you're currently using `grok-beta`, we recommend migrating to `grok-4` for:
- Better reasoning capabilities
- Improved accuracy
- Larger context window
- Enhanced performance on complex tasks

To migrate, simply update your `.env` file:
```bash
# Old configuration
# GROK_MODEL=grok-beta

# New configuration
GROK_MODEL=grok-4
```

## Troubleshooting

### Model Not Available
If a model is not available, the system will:
1. Log a warning message
2. Fall back to the default model
3. Continue operation with the fallback

### API Key Issues
Ensure your API keys are properly configured:
- `XAI_API_KEY` for Grok models
- `PPLX_API_KEY` for Perplexity models

### Performance Considerations
- Newer models (grok-4, sonar-deep-research) may have higher latency
- For time-sensitive applications, consider using faster models
- Monitor your API usage to manage costs effectively