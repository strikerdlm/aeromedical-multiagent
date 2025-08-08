"""
Orchestrates the end-to-end research pipeline.
"""
from __future__ import annotations

import logging
from typing import Dict, Any, Optional

from agents import Runner, RunConfig, ModelSettings
from .query_optimizer import create_query_optimizer_pipeline, ClarificationRequest, ResearchInstructions
from .research_agents import create_deep_research_agent

logger = logging.getLogger(__name__)

async def run_research_pipeline(
    initial_query: str,
    mock_answers: Optional[Dict[str, str]] = None,
    verbose: bool = False,
) -> Any:
    """
    Runs the full research pipeline.

    1. Starts with the query optimizer pipeline to refine the user query.
    2. If clarification is needed, it can use mock answers for non-interactive mode.
    3. Takes the final research instructions and runs the deep research agent.

    Args:
        initial_query: The raw user query.
        mock_answers: A dictionary of answers to potential clarification questions.
        verbose: If True, prints detailed event information.

    Returns:
        The final output from the deep research agent.
    """
    optimizer_agent = create_query_optimizer_pipeline()

    # --- Stage 1: Query Optimization ---
    logger.info("Starting query optimization pipeline...")
    optimizer_stream = Runner.run_streamed(
        optimizer_agent,
        initial_query,
        run_config=RunConfig(tracing_disabled=True),
    )

    final_instructions = None
    async for ev in optimizer_stream.stream_events():
        if getattr(ev, "item", None) and isinstance(ev.item, ClarificationRequest):
            reply = []
            for q in ev.item.questions:
                ans = (mock_answers or {}).get(q, "No preference.")
                reply.append(f"**{q}**\n{ans}")
            optimizer_stream.send_user_message("\\n\\n".join(reply))
            continue
        if verbose:
            print(ev)

    # The final_output is available after the stream completes.
    final_output = optimizer_stream.final_output
    if isinstance(final_output, ResearchInstructions):
        final_instructions = final_output
    else:
        logger.error("Query optimization did not produce ResearchInstructions.")
        # Fallback to a simple prompt if optimization fails
        final_instructions = ResearchInstructions(
            detailed_prompt=f"Conduct a comprehensive research on the following topic: {initial_query}"
        )

    if not final_instructions:
        raise Exception("Could not generate research instructions.")

    logger.info("Query optimization finished. Moving to deep research.")
    logger.debug(f"Detailed prompt: {final_instructions.detailed_prompt}")

    # --- Stage 2: Deep Research ---
    research_agent = create_deep_research_agent()

    # Configure run settings for deep research (reasoning effort handled via agent prompt)
    research_run_config = RunConfig(
        model=final_instructions.target_model,
        tracing_disabled=True,
    )

    logger.info(f"Starting deep research with model: {final_instructions.target_model}")

    # --- Model Fallback Logic ---
    fallback_models = ["gpt-5", "o4-mini-deep-research"]
    models_to_try = [final_instructions.target_model] + fallback_models

    research_result = None
    last_exception = None

    for model in models_to_try:
        try:
            logger.info(f"Attempting research with model: {model}")
            research_run_config.model = model

            result = await Runner.run(
                research_agent,
                final_instructions.detailed_prompt,
                run_config=research_run_config,
            )
            research_result = result.final_output
            break  # Success, exit loop
        except Exception as e:
            logger.warning(f"Research with model {model} failed: {e}")
            last_exception = e
            continue

    if research_result is None:
        logger.error("All research models failed.")
        raise last_exception or Exception("Unknown error during research.")

    return research_result
