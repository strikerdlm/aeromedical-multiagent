"""
Core Agent System for Query Optimization.

This module implements the multi-agent system responsible for taking raw user
queries and refining them into scientifically rigorous, well-structured prompts
for the downstream deep research agents.
"""
from __future__ import annotations

import logging
from typing import List, Dict, Optional

from pydantic import BaseModel
from agents import Agent, Runner, WebSearchTool, RunConfig

# Configure logging
logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------
# Pydantic Models for Structured I/O
# ----------------------------------------------------------------------------

class ClarificationRequest(BaseModel):
    """
    A model to request clarification from the user.
    """
    questions: List[str]


class ResearchInstructions(BaseModel):
    """
    A model to hold the final, detailed research instructions for the deep
    research agent.
    """
    detailed_prompt: str
    target_model: str = "o3-deep-research-2025-06-26"


# ----------------------------------------------------------------------------
# Agent Definitions
# ----------------------------------------------------------------------------

# Placeholder for the actual agent definitions.
# We will start by defining the Triage Agent.

TRIAGE_AGENT_INSTRUCTIONS = """
You are a Triage Agent. Your job is to analyze the user's research query and decide if it requires clarification before proceeding.

- If the query is ambiguous, too broad, or lacks specific details needed for a high-quality research report, you MUST hand off to the Clarifying Agent.
- If the query is clear, specific, and ready for research, you MUST hand off to the Instruction Agent.

Return exactly ONE handoff call.
"""

CLARIFYING_AGENT_INSTRUCTIONS = """
You are a Clarification Agent. Your job is to ask the user clarifying questions to refine their research query.

- Ask 2-3 specific questions to narrow the scope, define the desired output format, or identify key areas of focus.
- Your questions should be concise and aimed at producing a high-quality, actionable research prompt.
- You must output a `ClarificationRequest` containing your questions.
"""

INSTRUCTION_AGENT_INSTRUCTIONS = """
You are an Instruction Agent. Your job is to convert a user's query (and any clarifications) into a detailed, structured prompt for a deep research model.

- The prompt must be comprehensive and follow best practices for prompting deep research models.
- It should specify the desired output format (e.g., report, analysis, summary), tone, and any specific sections to include.
- It must explicitly request in-line citations and a list of sources (minimum 50 distinct scientific references).
- It must instruct the deep research agent to produce at least 10 000 words in the final document.
- You must output `ResearchInstructions`.
"""


def create_query_optimizer_pipeline() -> Agent:
    """
    Creates the full query optimization pipeline and returns the entry-point agent.

    The pipeline consists of:
    1. Triage Agent: Decides if clarification is needed.
    2. Clarifying Agent: Asks clarifying questions.
    3. Instruction Agent: Builds the final research prompt.

    Returns:
        The Triage Agent, which is the entry point to the pipeline.
    """
    # Define the agents from last to first to set up handoffs easily
    instruction_agent = Agent(
        name="Instruction Agent",
        model="gpt-5",
        instructions=INSTRUCTION_AGENT_INSTRUCTIONS,
        output_type=ResearchInstructions,
    )

    clarifying_agent = Agent(
        name="Clarifying Agent",
        model="gpt-5",
        instructions=CLARIFYING_AGENT_INSTRUCTIONS,
        output_type=ClarificationRequest,
        handoffs=[instruction_agent],
    )

    triage_agent = Agent(
        name="Triage Agent",
        model="gpt-5",
        instructions=TRIAGE_AGENT_INSTRUCTIONS,
        handoffs=[clarifying_agent, instruction_agent],
    )

    return triage_agent
