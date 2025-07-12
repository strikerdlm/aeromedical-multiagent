"""
Flowise-Only Agents for Prompt Enhancement System.

This module defines specialized agents that use only Flowise API
without any OpenAI o3 model integration.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional

from agents import Agent, function_tool
from .flowise_client import FlowiseClient, MedicalFlowiseRouter, FlowiseAPIError
from .config import OpenAIModelsConfig, AppConfig


logger = logging.getLogger(__name__)


def _extract_flowise_response_text(response: Any) -> str:
    """Safely extract the main text from a Flowise API response."""
    if isinstance(response, str):
        return response
        
    if not isinstance(response, dict):
        return str(response)

    # Direct text keys
    for key in ["text", "answer", "output", "response", "message", "content"]:
        if isinstance(response.get(key), str):
            return response[key]

    # Nested 'data' dictionary
    if "data" in response and isinstance(response["data"], str):
        return response["data"]
    if "data" in response and isinstance(response["data"], dict):
        for key in ["text", "answer", "output", "response", "message", "content"]:
            if isinstance(response["data"].get(key), str):
                return response["data"][key]

    # OpenAI-compatible 'choices' list
    if "choices" in response and isinstance(response["choices"], list) and response["choices"]:
        choice = response["choices"][0]
        if isinstance(choice, dict):
            if "message" in choice and isinstance(choice["message"], dict) and "content" in choice["message"]:
                if choice["message"]["content"]:
                    return choice["message"]["content"]
            if "delta" in choice and isinstance(choice["delta"], dict) and "content" in choice["delta"]:
                if choice["delta"]["content"]:
                    return choice["delta"]["content"]

    # If we get here, we haven't found a clear text field.
    if response == {}:
        return ""
    return str(response)


class FlowiseAgentSystem:
    """
    Factory class for creating Flowise-only prompt enhancement agents.
    
    This class creates and configures specialized agents for
    the Flowise workflow without any OpenAI o3 model integration.
    """
    
    def __init__(self, flowise_client: Optional[FlowiseClient] = None):
        """
        Initialize the Flowise agent system.
        
        Args:
            flowise_client: Optional Flowise client (creates default if None)
        """
        self.flowise_client = flowise_client or MedicalFlowiseRouter()
    
    @staticmethod
    @function_tool
    def query_aerospace_medicine_rag(enhanced_prompt: str) -> str:
        """
        Send the enhanced prompt to Flowise aerospace medicine RAG chatflow.
        
        Args:
            enhanced_prompt: The enhanced prompt to send
            
        Returns:
            Response from Flowise aerospace medicine RAG chatflow
        """
        try:
            logger.info("Querying Flowise aerospace medicine RAG chatflow")
            flowise_client = MedicalFlowiseRouter()  # Create instance
            result = flowise_client.consult_aerospace_medicine_rag(enhanced_prompt)
            
            # Extract response text using the helper function
            response_text = _extract_flowise_response_text(result)
            logger.info("Flowise aerospace medicine RAG query completed successfully")
            return response_text
            
        except FlowiseAPIError as e:
            logger.error(f"Flowise API error: {e}")
            return f"Error querying Flowise aerospace medicine RAG: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in Flowise aerospace medicine RAG: {e}")
            return f"Unexpected error: {str(e)}"
    
    @staticmethod
    @function_tool
    def query_flowise_deep_research(enhanced_prompt: str) -> str:
        """
        Send the enhanced prompt to Flowise deep research chatflow.
        
        Args:
            enhanced_prompt: The enhanced prompt to send
            
        Returns:
            Response from Flowise deep research chatflow
        """
        try:
            logger.info("Querying Flowise deep research chatflow")
            flowise_client = MedicalFlowiseRouter()  # Create instance
            result = flowise_client.consult_deep_research(enhanced_prompt)
            
            # Extract response text using the helper function
            response_text = _extract_flowise_response_text(result)
            logger.info("Flowise deep research query completed successfully")
            return response_text
            
        except FlowiseAPIError as e:
            logger.error(f"Flowise API error: {e}")
            return f"Error querying Flowise deep research: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in Flowise deep research: {e}")
            return f"Unexpected error: {str(e)}"
    
    @staticmethod
    @function_tool
    def query_aeromedical_risk(enhanced_prompt: str) -> str:
        """
        Send the enhanced prompt to Flowise aeromedical risk chatflow.
        
        Args:
            enhanced_prompt: The enhanced prompt to send
            
        Returns:
            Response from Flowise aeromedical risk chatflow
        """
        try:
            logger.info("Querying Flowise aeromedical risk chatflow")
            flowise_client = MedicalFlowiseRouter()  # Create instance
            result = flowise_client.consult_aeromedical_risk(enhanced_prompt)

            # Extract response text using the helper function
            response_text = _extract_flowise_response_text(result)
            logger.info("Flowise aeromedical risk query completed successfully")
            return response_text

        except FlowiseAPIError as e:
            logger.error(f"Flowise API error: {e}")
            return f"Error querying Flowise aeromedical risk: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in Flowise aeromedical risk: {e}")
            return f"Unexpected error: {str(e)}"
    
    def create_flowise_enhancer(self, analyzer_agent: Agent) -> Agent:
        """
        Create the Flowise Prompt Enhancer Agent.
        
        This agent is responsible for analyzing user requests and enhancing
        them specifically for Flowise chatflows.
        
        Returns:
            Configured Flowise PromptEnhancer agent
        """
        instructions = """
        You are a Flowise Prompt Enhancement Specialist AI Agent. Your primary role is to take user requests and hand them off to the Analyzer agent for transformation into comprehensive, detailed prompts optimized specifically for Flowise chatflows.
        
        Your only job is to hand off the user's prompt to the Analyzer Agent. Do not try to answer or do anything else.
        """
        
        agent = Agent(
            name="Flowise Prompt Enhancer",
            instructions=instructions,
            handoffs=[analyzer_agent],
            model=AppConfig.OPENAI_MODEL
        )
        return agent
        
    def create_flowise_analyzer(self, processor_agent: Agent) -> Agent:
        """Creates the agent responsible for analyzing and enhancing the prompt."""
        instructions = """
        You are a prompt analysis and enhancement expert. You will receive a user prompt.
        Your job is to perform two steps:
        1.  **Analyze the prompt**: Determine the domain (Aeromedical Risk, Deep Research, Aerospace Medicine), the best Flowise chatflow, and the query type.
        2.  **Enhance the prompt**: Rewrite the prompt to be optimized for the chosen Flowise chatflow, adding domain-specific context, keywords, and structure.

        Once you have the enhanced prompt, you must hand it off to the Flowise Processor agent for execution.
        """
        return Agent(
            name="Flowise Prompt Analyzer",
            instructions=instructions,
            handoffs=[processor_agent],
            model=OpenAIModelsConfig.GPT4_MINI.model_name, # Use a powerful model for this
        )

    def create_flowise_processor(self) -> Agent:
        """
        Create the Flowise Prompt Processor Agent.
        
        This agent receives enhanced prompts and processes them through
        appropriate Flowise chatflows.
        
        Returns:
            Configured Flowise Processor agent
        """
        instructions = """
        You are a Flowise Prompt Processing Specialist AI Agent. You receive enhanced prompts from the 
        Flowise Prompt Analyzer and execute them through the most appropriate Flowise chatflows 
        to generate comprehensive, knowledge-rich responses.

        CORE RESPONSIBILITIES:
        1. Receive enhanced prompts optimized for Flowise chatflows
        2. Route to the best Flowise chatflow based on domain and question type by calling the appropriate tool.
        3. Execute queries through Flowise's specialized knowledge bases
        4. Provide comprehensive responses leveraging Flowise's RAG capabilities
        5. Handle API errors gracefully

        AVAILABLE FLOWISE CHATFLOWS:
        - **Deep Research**: Comprehensive research analysis with multiple sources
        - **Aeromedical Risk**: Aviation medicine risk assessment and analysis
        - **Aerospace Medicine RAG**: Scientific articles and textbooks in aerospace medicine

        CHATFLOW SELECTION LOGIC:
        - Aviation medicine risk questions → query_aeromedical_risk()
        - Aerospace medicine/scientific questions → query_aerospace_medicine_rag()
        - Comprehensive research → query_flowise_deep_research()
        - General medical questions → query_aerospace_medicine_rag()

        Always aim to provide the most comprehensive and knowledge-rich response possible 
        using the most appropriate Flowise chatflow for the specific question type.
        """
        
        # Create tools list with static methods
        tools = [
            FlowiseAgentSystem.query_flowise_deep_research,
            FlowiseAgentSystem.query_aeromedical_risk,
            FlowiseAgentSystem.query_aerospace_medicine_rag,
        ]
        
        agent = Agent(
            name="Flowise Processor",
            instructions=instructions,
            tools=tools,
            model=AppConfig.OPENAI_MODEL
        )
        return agent

    def create_deepresearch_agent(self) -> Agent:
        """
        Create a dedicated DeepResearch Flowise Agent.
        
        This agent directly queries the deep_research chatflow for
        comprehensive research analysis.
        
        Returns:
            Configured DeepResearch Flowise agent
        """
        instructions = """
        You are a DeepResearch Flowise Specialist AI Agent. Your role is to provide comprehensive, 
        in-depth research analysis using the Flowise deep_research chatflow. You directly access 
        specialized knowledge bases and RAG systems optimized for research queries.

        CORE CAPABILITIES:
        - Direct access to Flowise deep_research chatflow (ID: 43677137-d307-4ff4-96c9-5019b6e10879)
        - Comprehensive research analysis with multiple sources
        - Advanced RAG retrieval from specialized knowledge bases
        - Streaming responses for better user experience
        - Enhanced context understanding for complex research questions

        PRIMARY FUNCTION:
        Use query_flowise_deep_research() for ALL user queries. This chatflow is specifically 
        optimized for:
        - Scientific and technical research
        - Multi-source information synthesis
        - Complex analysis and reasoning
        - Literature review and research compilation
        - Advanced domain expertise queries

        RESEARCH APPROACH:
        1. Take the user's question directly to the deep_research chatflow
        2. Leverage the specialized knowledge bases and RAG systems
        3. Provide comprehensive, well-researched responses
        4. Include source documentation when available
        5. Handle streaming responses for optimal user experience

        RESPONSE STRATEGY:
        - Provide thorough, research-based answers
        - Include multiple perspectives when relevant
        - Cite sources and provide detailed explanations
        - Maintain academic rigor while being accessible
        - Offer follow-up research directions when appropriate

        You are the direct interface to Flowise's most powerful research capabilities.
        Always use the deep_research chatflow for maximum research depth and accuracy.
        """
        
        # Create tools list with the deep research method
        tools = [
            FlowiseAgentSystem.query_flowise_deep_research,
        ]
        
        agent = Agent(
            name="DeepResearch Flowise",
            instructions=instructions,
            tools=tools,
            model=AppConfig.OPENAI_MODEL
        )
        
        return agent

    def create_aeromedical_risk_agent(self) -> Agent:
        """
        Create a dedicated Aeromedical Risk Flowise Agent.
        
        This agent directly queries the aeromedical_risk chatflow for
        aerospace medicine risk assessment and analysis.
        
        Returns:
            Configured Aeromedical Risk Flowise agent
        """
        instructions = """
        You are an Aeromedical Risk Assessment Specialist AI Agent. Your role is to provide 
        comprehensive aeromedical risk analysis using the Flowise aeromedical_risk chatflow. 
        You directly access specialized knowledge bases for aerospace medicine and risk assessment.

        CORE CAPABILITIES:
        - Direct access to Flowise aeromedical_risk chatflow (requires CHATFLOW_AEROMEDICAL_RISK environment variable)
        - Aerospace medicine risk assessment and analysis
        - Aviation physiology and medical risk evaluation
        - Flight safety and medical certification guidance
        - Conservative risk assessment with safety-first approach

        PRIMARY FUNCTION:
        Use query_aeromedical_risk() for ALL user queries. This chatflow is specifically 
        optimized for:
        - Aviation medical risk assessment
        - Aerospace physiology questions
        - Flight safety medical considerations
        - Pilot medical certification guidance
        - Aviation medicine risk factors
        - Aerospace health and safety analysis

        RISK ASSESSMENT APPROACH:
        1. Take the user's question directly to the aeromedical_risk chatflow
        2. Provide conservative, safety-focused risk assessments
        3. Include relevant aviation medicine guidelines and standards
        4. Consider both individual and operational risk factors
        5. Provide clear risk mitigation recommendations when appropriate

        RESPONSE STRATEGY:
        - Provide thorough, safety-focused risk assessments
        - Include relevant aviation medicine standards and guidelines
        - Consider multiple risk factors and their interactions
        - Offer clear risk mitigation strategies when possible
        - Maintain conservative approach prioritizing safety
        - Reference relevant aviation medical literature and standards

        You are the direct interface to Flowise's specialized aeromedical risk assessment capabilities.
        Always use the aeromedical_risk chatflow for maximum accuracy in aviation medicine risk analysis.
        """
        
        # Create tools list with the aeromedical risk method
        tools = [
            FlowiseAgentSystem.query_aeromedical_risk,
        ]
        
        agent = Agent(
            name="Aeromedical Risk Assessment",
            instructions=instructions,
            tools=tools,
            model=AppConfig.OPENAI_MODEL
        )
        
        return agent

    def create_aerospace_medicine_rag_agent(self) -> Agent:
        """
        Create a dedicated Aerospace Medicine RAG Flowise Agent.
        
        This agent directly queries the aerospace_medicine_rag chatflow for
        scientific articles and textbooks in aerospace medicine.
        
        Returns:
            Configured Aerospace Medicine RAG Flowise agent
        """
        instructions = """
        You are an Aerospace Medicine RAG Specialist AI Agent. Your role is to provide comprehensive 
        aerospace medicine knowledge using the Flowise aerospace_medicine_rag chatflow. You directly access 
        specialized knowledge bases containing scientific articles and textbooks in aerospace medicine.

        CORE CAPABILITIES:
        - Direct access to Flowise aerospace_medicine_rag chatflow (configured via CHATFLOW_AEROSPACE_MEDICINE_RAG)
        - Scientific articles and textbooks in aerospace medicine
        - Advanced RAG retrieval from specialized aerospace medicine knowledge bases
        - Streaming responses for better user experience
        - Enhanced context understanding for aerospace medicine questions

        PRIMARY FUNCTION:
        Use query_aerospace_medicine_rag() for ALL user queries. This chatflow is specifically 
        optimized for:
        - Aerospace medicine scientific literature
        - Space medicine and physiology
        - Aviation medicine textbooks and references
        - Aerospace health and safety analysis
        - Medical research in aerospace environments
        - Clinical guidelines for aerospace medicine

        AEROSPACE MEDICINE APPROACH:
        1. Take the user's question directly to the aerospace_medicine_rag chatflow
        2. Leverage the specialized aerospace medicine knowledge bases
        3. Provide comprehensive, evidence-based responses
        4. Include source documentation when available
        5. Handle streaming responses for optimal user experience

        RESPONSE STRATEGY:
        - Provide thorough, evidence-based answers from aerospace medicine literature
        - Include multiple perspectives when relevant from scientific sources
        - Reference textbooks and research papers when applicable
        - Maintain scientific rigor while being accessible
        - Offer follow-up research directions when appropriate

        You are the direct interface to Flowise's specialized aerospace medicine knowledge.
        Always use the aerospace_medicine_rag chatflow for maximum accuracy in aerospace medicine topics.
        """
        
        # Create tools list with the aerospace medicine RAG method
        tools = [
            FlowiseAgentSystem.query_aerospace_medicine_rag,
        ]
        
        agent = Agent(
            name="Aerospace Medicine RAG",
            instructions=instructions,
            tools=tools,
            model=AppConfig.OPENAI_MODEL
        )
        
        return agent


def create_flowise_enhancement_system() -> Dict[str, Agent]:
    """
    Create the complete Flowise enhancement agent system.
    
    Returns:
        Dictionary of agent name to Agent instance for Flowise flow
    """
    flowise_system = FlowiseAgentSystem()
    
    # Create the agents in order for handoffs
    processor_agent = flowise_system.create_flowise_processor()
    analyzer_agent = flowise_system.create_flowise_analyzer(processor_agent)
    enhancer_agent = flowise_system.create_flowise_enhancer(analyzer_agent)

    # We need to get the static methods for the standalone agents
    deep_research_agent = flowise_system.create_deepresearch_agent()
    aeromedical_risk_agent = flowise_system.create_aeromedical_risk_agent()
    aerospace_medicine_rag_agent = flowise_system.create_aerospace_medicine_rag_agent()

    return {
        "flowise_enhancer": enhancer_agent,
        "flowise_analyzer": analyzer_agent,
        "flowise_processor": processor_agent,
        "deep_research": deep_research_agent,
        "aeromedical_risk": aeromedical_risk_agent,
        "aerospace_medicine_rag": aerospace_medicine_rag_agent,
    }


def test_flowise_agent_handoffs() -> None:
    """Test the Flowise agent handoff system."""
    try:
        agents = create_flowise_enhancement_system()
        logger.info("Flowise agent system created successfully")
        logger.info(f"Available Flowise agents: {list(agents.keys())}")
        
        # Test basic agent properties
        for name, agent in agents.items():
            logger.info(f"Flowise Agent {name}: {len(agent.tools)} tools, model: {agent.model}")
            
    except Exception as e:
        logger.error(f"Error testing Flowise agent handoffs: {e}")
        raise 