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
    using the best available models and tools.

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
"""

    research_agent = Agent(
        name="Deep Research Agent",
        model="o3-deep-research",  # Primary model
        # Fallback models can be handled by the runner logic if the primary fails.
        # model_fallbacks=["o3", "o4-mini-deep-research"],
        instructions=DEEP_RESEARCH_INSTRUCTIONS,
        tools=[
            WebSearchTool(
                search_context_size="high",
            )
        ],
        # The 'reasoning' and other parameters are part of the Responses API
        # and are passed at runtime via ModelSettings or similar, not directly in Agent constructor.
        # We will handle this in the runner.
    )

    return research_agent 