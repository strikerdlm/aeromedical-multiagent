from __future__ import annotations

"""Deep Aeromedical Research pipeline using OpenAI Agents SDK.

This pipeline builds a minimal two-agent team:
- Aeromedical Researcher (o3-deep-research with web search)
- Scientific Writer (gpt-5)

It runs deep research and then composes a long-form PRISMA-style systematic review
in multiple sectioned calls, appending sections into a single long document.
"""

import logging
from typing import List

from agents import Agent, Runner, RunConfig, WebSearchTool
from .agents_md import apply_guidelines_to_instructions

logger = logging.getLogger(__name__)


def create_aeromedical_research_agent() -> Agent:
    """Create an aeromedical-focused deep research agent."""
    instructions = (
        "You are an aeromedical research specialist. Conduct exhaustive, postgraduate-level "
        "literature research focused on aerospace medicine and aviation safety. Use web search "
        "to find peer-reviewed sources (PubMed, Cochrane, NEJM, JAMA, Lancet, FAA/EASA). "
        "Return concise but comprehensive research notes with in-line numeric citations [^1], [^2], ... "
        "and a reference list in APA 7th style at the end. Aim for high factual density and high reasoning."
    )

    return Agent(
        name="Aeromedical Deep Researcher",
        model="o3-deep-research-2025-06-26",
        instructions=apply_guidelines_to_instructions(instructions, role_label="Aeromedical Deep Researcher"),
        tools=[
            WebSearchTool(
                search_context_size="high",
            )
        ],
    )


def create_scientific_writer_agent() -> Agent:
    """Create a scientific writer agent for long-form composition."""
    writer_instructions = (
        "You are a scientific writer. Write long-form, postgraduate/doctoral-level scientific text "
        "with rigorous structure, formal academic tone, and PRISMA compliance where applicable. "
        "Use Markdown with H2 headings (##). Include in-line numeric citations that map to a References section. "
        "Use deep reasoning and ensure cohesion across sections."
    )

    return Agent(
        name="Scientific Writer",
        model="gpt-5",
        instructions=apply_guidelines_to_instructions(writer_instructions, role_label="Scientific Writer"),
        tools=[
            WebSearchTool(
                search_context_size="high",
            )
        ],
    )


def _build_prisma_section_plan(research_question: str) -> List[str]:
    """Return ordered section prompts for a PRISMA-style review."""
    return [
        f"Title and Abstract for a PRISMA systematic review on: {research_question}",
        "Introduction / Background (context, significance, key concepts)",
        "Methods (PRISMA): protocol, eligibility criteria, information sources, search strategy, selection process, data collection, risk of bias)",
        "Results: study selection (PRISMA flow narrative), study characteristics, qualitative and quantitative synthesis",
        "Discussion: principal findings, interpretation, clinical and operational implications in aeromedical context",
        "Limitations and Risk of Bias",
        "Conclusion and Recommendations",
        "References (APA 7th). Ensure all in-text citations are included."
    ]


async def run_deep_aeromedical_pipeline(research_question: str) -> str:
    """Run deep aeromedical research and compose a long PRISMA-style report.

    The function performs:
      1) Deep research using o3-deep-research with web search
      2) Long-form writing across multiple sections via sequential API calls
    Returns the concatenated Markdown document.
    """
    logger.info("Starting deep aeromedical research pipeline")

    # Stage 1: Deep research notes
    researcher = create_aeromedical_research_agent()
    research_cfg = RunConfig(model="o3-deep-research-2025-06-26", tracing_disabled=True)
    research_run = await Runner.run(researcher, research_question, run_config=research_cfg)
    research_material = getattr(research_run, "final_output", str(research_run))

    # Stage 2: Long-form writing by sections
    writer = create_scientific_writer_agent()
    writer_cfg = RunConfig(model="gpt-5", tracing_disabled=True)

    sections = _build_prisma_section_plan(research_question)
    assembled: List[str] = []

    for idx, section_spec in enumerate(sections, start=1):
        section_prompt = (
            f"Using the following research notes, write the section '{section_spec}'.\n\n"
            f"Research Question: {research_question}\n\n"
            f"Research Notes:\n{research_material}\n\n"
            "Requirements:\n"
            "- Formal academic tone suitable for scientific journals\n"
            "- In-line citations [^1], [^2], ... mapped to a final References section\n"
            "- Extensive detail and deep reasoning\n"
            "- Cohesion with previous sections (assume you have full context)\n"
            "- Length: maximize depth; target 1,000-2,000 words for this section\n"
        )

        logger.info("Generating section %d/%d: %s", idx, len(sections), section_spec)
        result = await Runner.run(writer, section_prompt, run_config=writer_cfg)
        section_text = getattr(result, "final_output", str(result))

        assembled.append(f"\n\n## {section_spec}\n\n{section_text}\n")

    final_doc = f"# PRISMA Systematic Review: {research_question}\n" + "".join(assembled)
    logger.info("Deep aeromedical research pipeline complete")
    return final_doc