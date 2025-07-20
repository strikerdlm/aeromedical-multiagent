"""
Specialized Agents for Prompt Enhancement System.

This module defines the specific agents for the multi-agent prompt
enhancement application with advanced OpenAI model routing.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional

from agents import Agent, function_tool
from .openai_enhanced_client import EnhancedOpenAIClient, create_enhanced_openai_client
from .config import OpenAIModelsConfig, AppConfig


logger = logging.getLogger(__name__)


# Convert class methods to standalone functions for OpenAI agents SDK compatibility
@function_tool
def process_with_advanced_routing(enhanced_prompt: str, original_question: str) -> str:
    """
    Process the enhanced prompt using advanced OpenAI model routing.
    
    Args:
        enhanced_prompt: The enhanced prompt to process
        original_question: The original user question to guide routing
        
    Returns:
        Response from the appropriate OpenAI model (o3-deep-research or o3)
    """
    try:
        logger.info("Processing with advanced OpenAI model routing")
        openai_client = create_enhanced_openai_client()
        response = openai_client.route_and_process(enhanced_prompt, original_question)
        logger.info("Advanced routing processing completed successfully")
        return response
        
    except Exception as e:
        logger.error(f"Error in advanced routing: {e}")
        return f"Error processing with advanced routing: {str(e)}"

@function_tool
def force_deep_research_processing(enhanced_prompt: str) -> str:
    """
    Force processing with o3-deep-research model.
    
    Args:
        enhanced_prompt: The enhanced prompt to process
        
    Returns:
        Response from o3-deep-research model
    """
    try:
        logger.info("Force processing with o3-deep-research")
        openai_client = create_enhanced_openai_client()
        return openai_client.process_with_deep_research(enhanced_prompt)
    except Exception as e:
        logger.error(f"Error in deep research processing: {e}")
        return f"Error processing with deep research: {str(e)}"

@function_tool
def force_o3_web_search_processing(enhanced_prompt: str) -> str:
    """
    Force processing with o3 + web search.
    
    Args:
        enhanced_prompt: The enhanced prompt to process
        
    Returns:
        Response from o3 with web search
    """
    try:
        logger.info("Force processing with o3 + web search")
        openai_client = create_enhanced_openai_client()
        return openai_client.process_with_o3_and_web_search(enhanced_prompt)
    except Exception as e:
        logger.error(f"Error in o3 web search processing: {e}")
        return f"Error processing with o3 + web search: {str(e)}"


def create_triage_agent(analyzer_agent: Agent) -> Agent:
    """
    Create a Triage Agent for initial user interaction.
    
    This agent handles initial user requests and routes them to the analyzer.
    """
    @function_tool
    def escalate_to_human(summary: str) -> str:
        """Escalate complex issues to human assistance."""
        logger.info(f"Escalating to human: {summary}")
        return f"Escalated to human assistance: {summary}"
    
    instructions = """
    You are a Triage Agent. Your role is to greet users and route their request to the Prompt Analyzer Agent for enhancement and processing. Almost all requests should be handed off.
    """
    
    return Agent(
        name="Triage Agent",
        instructions=instructions,
        handoffs=[analyzer_agent],
        tools=[escalate_to_human],
        model=OpenAIModelsConfig.GPT4_MINI.model_name
    )

def create_analyzer_agent(processor_agent: Agent) -> Agent:
    """
    Creates the agent that analyzes and enhances the user's prompt.
    """
    instructions = """
    You are a Prompt Analyzer and Enhancer. You will receive a user prompt from the Triage Agent.
    Your task is to analyze the prompt's domain, intent, and complexity, and then rewrite it to be significantly more detailed, contextual, and structured for an advanced AI model.
    Once you have the enhanced prompt, you MUST hand it off to the Prompt Processor Agent.
    You should also pass the original user prompt along with the enhanced one to the processor.
    """
    return Agent(
        name="Prompt Analyzer Agent",
        instructions=instructions,
        handoffs=[processor_agent],
        model=OpenAIModelsConfig.GPT4_MINI.model_name
    )

def create_processor_agent(tools: List[callable]) -> Agent:
    """
    Create the Prompt Processor Agent.
    
    This agent receives enhanced prompts and processes them through
    advanced OpenAI models with intelligent routing.
    """
    instructions = """
    You are a Prompt Processing Specialist. You receive an enhanced prompt and the original user question from the Analyzer Agent.
    Your job is to call the `process_with_advanced_routing` tool, passing it both the enhanced prompt and the original question.
    This tool will intelligently route the request to the best AI model.
    You also have tools to force processing with a specific model if needed.
    """
    return Agent(
        name="Prompt Processor Agent",
        instructions=instructions,
        tools=tools,
        model=OpenAIModelsConfig.GPT4_MINI.model_name
    )

def create_prompt_enhancement_system() -> Dict[str, Agent]:
    """
    Create the complete prompt enhancement system with all agents.
    
    Returns:
        Dictionary mapping agent names to agent instances
    """
    # Create agents in reverse order of handoff using the standalone functions
    processor_agent = create_processor_agent(
        tools=[
            process_with_advanced_routing,
            force_deep_research_processing,
            force_o3_web_search_processing,
        ]
    )
    analyzer_agent = create_analyzer_agent(processor_agent)
    triage_agent = create_triage_agent(analyzer_agent)
    
    agents = {
        "triage": triage_agent,
        "analyzer": analyzer_agent,
        "processor": processor_agent,
    }
    
    return agents


# Example usage and testing functions
def test_agent_handoffs() -> None:
    """Test the agent handoff functionality."""
    # Create agents in reverse order of handoff using the standalone functions
    processor_agent = create_processor_agent(
        tools=[
            process_with_advanced_routing,
            force_deep_research_processing,
            force_o3_web_search_processing,
        ]
    )
    analyzer_agent = create_analyzer_agent(processor_agent)
    triage_agent = create_triage_agent(analyzer_agent)
    
    # Test handoff functions
    # The handoff logic is now handled by the Agent class itself
    # We can just call the tools directly or create a dummy Agent for testing
    # For simplicity, let's just call the tools directly
    
    test_prompt = "Tell me about quantum computing and its applications in cryptography"
    
    # For testing, we can directly call the standalone functions
    logger.info(f"Test prompt: {test_prompt}")
    
    # Test direct function call
    try:
        response = process_with_advanced_routing(test_prompt, test_prompt)
        logger.info(f"Test response: {response[:100] if response else 'No response'}...")
    except Exception as e:
        logger.error(f"Test failed: {e}")


if __name__ == "__main__":
    # Set up logging for testing
    logging.basicConfig(level=logging.INFO)
    
    # Test the system
    test_agent_handoffs()
    
    # Create full system
    system = create_prompt_enhancement_system()
    logger.info(f"Created system with agents: {list(system.keys())}") 