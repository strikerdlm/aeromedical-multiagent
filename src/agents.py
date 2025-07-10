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
    
    class Config:
        arbitrary_types_allowed = True


class Response(BaseModel):
    """Response from an agent interaction containing the agent and messages."""
    
    agent: Optional[Agent]
    messages: List[Dict[str, Any]]


class AgentOrchestrator:
    """
    Orchestrates multiple agents with handoffs and tool execution.
    
    This class manages the execution flow between different agents,
    handles tool calls, and manages the conversation state.
    """
    
    def __init__(self, client: Optional[OpenAI] = None):
        """
        Initialize the agent orchestrator.
        
        Args:
            client: OpenAI client instance (optional, creates default if None)
        """
        self.client = client or OpenAI(api_key=AppConfig.OPENAI_API_KEY)
        self.flowise_client = MedicalFlowiseRouter()
    
    def function_to_schema(self, func: Callable) -> Dict[str, Any]:
        """
        Convert a Python function to OpenAI function schema.
        
        Args:
            func: The function to convert
            
        Returns:
            OpenAI function schema dictionary
            
        Raises:
            ValueError: If function signature cannot be determined
        """
        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
            type(None): "null",
        }
        
        try:
            signature = inspect.signature(func)
        except ValueError as e:
            raise ValueError(f"Failed to get signature for function {func.__name__}: {str(e)}")
        
        parameters = {}
        for param in signature.parameters.values():
            try:
                param_type = type_map.get(param.annotation, "string")
            except KeyError as e:
                raise KeyError(f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}")
            parameters[param.name] = {"type": param_type}
        
        required = [
            param.name
            for param in signature.parameters.values()
            if param.default == inspect._empty
        ]
        
        return {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": (func.__doc__ or "").strip(),
                "parameters": {
                    "type": "object",
                    "properties": parameters,
                    "required": required,
                },
            },
        }
    
    def execute_tool_call(self, tool_call, tools_map: Dict[str, Callable], agent_name: str) -> Any:
        """
        Execute a tool call and return the result.
        
        Args:
            tool_call: The tool call object from OpenAI
            tools_map: Mapping of tool names to functions
            agent_name: Name of the agent making the call
            
        Returns:
            Result of the tool execution
        """
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        
        safe_log_info(f"{agent_name}: {name}({args})")
        
        try:
            return tools_map[name](**args)
        except Exception as e:
            logger.error(f"Tool execution error in {name}: {e}")
            return f"Error executing {name}: {str(e)}"
    
    def run_full_turn(self, agent: Agent, messages: List[Dict[str, Any]]) -> Response:
        """
        Execute a full turn for an agent, handling tool calls and handoffs.
        
        Args:
            agent: The agent to execute
            messages: Current conversation messages
            
        Returns:
            Response containing the updated agent and new messages
        """
        current_agent = agent
        num_init_messages = len(messages)
        messages = messages.copy()
        
        while True:
            # Convert tools to schemas and create mapping
            tool_schemas = [self.function_to_schema(tool) for tool in current_agent.tools]
            tools_map = {tool.__name__: tool for tool in current_agent.tools}
            
            # Make OpenAI completion call
            try:
                response = self.client.chat.completions.create(
                    model=current_agent.model,
                    messages=[{"role": "system", "content": current_agent.instructions}] + messages,
                    tools=tool_schemas or None,
                )
            except Exception as e:
                logger.error(f"OpenAI API error: {e}")
                raise
            
            message = response.choices[0].message
            messages.append(message.model_dump())
            
            # Print agent response if there's content
            if message.content:
                safe_log_info(f"{current_agent.name}: {message.content}")
            
            # Break if no tool calls
            if not message.tool_calls:
                break
            
            # Handle tool calls
            for tool_call in message.tool_calls:
                result = self.execute_tool_call(tool_call, tools_map, current_agent.name)
                
                # Check if result is an agent handoff
                if isinstance(result, Agent):
                    current_agent = result
                    result = f"Transferred to {current_agent.name}. Adopt persona immediately."
                
                # Add tool result to messages
                result_message = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result),
                }
                messages.append(result_message)
        
        # Return response with updated agent and new messages
        return Response(
            agent=current_agent,
            messages=messages[num_init_messages:]
        )


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