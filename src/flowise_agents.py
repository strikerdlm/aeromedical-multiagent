"""
Flowise-Only Agents for Prompt Enhancement System.

This module defines specialized agents that use only Flowise API
without any OpenAI o3 model integration.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional

from agents import Agent, tool
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


class FlowisePromptTools:
    """
    Tools for prompt enhancement using only Flowise API.
    
    This class provides tools that agents can use to enhance prompts
    and route them to appropriate Flowise chatflows.
    """
    
    def __init__(self, flowise_client: Optional[FlowiseClient] = None):
        """
        Initialize the tools with a Flowise client.
        
        Args:
            flowise_client: FlowiseClient instance for API calls
        """
        self.flowise_client = flowise_client or MedicalFlowiseRouter()
    
    @tool
    def analyze_prompt_for_flowise(self, user_prompt: str) -> str:
        """
        Analyze the user prompt to determine the best Flowise chatflow.
        
        Args:
            user_prompt: The original user prompt
            
        Returns:
            Analysis of the prompt for Flowise routing
        """
        try:
            # Use GPT-4o-mini for quick analysis focused on Flowise routing
            analysis_prompt = f"""
            Analyze this user prompt specifically for Flowise chatflow routing and provide:
            
            1. **Domain Classification**: Aeromedical Risk, Deep Research, Aerospace Medicine
            2. **Best Flowise Chatflow**: Which chatflow would handle this best?
               - aeromedical_risk: Aviation medicine risk assessment and analysis
               - deep_research: Comprehensive research analysis with multiple sources
               - aerospace_medicine_rag: Scientific articles and textbooks in aerospace medicine
            3. **Query Type**: research, aeromedical, aerospace_medicine
            4. **Enhancement Needs**: What context would improve Flowise processing?
            5. **Streaming Preference**: Should this use streaming response?
            
            User prompt to analyze: "{user_prompt}"
            
            Provide a clear analysis for optimal Flowise chatflow selection and enhancement.
            """
            
            # Use a simple completion for analysis
            from openai import OpenAI
            
            client = OpenAI(api_key=AppConfig.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=OpenAIModelsConfig.GPT4_MINI.model_name,
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=800,
                temperature=0.2
            )
            
            analysis = response.choices[0].message.content
            logger.info(f"Flowise prompt analysis completed for: {user_prompt[:50]}...")
            return analysis or "Flowise analysis completed successfully."
            
        except Exception as e:
            logger.error(f"Error analyzing prompt for Flowise: {e}")
            return f"Error analyzing prompt for Flowise: {str(e)}"
    
    @tool
    def enhance_prompt_for_flowise(self, original_prompt: str, flowise_analysis: str) -> str:
        """
        Enhance the original prompt specifically for Flowise chatflows.
        
        Args:
            original_prompt: The user's original prompt
            flowise_analysis: Analysis of the prompt for Flowise routing
            
        Returns:
            Enhanced prompt optimized for Flowise chatflows
        """
        try:
            enhancement_prompt = f"""
            Based on the original user prompt and Flowise analysis, create an enhanced version 
            optimized specifically for Flowise chatflow processing.
            
            **Original user prompt:** "{original_prompt}"
            
            **Flowise Analysis:** {flowise_analysis}
            
            **Your task:** Create an enhanced prompt that:
            1. Adds relevant domain-specific context for the identified Flowise chatflow
            2. Includes medical/research terminology that Flowise RAG systems understand
            3. Structures the query for optimal retrieval from Flowise knowledge bases
            4. Adds specific details that leverage Flowise's specialized datasets
            5. Maintains the original intent while optimizing for Flowise processing
            6. Includes context that helps Flowise's RAG systems find relevant documents
            7. Formats the request for the specific chatflow type identified
            8. Adds background information that Flowise systems can build upon
            
            **Flowise-Optimized Enhanced Prompt:**
            """
            
            # Use GPT-4o-mini for enhancement
            from openai import OpenAI
            
            client = OpenAI(api_key=AppConfig.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=OpenAIModelsConfig.GPT4_MINI.model_name,
                messages=[{"role": "user", "content": enhancement_prompt}],
                max_tokens=1500,
                temperature=0.3
            )
            
            enhanced = response.choices[0].message.content
            logger.info(f"Flowise prompt enhanced successfully")
            return enhanced or f"Flowise-enhanced version of: {original_prompt}"
            
        except Exception as e:
            logger.error(f"Error enhancing prompt for Flowise: {e}")
            return f"Error enhancing prompt for Flowise: {str(e)}"


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
        self.tools = FlowisePromptTools(self.flowise_client)
        
        # Store agents for handoffs
        self._flowise_enhancer: Optional[Agent] = None
        self._flowise_processor: Optional[Agent] = None
        
        # Store original question and analysis for routing
        self._original_question: str = ""
        self._flowise_analysis: str = ""
    
    def set_original_question(self, question: str) -> None:
        """Store the original question for routing decisions."""
        self._original_question = question
    
    def set_flowise_analysis(self, analysis: str) -> None:
        """Store the Flowise analysis for routing decisions."""
        self._flowise_analysis = analysis
    
    @tool
    def transfer_to_flowise_processor(self) -> Agent:
        """Transfer to the Flowise processor agent."""
        if not self._flowise_processor:
            self._flowise_processor = self.create_flowise_processor()
        return self._flowise_processor
    
    @tool
    def transfer_to_flowise_enhancer(self) -> Agent:
        """Transfer back to the Flowise enhancer agent."""
        if not self._flowise_enhancer:
            self._flowise_enhancer = self.create_flowise_enhancer()
        return self._flowise_enhancer
    
    @tool
    def analyze_and_enhance_for_flowise(self, user_prompt: str) -> str:
        """
        Analyze the user prompt and create an enhanced version for Flowise.
        
        Args:
            user_prompt: The original user prompt
            
        Returns:
            Enhanced prompt optimized for Flowise chatflows
        """
        try:
            # Store the original question for routing
            self.set_original_question(user_prompt)
            
            # Step 1: Analyze the prompt for Flowise routing
            analysis = self.tools.analyze_prompt_for_flowise(user_prompt)
            self.set_flowise_analysis(analysis)
            logger.info(f"Flowise prompt analysis completed: {analysis[:100]}...")
            
            # Step 2: Enhance the prompt for Flowise
            enhanced = self.tools.enhance_prompt_for_flowise(user_prompt, analysis)
            logger.info(f"Flowise prompt enhanced: {enhanced[:100]}...")
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error in Flowise prompt enhancement: {e}")
            return f"Error enhancing prompt for Flowise: {str(e)}"
    
    @tool
    def query_aerospace_medicine_rag(self, enhanced_prompt: str) -> str:
        """
        Send the enhanced prompt to Flowise aerospace medicine RAG chatflow.
        
        Args:
            enhanced_prompt: The enhanced prompt to send
            
        Returns:
            Response from Flowise aerospace medicine RAG chatflow
        """
        try:
            logger.info("Querying Flowise aerospace medicine RAG chatflow")
            result = self.flowise_client.consult_aerospace_medicine_rag(enhanced_prompt)
            
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
    
    @tool
    def query_flowise_deep_research(self, enhanced_prompt: str) -> str:
        """
        Send the enhanced prompt to Flowise deep research chatflow.
        
        Args:
            enhanced_prompt: The enhanced prompt to send
            
        Returns:
            Response from Flowise deep research chatflow
        """
        try:
            logger.info("Querying Flowise deep research chatflow")
            result = self.flowise_client.consult_deep_research(enhanced_prompt)
            
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
    
    @tool
    def query_aeromedical_risk(self, enhanced_prompt: str) -> str:
        """
        Send the enhanced prompt to Flowise aeromedical risk chatflow.
        
        Args:
            enhanced_prompt: The enhanced prompt to send
            
        Returns:
            Response from Flowise aeromedical risk chatflow
        """
        try:
            logger.info("Querying Flowise aeromedical risk chatflow")
            result = self.flowise_client.consult_aeromedical_risk(enhanced_prompt)

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
    
    @tool
    def route_to_flowise_specialist(self, query_type: str, enhanced_prompt: str) -> str:
        """
        Route the enhanced prompt to a specialist Flowise chatflow.
        
        Args:
            query_type: Type of specialist query ('research', 'aeromedical', 'aerospace_medicine')
            enhanced_prompt: The enhanced prompt to send
            
        Returns:
            Response from the specialist Flowise chatflow
        """
        try:
            logger.info(f"Routing to Flowise specialist: {query_type}")
            result = self.flowise_client.route_medical_query(query_type, enhanced_prompt)
            
            # Extract response text using the helper function
            response_text = _extract_flowise_response_text(result)
            logger.info(f"Flowise {query_type} specialist query completed successfully")
            return response_text
                
        except FlowiseAPIError as e:
            logger.error(f"Flowise routing error: {e}")
            return f"Error routing to Flowise specialist: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in Flowise specialist routing: {e}")
            return f"Unexpected error: {str(e)}"
    
    def create_flowise_enhancer(self) -> Agent:
        """
        Create the Flowise Prompt Enhancer Agent.
        
        This agent is responsible for analyzing user requests and enhancing
        them specifically for Flowise chatflows.
        
        Returns:
            Configured Flowise PromptEnhancer agent
        """
        instructions = """
        You are a Flowise Prompt Enhancement Specialist AI Agent. Your primary role is to take user requests 
        and transform them into comprehensive, detailed prompts optimized specifically for Flowise chatflows 
        and RAG (Retrieval-Augmented Generation) systems.

        CORE RESPONSIBILITIES:
        1. Analyze the user's original request for Flowise chatflow compatibility
        2. Identify the best Flowise chatflow for the request type
        3. Enhance the prompt with domain-specific context that Flowise systems understand
        4. Optimize for Flowise's RAG retrieval and knowledge base systems
        5. Transfer the enhanced prompt to the Flowise Processor for chatflow execution

        FLOWISE CHATFLOW SPECIALIZATIONS:
        - **aeromedical_risk**: Aviation medicine risk assessment and analysis
        - **deep_research**: Comprehensive research analysis with multiple sources
        - **aerospace_medicine_rag**: Scientific articles and textbooks in aerospace medicine

        FLOWISE OPTIMIZATION STRATEGY:
        - Add medical/scientific terminology that Flowise RAG systems recognize
        - Include domain-specific context that helps document retrieval
        - Structure queries for optimal knowledge base search
        - Add background information that Flowise can build upon
        - Format requests to leverage Flowise's specialized datasets
        - Include relevant keywords for better RAG performance
        - Specify the type of information needed from Flowise knowledge bases

        ENHANCEMENT STRATEGY:
        - Add domain-specific context and medical/research terminology
        - Include relevant background that helps Flowise document retrieval
        - Clarify medical/scientific terms for better RAG matching
        - Expand scope to include related concepts Flowise can find
        - Add structure that works well with Flowise's knowledge organization
        - Include examples or case studies when relevant for Flowise processing
        - Specify desired depth that matches Flowise capabilities

        WORKFLOW:
        1. First, analyze the user's prompt using analyze_and_enhance_for_flowise()
        2. Create an enhanced version specifically optimized for Flowise chatflows
        3. When ready, transfer to the Flowise Processor using transfer_to_flowise_processor()
        4. The processor will route to the most appropriate Flowise chatflow

        Always optimize for Flowise's RAG capabilities and specialized knowledge bases 
        while maintaining the user's original intent.
        """
        
        # Create tools list with instance methods
        tools = [
            self.analyze_and_enhance_for_flowise,
            self.transfer_to_flowise_processor,
        ]
        
        agent = Agent(
            name="Flowise Prompt Enhancer",
            instructions=instructions,
            tools=tools,
            model=AppConfig.OPENAI_MODEL
        )
        
        self._flowise_enhancer = agent
        return agent
    
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
        Flowise Prompt Enhancer and execute them through the most appropriate Flowise chatflows 
        to generate comprehensive, knowledge-rich responses.

        CORE RESPONSIBILITIES:
        1. Receive enhanced prompts optimized for Flowise chatflows
        2. Route to the best Flowise chatflow based on domain and question type
        3. Execute queries through Flowise's specialized knowledge bases
        4. Provide comprehensive responses leveraging Flowise's RAG capabilities
        5. Handle streaming responses and API errors gracefully

        AVAILABLE FLOWISE CHATFLOWS:
        - **Deep Research**: Comprehensive research analysis with multiple sources
        - **Aeromedical Risk**: Aviation medicine risk assessment and analysis
        - **Aerospace Medicine RAG**: Scientific articles and textbooks in aerospace medicine

        FLOWISE PROCESSING STRATEGY:
        1. Use query_flowise_deep_research() for comprehensive research questions
        2. Use query_aeromedical_risk() for aviation medicine risk assessment
        3. Use query_aerospace_medicine_rag() for aerospace medicine knowledge
        4. Use route_to_flowise_specialist() for domain-specific questions
        5. Leverage Flowise's streaming capabilities for better user experience
        6. Handle Flowise API errors and provide meaningful feedback

        CHATFLOW SELECTION LOGIC:
        - Aviation medicine risk questions → aeromedical_risk chatflow
        - Aerospace medicine/scientific questions → aerospace_medicine_rag chatflow
        - Comprehensive research → deep_research chatflow
        - General medical questions → aerospace_medicine_rag chatflow

        Always aim to provide the most comprehensive and knowledge-rich response possible 
        using the most appropriate Flowise chatflow for the specific question type.
        """
        
        # Create tools list with instance methods
        tools = [
            self.query_flowise_deep_research,
            self.query_aeromedical_risk,
            self.query_aerospace_medicine_rag,
            self.route_to_flowise_specialist,
            self.transfer_to_flowise_enhancer,
        ]
        
        agent = Agent(
            name="Flowise Processor",
            instructions=instructions,
            tools=tools,
            model=AppConfig.OPENAI_MODEL
        )
        
        self._flowise_processor = agent
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
            self.query_flowise_deep_research,
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
            self.query_aeromedical_risk,
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
            self.query_aerospace_medicine_rag,
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
    
    return {
        "flowise_enhancer": flowise_system.create_flowise_enhancer(),
        "flowise_processor": flowise_system.create_flowise_processor(),
        "deep_research": flowise_system.create_deepresearch_agent(),
        "aeromedical_risk": flowise_system.create_aeromedical_risk_agent(),
        "aerospace_medicine_rag": flowise_system.create_aerospace_medicine_rag_agent(),
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