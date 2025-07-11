"""
O3 Deep Research Agents for Prompt Enhancement System.

This module defines specialized agents that use only OpenAI's o3-deep-research
and o3 models without any Flowise integration.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional

from agents import Agent, tool
from .openai_enhanced_client import EnhancedOpenAIClient, create_enhanced_openai_client
from .config import OpenAIModelsConfig


logger = logging.getLogger(__name__)


class O3PromptTools:
    """
    Tools for prompt enhancement using only OpenAI o3 models.
    
    This class provides tools that agents can use to enhance prompts
    and route them to appropriate OpenAI o3 models without Flowise.
    """
    
    def __init__(self, openai_client: Optional[EnhancedOpenAIClient] = None):
        """
        Initialize the tools with an enhanced OpenAI client.
        
        Args:
            openai_client: EnhancedOpenAIClient instance for API calls
        """
        self.openai_client = openai_client or create_enhanced_openai_client()
    
    @tool
    def analyze_prompt_context(self, user_prompt: str) -> str:
        """
        Analyze the user prompt to understand context and intent.
        
        Args:
            user_prompt: The original user prompt
            
        Returns:
            Analysis of the prompt's context and intent
        """
        try:
            # Use GPT-4o-mini for quick analysis
            analysis_prompt = f"""
            Analyze this user prompt and provide a structured analysis:
            
            1. **Main Topic/Domain**: What is the primary subject area?
            2. **Intent**: What does the user want to achieve?
            3. **Complexity Level**: Rate as Simple/Medium/Complex and explain why
            4. **Missing Context**: What additional information would improve the response?
            5. **Enhancement Opportunities**: Specific suggestions for prompt improvement
            6. **Question Type**: Is this science/technology related or general knowledge?
            7. **Recommended O3 Model**: Should this use o3-deep-research or o3+web search?
            
            User prompt to analyze: "{user_prompt}"
            
            Provide a clear, structured analysis that will guide prompt enhancement and model selection.
            """
            
            # Use a simple completion for analysis
            from openai import OpenAI
            from .config import AppConfig
            
            client = OpenAI(api_key=AppConfig.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=OpenAIModelsConfig.GPT4_MINI.model_name,
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=1000,
                temperature=0.2
            )
            
            analysis = response.choices[0].message.content
            logger.info(f"O3 Prompt analysis completed for: {user_prompt[:50]}...")
            return analysis or "Analysis completed successfully."
            
        except Exception as e:
            logger.error(f"Error analyzing prompt: {e}")
            return f"Error analyzing prompt: {str(e)}"
    
    @tool
    def enhance_prompt_with_context(self, original_prompt: str, context_analysis: str) -> str:
        """
        Enhance the original prompt based on context analysis.
        
        Args:
            original_prompt: The user's original prompt
            context_analysis: Analysis of the prompt context
            
        Returns:
            Enhanced prompt with additional context and details
        """
        try:
            enhancement_prompt = f"""
            Based on the original user prompt and the detailed analysis provided, create a significantly 
            enhanced version of the prompt that will yield much better results from OpenAI's o3 models.
            
            **Original user prompt:** "{original_prompt}"
            
            **Analysis of the prompt:** {context_analysis}
            
            **Your task:** Create an enhanced prompt that:
            1. Adds relevant background context and domain-specific information
            2. Clarifies the intent and expected outcome format
            3. Includes specific details that would improve response quality
            4. Adds structure and organization to the request
            5. Maintains the original intent while expanding scope appropriately
            6. Includes success criteria or evaluation parameters if relevant
            7. Adds examples or analogies if helpful
            8. Specifies the desired depth and comprehensiveness of the response
            9. Optimizes for o3-deep-research or o3+web search based on the analysis
            
            **Enhanced Prompt:**
            """
            
            # Use GPT-4o-mini for enhancement
            from openai import OpenAI
            from .config import AppConfig
            
            client = OpenAI(api_key=AppConfig.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=OpenAIModelsConfig.GPT4_MINI.model_name,
                messages=[{"role": "user", "content": enhancement_prompt}],
                max_tokens=2000,
                temperature=0.3
            )
            
            enhanced = response.choices[0].message.content
            logger.info(f"O3 Prompt enhanced successfully")
            return enhanced or f"Enhanced version of: {original_prompt}"
            
        except Exception as e:
            logger.error(f"Error enhancing prompt: {e}")
            return f"Error enhancing prompt: {str(e)}"


class O3AgentSystem:
    """
    Factory class for creating O3-only prompt enhancement agents.
    
    This class creates and configures specialized agents for
    the O3 model workflow without any Flowise integration.
    """
    
    def __init__(self, openai_client: Optional[EnhancedOpenAIClient] = None):
        """
        Initialize the O3 agent system.
        
        Args:
            openai_client: Optional enhanced OpenAI client (creates default if None)
        """
        self.openai_client = openai_client or create_enhanced_openai_client()
        self.tools = O3PromptTools(self.openai_client)
        
        # Store agents for handoffs
        self._o3_enhancer: Optional[Agent] = None
        self._o3_processor: Optional[Agent] = None
        
        # Store original question for routing decisions
        self._original_question: str = ""
    
    def set_original_question(self, question: str) -> None:
        """Store the original question for routing decisions."""
        self._original_question = question
    
    @tool
    def transfer_to_o3_processor(self) -> Agent:
        """Transfer to the O3 processor agent."""
        if not self._o3_processor:
            self._o3_processor = self.create_o3_processor()
        return self._o3_processor
    
    @tool
    def transfer_to_o3_enhancer(self) -> Agent:
        """Transfer back to the O3 enhancer agent."""
        if not self._o3_enhancer:
            self._o3_enhancer = self.create_o3_enhancer()
        return self._o3_enhancer
    
    @tool
    def analyze_and_enhance_prompt(self, user_prompt: str) -> str:
        """
        Analyze the user prompt and create an enhanced version for O3 models.
        
        Args:
            user_prompt: The original user prompt
            
        Returns:
            Enhanced prompt with additional context and details
        """
        try:
            # Store the original question for routing
            self.set_original_question(user_prompt)
            
            # Step 1: Analyze the prompt context
            analysis = self.tools.analyze_prompt_context(user_prompt)
            logger.info(f"O3 Prompt analysis completed: {analysis[:100]}...")
            
            # Step 2: Enhance the prompt based on analysis
            enhanced = self.tools.enhance_prompt_with_context(user_prompt, analysis)
            logger.info(f"O3 Prompt enhanced: {enhanced[:100]}...")
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error in O3 prompt enhancement: {e}")
            return f"Error enhancing prompt: {str(e)}"
    
    @tool
    def process_with_o3_routing(self, enhanced_prompt: str) -> str:
        """
        Process the enhanced prompt using O3 model routing.
        
        Args:
            enhanced_prompt: The enhanced prompt to process
            
        Returns:
            Response from the appropriate O3 model
        """
        try:
            logger.info("Processing with O3 model routing")
            
            # Route and process using the enhanced client
            response = self.openai_client.route_and_process(
                enhanced_prompt, 
                self._original_question
            )
            
            logger.info("O3 routing processing completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error in O3 routing: {e}")
            return f"Error processing with O3 routing: {str(e)}"
    
    @tool
    def force_deep_research_processing(self, enhanced_prompt: str) -> str:
        """
        Force processing with o3-deep-research model.
        
        Args:
            enhanced_prompt: The enhanced prompt to process
            
        Returns:
            Response from o3-deep-research model
        """
        try:
            logger.info("Force processing with o3-deep-research")
            return self.openai_client.process_with_deep_research(enhanced_prompt)
        except Exception as e:
            logger.error(f"Error in deep research processing: {e}")
            return f"Error processing with deep research: {str(e)}"
    
    @tool
    def force_o3_web_search_processing(self, enhanced_prompt: str) -> str:
        """
        Force processing with o3 + web search.
        
        Args:
            enhanced_prompt: The enhanced prompt to process
            
        Returns:
            Response from o3 with web search
        """
        try:
            logger.info("Force processing with o3 + web search")
            return self.openai_client.process_with_o3_and_web_search(enhanced_prompt)
        except Exception as e:
            logger.error(f"Error in o3 web search processing: {e}")
            return f"Error processing with o3 + web search: {str(e)}"
    
    def create_o3_enhancer(self) -> Agent:
        """
        Create the O3 Prompt Enhancer Agent.
        
        This agent is responsible for analyzing user requests and enhancing
        them specifically for OpenAI's o3 models.
        
        Returns:
            Configured O3 PromptEnhancer agent
        """
        instructions = """
        You are an O3 Prompt Enhancement Specialist AI Agent. Your primary role is to take user requests 
        and transform them into comprehensive, detailed prompts optimized specifically for OpenAI's 
        o3-deep-research and o3 models.

        CORE RESPONSIBILITIES:
        1. Analyze the user's original request deeply
        2. Identify the domain, intent, complexity level, and question type
        3. Enhance the prompt by adding relevant context, background, and specificity
        4. Optimize the prompt specifically for o3 model capabilities
        5. Transfer the enhanced prompt to the O3 Processor for model routing

        O3 MODEL OPTIMIZATION STRATEGY:
        - Structure prompts for o3-deep-research's analytical capabilities
        - Add domain-specific context that leverages o3's knowledge depth
        - Include reasoning frameworks that work well with o3 models
        - Specify output formats that maximize o3's structured thinking
        - Add complexity layers that benefit from o3's advanced reasoning
        - Consider multi-step analysis requests for o3-deep-research

        ENHANCEMENT STRATEGY:
        - Add domain-specific context and background information
        - Clarify ambiguous terms and add precision
        - Include relevant constraints, requirements, and success criteria
        - Expand scope where beneficial while maintaining original intent
        - Add structure and format specifications optimized for o3 models
        - Include examples or analogies when helpful for o3 processing
        - Specify desired depth and comprehensiveness
        - Frame questions to leverage o3's reasoning capabilities

        WORKFLOW:
        1. First, analyze the user's prompt using analyze_and_enhance_prompt()
        2. Create an enhanced version specifically optimized for o3 models
        3. When ready, transfer to the O3 Processor using transfer_to_o3_processor()
        4. The processor will route to either:
           - o3-deep-research-2025-06-26 for complex analysis
           - o3 with web search for current information needs

        Always optimize for o3 model strengths while maintaining the user's original intent. 
        Your goal is to create prompts that will generate exceptional responses from o3 models.
        """
        
        # Create tools list with instance methods
        tools = [
            self.analyze_and_enhance_prompt,
            self.transfer_to_o3_processor,
        ]
        
        agent = Agent(
            name="O3 Prompt Enhancer",
            instructions=instructions,
            tools=tools,
            model=OpenAIModelsConfig.GPT4_MINI.model_name
        )
        
        self._o3_enhancer = agent
        return agent
    
    def create_o3_processor(self) -> Agent:
        """
        Create the O3 Prompt Processor Agent.
        
        This agent receives enhanced prompts and processes them through
        OpenAI's o3 models with intelligent routing.
        
        Returns:
            Configured O3 Processor agent
        """
        instructions = """
        You are an O3 Prompt Processing Specialist AI Agent. You receive enhanced prompts from the 
        O3 Prompt Enhancer and execute them through the most appropriate OpenAI o3 models 
        to generate comprehensive, high-quality responses.

        CORE RESPONSIBILITIES:
        1. Receive enhanced prompts optimized for o3 models
        2. Automatically route to the best o3 model based on question type:
           - o3-deep-research-2025-06-26 for complex scientific/technical/research questions
           - o3 with web search and high reasoning for current information and general topics
        3. Provide comprehensive responses leveraging o3 model capabilities
        4. Handle any errors or routing issues gracefully

        AVAILABLE O3 PROCESSING OPTIONS:
        - **Automatic O3 Routing**: Uses intelligent classification to select the best o3 model
        - **Deep Research**: o3-deep-research-2025-06-26 for complex analytical tasks
        - **Web-Enhanced O3**: o3 model with web search for current information

        O3 MODEL SELECTION LOGIC:
        - Complex analysis, research, scientific questions → o3-deep-research-2025-06-26
        - Multi-step reasoning, comprehensive analysis → o3-deep-research
        - Current events, real-time information needs → o3 + web search
        - General questions with reasoning complexity → automatic routing
        - Technical deep-dives and synthesis → o3-deep-research

        PROCESSING STRATEGY:
        1. Use process_with_o3_routing() for automatic intelligent routing (PREFERRED)
        2. Use force_deep_research_processing() for explicit research requests
        3. Use force_o3_web_search_processing() for explicit web search needs
        4. Leverage o3 models' advanced reasoning and analytical capabilities
        5. Provide detailed, comprehensive responses that showcase o3 strengths

        Always aim to provide the most comprehensive and analytically rigorous response possible 
        using the most appropriate o3 model for the specific question type.
        """
        
        # Create tools list with instance methods
        tools = [
            self.process_with_o3_routing,
            self.force_deep_research_processing,
            self.force_o3_web_search_processing,
            self.transfer_to_o3_enhancer,
        ]
        
        agent = Agent(
            name="O3 Processor",
            instructions=instructions,
            tools=tools,
            model=OpenAIModelsConfig.GPT4_MINI.model_name
        )
        
        self._o3_processor = agent
        return agent


def create_o3_enhancement_system() -> Dict[str, Agent]:
    """
    Create the complete O3 enhancement agent system.
    
    Returns:
        Dictionary of agent name to Agent instance for O3 flow
    """
    o3_system = O3AgentSystem()
    
    return {
        "o3_enhancer": o3_system.create_o3_enhancer(),
        "o3_processor": o3_system.create_o3_processor(),
    }


def test_o3_agent_handoffs() -> None:
    """Test the O3 agent handoff system."""
    try:
        agents = create_o3_enhancement_system()
        logger.info("O3 agent system created successfully")
        logger.info(f"Available O3 agents: {list(agents.keys())}")
        
        # Test basic agent properties
        for name, agent in agents.items():
            logger.info(f"O3 Agent {name}: {len(agent.tools)} tools, model: {agent.model}")
            
    except Exception as e:
        logger.error(f"Error testing O3 agent handoffs: {e}")
        raise 