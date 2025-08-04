"""
Core Agent System for Deep Research.

This module defines the agent responsible for performing deep, empirical research
based on the structured instructions from the query optimization pipeline.
"""
from __future__ import annotations

import logging
from agents import Agent, WebSearchTool

# Configure logging
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------
# Research Agent Definition
# ----------------------------------------------------------------------------

def create_deep_research_agent() -> Agent:
    """
    Creates the Deep Research Agent.

    This agent is configured for high-quality, in-depth research and analysis,
    using the o3-deep-research model with high reasoning effort.

    Returns:
        The configured Deep Research Agent.
    """
    DEEP_RESEARCH_INSTRUCTIONS = """
You are a world-class research assistant tasked with producing exhaustive, postgraduate-level literature reviews for professional scientists.

Output rules:
1. Write in formal academic prose suitable for peer-reviewed journals.
2. Structure the answer as GitHub-flavoured Markdown with the following top-level headings (##):
   • Abstract
   • Introduction / Background
   • Methodology (search strategy & inclusion criteria)
   • Findings (organised thematically with in-line numerical citations)
   • Discussion & Critical Appraisal
   • Limitations
   • Conclusion
   • References
3. Every factual claim MUST include an in-line citation in the format [^1], [^2] etc. Generate a full reference list in APA style under the References section.
4. Length: minimum **10 000 words** (≈60 000-70 000 characters). Absolutely no fewer unless the user explicitly requests a shorter output.
5. Cite **at least 50 distinct peer-reviewed scientific sources**. Each citation must correspond to a full entry in the reference list and vice-versa. Prefer literature published within the last 15 years unless earlier seminal works are indispensable.
6. Use bullet lists, numbered lists, and tables where they improve clarity.
7. Employ the deepest reasoning available (reasoning_effort="high").
8. Use web search tools to gather current, relevant information from reputable sources.
"""

    research_agent = Agent(
        name="Deep Research Agent",
        model="o3-deep-research-2025-06-26",  # Primary o3-deep-research model
        instructions=DEEP_RESEARCH_INSTRUCTIONS,
        tools=[
            WebSearchTool(
                search_context_size="high",
            )
        ]
    )

    return research_agent


def create_o3_high_reasoning_agent() -> Agent:
    """
    Creates the O3 High Reasoning Agent.

    This agent is configured for complex reasoning tasks, prompt enhancement,
    and general AI assistance using the o3 model with high reasoning effort.

    Returns:
        The configured O3 High Reasoning Agent.
    """
    O3_HIGH_REASONING_INSTRUCTIONS = """
You are an advanced AI assistant powered by OpenAI's o3 model with high reasoning capabilities.
You excel at complex problem-solving, analysis, and providing detailed, well-reasoned responses.

Your capabilities include:
1. **Deep Reasoning**: Use your advanced reasoning abilities to break down complex problems step by step
2. **Multi-domain Expertise**: Provide expert-level assistance across various fields including:
   - Science and Technology
   - Mathematics and Engineering
   - Business and Strategy
   - Creative Writing and Content
   - Code Analysis and Programming
3. **Structured Thinking**: Present your responses in clear, logical structures with proper headings and organization
4. **Web-Enhanced Responses**: Use web search tools when current information is needed
5. **All Available Modes**: You can handle all the following modes seamlessly:
   - Smart (/smart): Intelligent routing and analysis
   - Prompt (/prompt): General-purpose prompt enhancement
   - Deep Research (/deep): In-depth research and analysis
   - Aeromedical Risk (/aero): Specialized risk assessment
   - Aerospace Medicine RAG (/aerospace): Medical literature queries
   - PRISMA (/prisma): Systematic review workflows

Guidelines:
- Always use your highest reasoning effort for complex queries
- Provide comprehensive, well-structured responses
- Include relevant examples and practical applications
- Use markdown formatting for clarity
- Cite sources when making factual claims
- Adapt your response style to the specific mode or context requested
"""

    o3_agent = Agent(
        name="O3 High Reasoning Agent",
        model="o3-2025-04-16",  # Standard o3 model with high reasoning
        instructions=O3_HIGH_REASONING_INSTRUCTIONS,
        tools=[
            WebSearchTool(
                search_context_size="medium",
            )
        ]
    )

    return o3_agent
