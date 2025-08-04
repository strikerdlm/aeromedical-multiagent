from __future__ import annotations

"""PRISMA systematic review pipeline using OpenAI Agents SDK."""

import logging
from agents import Agent, Runner, RunConfig
from .core_agents.research_agents import create_deep_research_agent
from .config import PRISMAConfig

logger = logging.getLogger(__name__)


def create_prisma_writer_agent() -> Agent:
    """Return an agent that writes the final PRISMA review."""
    instructions = f"""
You are an expert academic writer tasked with drafting a PRISMA-compliant systematic review.
Follow this structure:
- Title
- Abstract
- Introduction
- Methods
- Results
- Discussion
- Limitations
- Conclusion
- References
Use formal academic language and Markdown headings (##). Include at least {PRISMAConfig.MIN_CITATIONS} peer-reviewed citations in APA style. Target between {PRISMAConfig.TARGET_WORD_COUNT} and {PRISMAConfig.MAX_WORD_COUNT} words.
"""
    return Agent(
        name="PRISMA Writer",
        model="o3-deep-research-2025-06-26",
        instructions=instructions,
    )


async def run_prisma_pipeline(research_question: str) -> str:
    """Run a simplified PRISMA pipeline using deep-research then o3 models."""
    logger.info("Starting PRISMA research pipeline")

    # Stage 1: deep research to gather literature
    search_agent = create_deep_research_agent()
    search_cfg = RunConfig(model="o3-deep-research-2025-06-26", tracing_disabled=True)
    search_res = await Runner.run(search_agent, research_question, run_config=search_cfg)
    research_material = getattr(search_res, "final_output", str(search_res))

    # Stage 2: write full review
    writer_agent = create_prisma_writer_agent()
    writer_prompt = (
        f"Using the following research notes, write a PRISMA systematic review on '{research_question}'.\n\n"
        f"Research notes:\n{research_material}"
    )
    writer_cfg = RunConfig(model="o3-deep-research-2025-06-26", tracing_disabled=True)
    final_res = await Runner.run(writer_agent, writer_prompt, run_config=writer_cfg)
    final_output = getattr(final_res, "final_output", str(final_res))
    return final_output
