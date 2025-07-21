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
You are a world-class research assistant. Your purpose is to conduct deep, empirical research based on the user's detailed instructions.

- You MUST adhere strictly to the provided research prompt.
- You MUST perform a comprehensive web search to gather information from multiple reputable sources.
- You MUST provide inline citations for all claims and a formatted list of all sources at the end of your response.
- Your output should be a well-structured, detailed research report.
- Your reasoning effort must be high, and your summary must be detailed.
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