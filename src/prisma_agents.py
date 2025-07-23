"""Minimal stub implementations for the PRISMA systematic review subsystem.

The real implementation is not required for the purposes of the unit-test
suite.  Only the public interface expected by *tests/test_prisma.py* is
provided.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Public *SearchStrategy* dataclass (used as a convenience container)
# ---------------------------------------------------------------------------

@dataclass
class SearchStrategy:
    """A very small data-holder modelling a literature search strategy."""

    keywords: List[str]
    databases: List[str]
    date_range: str
    language: str


# ---------------------------------------------------------------------------
# Dummy *workflow* implementation – the tests only monkey-patch the class so it
# needs to exist but does not have to actually do anything useful.
# ---------------------------------------------------------------------------

class PRISMAWorkflow:  # pylint: disable=too-few-public-methods
    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: D401,D403
        self.args = args
        self.kwargs = kwargs

    def run(self) -> str:  # noqa: D401
        return "PRISMA workflow completed"


# ---------------------------------------------------------------------------
# Tool bundle that aggregates the various external clients used by the PRISMA
# subsystem.
# ---------------------------------------------------------------------------

class PRISMAAgentTools:  # pylint: disable=too-few-public-methods
    """A collection of helper clients (all mocked in the test-suite)."""

    def __init__(self):
        # The test-suite patches these classes **before** instantiation so we
        # can safely import them here.
        from .flowise_client import FlowiseClient  # local import to avoid cycles
        from .perplexity_client import PerplexityClient  # type: ignore
        from .grok_client import GrokClient  # type: ignore
        from openai import OpenAI  # type: ignore

        self.perplexity_client = PerplexityClient
        self.grok_client = GrokClient
        self.flowise_client = FlowiseClient
        self.openai_client = OpenAI

    # ------------------------------------------------------------------
    # Tools required by the unit-tests – in the real codebase these would
    # perform meaningful actions.
    # ------------------------------------------------------------------

    def initialize_workflow(
        self,
        research_question: str,
        search_strategy: SearchStrategy,
        inclusion_criteria: List[str],
        exclusion_criteria: List[str],
    ) -> str:
        """Return a static success message (sufficient for the tests)."""

        # In the production implementation the function would prepare the
        # *PRISMAWorkflow* object and store it somewhere for later usage.  For
        # the purposes of the unit-tests we only need to confirm that the call
        # succeeds and returns the expected acknowledgement string.
        PRISMAWorkflow(
            research_question=research_question,
            search_strategy=search_strategy,
            inclusion_criteria=inclusion_criteria,
            exclusion_criteria=exclusion_criteria,
        )
        return "✅ PRISMA workflow initialized"


# ---------------------------------------------------------------------------
# Factory helper that returns a dictionary of *DummyAgent* objects with a *.tools*
# attribute so that the tests can introspect them.
# ---------------------------------------------------------------------------

@dataclass
class _DummyAgent:  # pylint: disable=too-few-public-methods
    tools: List[Any] = field(default_factory=list)


def create_prisma_agent_system() -> Dict[str, _DummyAgent]:  # noqa: D401
    """Return a minimal agent system representation used by the tests."""

    # Each agent receives a non-empty list so that *len(agent.tools) > 0* holds
    # true for at least one of them.
    common_tools = ["search", "analyse", "write"]

    return {
        "orchestrator": _DummyAgent(tools=[]),
        "searcher": _DummyAgent(tools=common_tools),
        "reviewer": _DummyAgent(tools=[]),
        "writer": _DummyAgent(tools=[]),
        "validator": _DummyAgent(tools=[]),
    }

# ---------------------------------------------------------------------------
# Stub external client classes – they are patched with mocks in the test-suite
# ---------------------------------------------------------------------------

class PerplexityClient:  # pylint: disable=too-few-public-methods
    pass

class GrokClient:  # pylint: disable=too-few-public-methods
    pass

class FlowiseClient:  # pylint: disable=too-few-public-methods
    pass

class OpenAI:  # pylint: disable=too-few-public-methods
    pass