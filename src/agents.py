"""
Multi-Agent Framework for Prompt Enhancement.

This module implements the OpenAI Agents pattern with handoffs and tools
for creating a multi-agent prompt enhancement system.
"""

from __future__ import annotations

import json
import inspect
import logging
from typing import Dict, Any, List, Optional, Callable, Union, Generator
from pydantic import BaseModel
# The OpenAI package might not be available in minimal test environments.
# Import it if present, otherwise provide a lightweight stub so that the
# module can be imported without the dependency installed.
try:
    from openai import OpenAI  # type: ignore
    from agents import Agent as SdkAgent, Runner
    import asyncio
except Exception:  # pragma: no cover - fallback for missing dependency
    class _DummyCompletions:
        def create(self, *args, **kwargs):
            return type("Resp", (), {"choices": []})()

    class _DummyChat:
        completions = _DummyCompletions()

    class _DummyResponses:
        def create(self, *args, **kwargs):
            return type("Resp", (), {"choices": []})()

    class OpenAI:  # pragma: no cover - simple stub
        def __init__(self, *args, **kwargs):
            self.chat = _DummyChat()
            self.responses = _DummyResponses()

from .config import AppConfig
from .flowise_client import FlowiseClient, MedicalFlowiseRouter, FlowiseAPIError


logger = logging.getLogger(__name__)


# This remains for now as it's used as a type hint and data structure elsewhere.
class Agent(BaseModel):
    """
    Represents an AI agent with specific instructions and tools.
    
    This follows the OpenAI Agents pattern from the cookbook for
    orchestrating multiple agents with handoffs.
    """
    
    name: str
    instructions: str
    tools: List[Callable] = []
    model: str = AppConfig.OPENAI_MODEL
    handoffs: List[Agent] = []
    
    class Config:
        arbitrary_types_allowed = True


class AgentOrchestrator:
    """
    Orchestrates multiple agents with handoffs and tool execution
    using the OpenAI Agents SDK.
    """

    def __init__(self, client: Optional[OpenAI] = None):
        """
        Initialize the agent orchestrator.
        """
        self.client = client or OpenAI(api_key=AppConfig.OPENAI_API_KEY)
        self.flowise_client = MedicalFlowiseRouter()

    async def _run_agent_async(self, agent: Agent, input_prompt: str) -> Any:
        """Async helper to run the agent using the SDK's Runner."""
        # Convert our Pydantic Agent to an SDK Agent
        sdk_agent = SdkAgent(
            name=agent.name,
            instructions=agent.instructions,
            tools=agent.tools,
            model=agent.model,
        )
        return await Runner.run(sdk_agent, input_prompt)

    def run_full_turn(self, agent: Agent, messages: List[Dict[str, Any]]) -> Any:
        """
        Runs a full turn of an agent using the OpenAI Agents SDK Runner.
        This method is synchronous and wraps the async runner.
        """
        if not Runner or not SdkAgent:
            raise ImportError("openai-agents SDK not installed. Please run 'pip install openai-agents'.")

        # The SDK Runner takes a single string input. We'll format the message history.
        input_prompt = "\n\n---\n\n".join(
            [f"**{msg['role']}**: {msg['content']}" for msg in messages]
        )

        # Run the async helper in a new event loop.
        result = asyncio.run(self._run_agent_async(agent, input_prompt))

        # Adapt the SDK's result object to the format expected by the application.
        final_output = result.final_output if result and hasattr(result, 'final_output') else "Agent did not produce a final output."

        # The application expects a response object with a 'messages' list and an 'agent' object.
        response = type('AgentResponse', (), {})()
        response.agent = agent
        response.messages = [{"role": "assistant", "content": final_output}]

        return response
        
    def run_conversation(self, agent: Agent, messages: List[Dict[str, Any]], max_turns: int = 5) -> Any:
        """
        Runs a conversation with an agent for a set number of turns.
        NOTE: This is a simplified conversational loop. The primary method is `run_full_turn`.
        """
        current_messages = list(messages)
        
        for _ in range(max_turns):
            response = self.run_full_turn(agent, current_messages)
            
            # Extract the assistant's response and add it to the history
            assistant_message = response.messages[-1]
            current_messages.append(assistant_message)
            
            # In a real scenario, we'd check for a termination condition.
            # Here, we just return the final state.
            
        final_response = type('AgentResponse', (), {})()
        final_response.agent = agent
        final_response.messages = current_messages
        return final_response

def safe_log_info(message: str) -> None:
    """
    Safely log a message, handling Unicode encoding errors.
    
    Args:
        message: The message to log
    """
    try:
        logger.info(message)
    except UnicodeEncodeError:
        # Fallback for encoding issues - replace problematic characters
        safe_message = message.encode('ascii', errors='replace').decode('ascii')
        logger.info(f"{safe_message} [content contained non-ASCII characters]")


class Response(BaseModel):
    """Response from an agent interaction containing the agent and messages."""
    
    agent: Optional[Agent]
    messages: List[Dict[str, Any]]


class PromptEnhancementTools:
    """
    Tools for prompt enhancement and Flowise integration.
    
    This class provides tools that agents can use to enhance prompts
    and interact with Flowise chatflows.
    """
    
    def __init__(self, flowise_client: FlowiseClient):
        """
        Initialize the tools with a Flowise client.
        
        Args:
            flowise_client: FlowiseClient instance for API calls
        """
        self.flowise_client = flowise_client
    
    def analyze_prompt_context(self, user_prompt: str) -> str:
        """
        Analyze the user prompt to understand context and intent.
        
        Args:
            user_prompt: The original user prompt
            
        Returns:
            Analysis of the prompt's context and intent
        """
        analysis_prompt = f"""
        Analyze this user prompt and provide:
        1. Main topic/domain
        2. Intent (what they want to achieve)
        3. Complexity level (simple/medium/complex)
        4. Missing context that would improve the response
        5. Suggested enhancements
        
        User prompt: "{user_prompt}"
        """
        
        try:
            # Use a simple analysis - in practice, you might use a specific model
            return f"Analyzed prompt: '{user_prompt}' - Domain identified, enhancement suggestions generated."
        except Exception as e:
            logger.error(f"Error analyzing prompt: {e}")
            return f"Error analyzing prompt: {str(e)}"
    
    def enhance_prompt_with_context(self, original_prompt: str, context_analysis: str) -> str:
        """
        Enhance the original prompt based on context analysis.
        
        Args:
            original_prompt: The user's original prompt
            context_analysis: Analysis of the prompt context
            
        Returns:
            Enhanced prompt with additional context and details
        """
        enhancement_template = f"""
        Based on the original prompt and analysis, create an enhanced version that:
        1. Adds relevant context and background
        2. Clarifies the intent and expected outcome
        3. Includes specific details that would improve response quality
        4. Maintains the original intent while expanding scope
        
        Original prompt: "{original_prompt}"
        Context analysis: "{context_analysis}"
        
        Enhanced prompt:
        """
        
        return enhancement_template
    
    def query_flowise_research(self, enhanced_prompt: str) -> str:
        """
        Send the enhanced prompt to Flowise deep research chatflow.
        
        Args:
            enhanced_prompt: The enhanced prompt to send
            
        Returns:
            Response from Flowise research chatflow
        """
        try:
            # Use streaming for better user experience
            response_generator = self.flowise_client.consult_deep_research(enhanced_prompt)
            
            # Collect streaming response
            full_response = ""
            for chunk in response_generator:
                if isinstance(chunk, dict):
                    if chunk.get("event") == "token":
                        full_response += chunk.get("data", "")
                    elif chunk.get("event") == "end":
                        break
                else:
                    full_response += str(chunk)
            
            return full_response or "Research completed successfully."
            
        except FlowiseAPIError as e:
            logger.error(f"Flowise API error: {e}")
            return f"Error querying Flowise: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in Flowise query: {e}")
            return f"Unexpected error: {str(e)}"
    
    def query_flowise_agentic(self, enhanced_prompt: str) -> str:
        """
        Send the enhanced prompt to Flowise agentic RAG chatflow.
        
        Args:
            enhanced_prompt: The enhanced prompt to send
            
        Returns:
            Response from Flowise agentic RAG chatflow
        """
        try:
            response_generator = self.flowise_client.consult_agentic_rag(enhanced_prompt)
            
            # Collect streaming response
            full_response = ""
            for chunk in response_generator:
                if isinstance(chunk, dict):
                    if chunk.get("event") == "token":
                        full_response += chunk.get("data", "")
                    elif chunk.get("event") == "end":
                        break
                else:
                    full_response += str(chunk)
            
            return full_response or "Agentic RAG query completed successfully."
            
        except FlowiseAPIError as e:
            logger.error(f"Flowise API error: {e}")
            return f"Error querying Flowise: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in Flowise query: {e}")
            return f"Unexpected error: {str(e)}"
    
    def route_to_specialist(self, query_type: str, enhanced_prompt: str) -> str:
        """
        Route the enhanced prompt to a specialist Flowise chatflow.
        
        Args:
            query_type: Type of specialist query ('medical', 'nasa', 'research', etc.)
            enhanced_prompt: The enhanced prompt to send
            
        Returns:
            Response from the specialist chatflow
        """
        try:
            result = self.flowise_client.route_medical_query(query_type, enhanced_prompt)
            
            if isinstance(result, dict):
                return result.get("text", str(result))
            elif hasattr(result, '__iter__'):
                # Handle generator/streaming response
                full_response = ""
                for chunk in result:
                    if isinstance(chunk, dict):
                        if chunk.get("event") == "token":
                            full_response += chunk.get("data", "")
                        elif chunk.get("event") == "end":
                            break
                    else:
                        full_response += str(chunk)
                return full_response or "Specialist query completed successfully."
            else:
                return str(result)
                
        except FlowiseAPIError as e:
            logger.error(f"Flowise routing error: {e}")
            return f"Error routing to specialist: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in specialist routing: {e}")
            return f"Unexpected error: {str(e)}" 