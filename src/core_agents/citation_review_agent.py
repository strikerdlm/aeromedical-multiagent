from __future__ import annotations

"""Citation Review Agent

This module defines the agent responsible for verifying and redacting citation
lists produced by other agents. It ensures that every reference is:
1. Verifiable through an online lookup (web search).
2. Accurately represented using the latest APA (7th edition) formatting rules.
3. Removed if it cannot be verified, is duplicated, or is not a peer-reviewed
   scholarly source.
4. Export-ready as GitHub-flavoured Markdown so it can be written directly to a
   `.md` file or injected into downstream pipelines.

The agent uses a large-context model to comfortably ingest entire research
reports (which can be tens of thousands of words long) and a WebSearchTool to
perform real-time verification of the references.
"""

import logging
from typing import List

from pydantic import BaseModel

# The core "agents" package is assumed to be available in the runtime
# environment just like the other core_agent modules.
from agents import Agent, WebSearchTool

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic output model
# ---------------------------------------------------------------------------

class CitationList(BaseModel):
    """Structured list of APA formatted citations."""

    citations: List[str]


# ---------------------------------------------------------------------------
# Agent factory
# ---------------------------------------------------------------------------

def create_citation_review_agent() -> Agent:
    """Create and return the citation review / redaction agent.

    The agent consumes a full research report (markdown or plain text) and
    outputs ONLY the final list of verified APA citations as Markdown (one per
    line starting with a numerical bullet).
    """

    CITATION_REVIEW_INSTRUCTIONS = r"""
You are an elite citation-verification assistant.

Your task is to review the complete research document supplied by the user,
validate every reference, and return ONLY the final list of citations that meet
ALL of the following criteria:

1. The reference can be located through a real-time web search and its metadata
   (authors, year, title, journal / conference, volume, issue, pages, DOI or URL)
   can be confirmed.
2. It is a legitimate, peer-reviewed scholarly source (journal article, book
   chapter, conference proceeding, official guideline, etc.). Exclude blog
   posts, opinion pieces, pre-prints without peer review, or unverifiable
   documents.
3. The formatted entry strictly follows the latest APA Style (7th edition):
   • Use hanging indent (not required in Markdown but keep the line intact).
   • List up to 20 authors. Use an ampersand before the final author’s name.
   • Provide DOIs as https URLs when available.
   • Capitalise titles sentence-style.
   • Italicise journal / book titles using *asterisks* (GitHub Markdown).
4. Remove duplicates and renumber citations sequentially starting from 1.
5. Output rules:
   • Return the list as GitHub-flavoured Markdown: each citation on its own line
     prefixed with a numerical list marker, e.g., `1.` `2.` etc.
   • Do NOT output anything else—no commentary, no explanation—only the
     verified reference list.
"""

    agent = Agent(
        name="Citation Review Agent",
        model="gpt-5",  # use GPT-5 for reporting/validation
        instructions=CITATION_REVIEW_INSTRUCTIONS,
        output_type=CitationList,
        tools=[
            WebSearchTool(search_context_size="high"),
        ],
    )

    logger.debug("Citation Review Agent created.")
    return agent
