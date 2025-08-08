from __future__ import annotations

"""Citation Review Orchestrator

Provides an async helper function to run the Citation Review Agent against a
research report and return the verified APA reference list.
"""

import logging
from typing import Any, Optional, List

from agents import Runner, RunConfig

from .citation_review_agent import create_citation_review_agent, CitationList

logger = logging.getLogger(__name__)


async def run_citation_review(
    report_markdown: str,
    verbose: bool = False,
) -> List[str]:
    """Run the citation review pipeline.

    Args:
        report_markdown: The full text (or Markdown) of the research report
            containing inline citations and a reference list.
        verbose: If True, prints streaming events for debugging.

    Returns:
        A list of verified, APA-formatted citation strings.
    """

    agent = create_citation_review_agent()

    run_config = RunConfig(
        # The agent already specifies its preferred model (gpt-5) but this can
        # be overridden here if required.
        tracing_disabled=True,
    )

    logger.info("Starting citation verification / redaction…")

    try:
        result = await Runner.run(
            agent,
            report_markdown,
            run_config=run_config,
        )
    except Exception as e:
        logger.error(f"Citation review failed: {e}")
        raise

    final_output = result.final_output

    if isinstance(final_output, CitationList):
        citations = final_output.citations
    else:
        # Fallback: If the agent did not return a structured object, assume it
        # returned raw markdown list as string
        if isinstance(final_output, str):
            citations = [line.strip() for line in final_output.splitlines() if line.strip()]
        else:
            raise TypeError("Citation review agent returned unexpected type")

    if verbose:
        logger.debug("Verified citations:")
        for c in citations:
            logger.debug(c)

    return citations
