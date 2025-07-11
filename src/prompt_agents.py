"""
Specialized Agents for Prompt Enhancement System.

This module defines the specific agents for the multi-agent prompt
enhancement application with advanced OpenAI model routing.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional

from agents import Agent, tool
from .openai_enhanced_client import EnhancedOpenAIClient, create_enhanced_openai_client
from .config import OpenAIModelsConfig


logger = logging.getLogger(__name__)


class EnhancedPromptTools:
    """
    Tools for prompt enhancement and advanced OpenAI model processing.
    
    This class provides tools that agents can use to enhance prompts
    and route them to appropriate OpenAI models.
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
            
            User prompt to analyze: "{user_prompt}"
            
            Provide a clear, structured analysis that will guide prompt enhancement.
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
            logger.info(f"Prompt analysis completed for: {user_prompt[:50]}...")
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
            enhanced version of the prompt that will yield much better results from AI systems.
            
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
            logger.info(f"Prompt enhanced successfully")
            return enhanced or f"Enhanced version of: {original_prompt}"
            
        except Exception as e:
            logger.error(f"Error enhancing prompt: {e}")
            return f"Error enhancing prompt: {str(e)}"


class PromptEnhancementAgents:
    """
    Factory class for creating prompt enhancement agents with advanced OpenAI routing.
    
    This class creates and configures the specialized agents for
    the prompt enhancement workflow using o3-deep-research and o3 models.
    """
    
    def __init__(self, openai_client: Optional[EnhancedOpenAIClient] = None):
        """
        Initialize the agent factory.
        
        Args:
            openai_client: Optional enhanced OpenAI client (creates default if None)
        """
        self.openai_client = openai_client or create_enhanced_openai_client()
        self.tools = EnhancedPromptTools(self.openai_client)
        
        # Store agents for handoffs
        self._prompt_enhancer: Optional[Agent] = None
        self._prompt_processor: Optional[Agent] = None
        
        # Store original question for routing decisions
        self._original_question: str = ""
    
    def set_original_question(self, question: str) -> None:
        """Store the original question for routing decisions."""
        self._original_question = question
    
    @tool
    def transfer_to_prompt_processor(self) -> Agent:
        """Transfer to the prompt processor agent."""
        if not self._prompt_processor:
            self._prompt_processor = self.create_prompt_processor()
        return self._prompt_processor
    
    @tool
    def transfer_to_prompt_enhancer(self) -> Agent:
        """Transfer back to the prompt enhancer agent."""
        if not self._prompt_enhancer:
            self._prompt_enhancer = self.create_prompt_enhancer()
        return self._prompt_enhancer
    
    @tool
    def analyze_and_enhance_prompt(self, user_prompt: str) -> str:
        """
        Analyze the user prompt and create an enhanced version.
        
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
            logger.info(f"Prompt analysis completed: {analysis[:100]}...")
            
            # Step 2: Enhance the prompt based on analysis
            enhanced = self.tools.enhance_prompt_with_context(user_prompt, analysis)
            logger.info(f"Prompt enhanced: {enhanced[:100]}...")
            
            return enhanced
            
        except Exception as e:
            logger.error(f"Error in prompt enhancement: {e}")
            return f"Error enhancing prompt: {str(e)}"
    
    @tool
    def process_with_advanced_routing(self, enhanced_prompt: str) -> str:
        """
        Process the enhanced prompt using advanced OpenAI model routing.
        
        Args:
            enhanced_prompt: The enhanced prompt to process
            
        Returns:
            Response from the appropriate OpenAI model (o3-deep-research or o3)
        """
        try:
            logger.info("Processing with advanced OpenAI model routing")
            
            # Route and process using the enhanced client
            response = self.openai_client.route_and_process(
                enhanced_prompt, 
                self._original_question
            )
            
            logger.info("Advanced routing processing completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error in advanced routing: {e}")
            return f"Error processing with advanced routing: {str(e)}"
    
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
    
    def create_prompt_enhancer(self) -> Agent:
        """
        Create the Prompt Enhancer Agent.
        
        This agent is responsible for analyzing user requests and enhancing
        them with additional context and details.
        
        Returns:
            Configured PromptEnhancer agent
        """
        instructions = """
        You are a Prompt Enhancement Specialist AI Agent. Your primary role is to take user requests 
        and transform them into comprehensive, detailed prompts that will yield much better results 
        from advanced AI systems including o3-deep-research and o3 models.

        CORE RESPONSIBILITIES:
        1. Analyze the user's original request deeply
        2. Identify the domain, intent, complexity level, and question type
        3. Enhance the prompt by adding relevant context, background, and specificity
        4. Create a significantly stronger prompt that goes beyond what the user initially asked
        5. Transfer the enhanced prompt to the Prompt Processor for advanced model routing

        ENHANCEMENT STRATEGY:
        - Add domain-specific context and background information
        - Clarify ambiguous terms and add precision
        - Include relevant constraints, requirements, and success criteria
        - Expand scope where beneficial while maintaining original intent
        - Add structure and format specifications for better responses
        - Include examples or analogies when helpful
        - Specify desired depth and comprehensiveness
        - Consider whether the question would benefit from scientific/technical analysis

        WORKFLOW:
        1. First, analyze the user's prompt using analyze_and_enhance_prompt()
        2. Create an enhanced version that is significantly more detailed and contextual
        3. When ready, transfer to the Prompt Processor using transfer_to_prompt_processor()
        4. The processor will automatically route to either:
           - o3-deep-research-2025-06-26 for science/technology questions
           - o3 with web search and high reasoning for other questions

        Always be thorough in your enhancement but maintain the user's original intent. 
        Your goal is to create prompts that will generate much more comprehensive and useful responses
        from the most appropriate advanced AI model.
        """
        
        # Create tools list with instance methods
        tools = [
            self.analyze_and_enhance_prompt,
            self.transfer_to_prompt_processor,
        ]
        
        agent = Agent(
            name="Prompt Enhancer",
            instructions=instructions,
            tools=tools,
            model=OpenAIModelsConfig.GPT4_MINI.model_name
        )
        
        self._prompt_enhancer = agent
        return agent
    
    def create_prompt_processor(self) -> Agent:
        """
        Create the Prompt Processor Agent.
        
        This agent receives enhanced prompts and processes them through
        advanced OpenAI models with intelligent routing.
        
        Returns:
            Configured PromptProcessor agent
        """
        instructions = """
        You are a Prompt Processing Specialist AI Agent. You receive enhanced prompts from the 
        Prompt Enhancer and execute them through the most appropriate advanced OpenAI models 
        to generate comprehensive, high-quality responses.

        CORE RESPONSIBILITIES:
        1. Receive enhanced prompts from the Prompt Enhancer
        2. Automatically route to the best OpenAI model based on question type:
           - o3-deep-research-2025-06-26 for science/technology/research questions
           - o3 with web search and high reasoning for general questions
        3. Provide comprehensive responses to the user
        4. Handle any errors or routing issues gracefully

        AVAILABLE PROCESSING OPTIONS:
        - **Automatic Routing**: Uses intelligent classification to select the best model
        - **Deep Research**: o3-deep-research-2025-06-26 for complex scientific/technical analysis
        - **Web-Enhanced O3**: o3 model with web search for current information and general topics

        PROCESSING STRATEGY:
        1. Use process_with_advanced_routing() for automatic intelligent routing (PREFERRED)
        2. Use force_deep_research_processing() only if explicitly requested for research
        3. Use force_o3_web_search_processing() only if explicitly requested for web search
        4. Provide detailed, comprehensive responses
        5. Explain which model was used and why when relevant

        MODEL SELECTION LOGIC:
        - Science/Technology questions → o3-deep-research-2025-06-26
        - Questions with keywords like "research", "analysis", "comprehensive" → o3-deep-research
        - General questions, current events, practical advice → o3 + web search
        - Complex multi-part questions → o3-deep-research

        Always aim to provide the most comprehensive and useful response possible using the 
        most appropriate advanced AI model for the specific question type.
        """
        
        # Create tools list with instance methods
        tools = [
            self.process_with_advanced_routing,
            self.force_deep_research_processing,
            self.force_o3_web_search_processing,
            self.transfer_to_prompt_enhancer,
        ]
        
        agent = Agent(
            name="Prompt Processor",
            instructions=instructions,
            tools=tools,
            model=OpenAIModelsConfig.GPT4_MINI.model_name
        )
        
        self._prompt_processor = agent
        return agent
    
    def create_triage_agent(self) -> Agent:
        """
        Create a Triage Agent for initial user interaction.
        
        This agent handles initial user requests and routes them to
        the appropriate enhancement workflow.
        
        Returns:
            Configured Triage agent
        """
        @tool
        def escalate_to_human(summary: str) -> str:
            """Escalate complex issues to human assistance."""
            logger.info(f"Escalating to human: {summary}")
            return f"Escalated to human assistance: {summary}"
        
        instructions = """
        You are a Triage Agent for the Advanced Multi-Agent Prompt Enhancement System. Your role is to:
        
        1. Greet users and understand their needs
        2. Determine if their request can benefit from prompt enhancement
        3. Route requests to the enhancement workflow for processing by advanced AI models
        4. Transfer to Prompt Enhancer for most requests that need enhancement
        
        SYSTEM CAPABILITIES:
        - Advanced prompt enhancement using AI analysis
        - Intelligent routing between o3-deep-research and o3 models
        - Science/technology questions → o3-deep-research-2025-06-26
        - General questions → o3 with web search and high reasoning
        
        ROUTING DECISIONS:
        - Simple, clear requests: Still benefit from enhancement - Transfer to Prompt Enhancer
        - Complex, technical, or scientific requests: Transfer to Prompt Enhancer (will route to o3-deep-research)
        - General knowledge or current events: Transfer to Prompt Enhancer (will route to o3 + web search)
        - Requests that could benefit from additional context: Transfer to Prompt Enhancer
        
        Almost all requests should go through the enhancement workflow to take advantage of the 
        advanced AI models. Always explain what you're doing for the user and mention which 
        advanced model will likely be used based on their question type.
        """
        
        tools = [
            self.transfer_to_prompt_enhancer,
            escalate_to_human,
        ]
        
        return Agent(
            name="Triage Agent",
            instructions=instructions,
            tools=tools,
            model=OpenAIModelsConfig.GPT4_MINI.model_name
        )


# Example usage and testing functions
def create_prompt_enhancement_system() -> Dict[str, Agent]:
    """
    Create the complete prompt enhancement system with all agents.
    
    Returns:
        Dictionary mapping agent names to agent instances
    """
    factory = PromptEnhancementAgents()
    
    agents = {
        "triage": factory.create_triage_agent(),
        "enhancer": factory.create_prompt_enhancer(),
        "processor": factory.create_prompt_processor(),
    }
    
    return agents


def test_agent_handoffs() -> None:
    """Test the agent handoff functionality."""
    factory = PromptEnhancementAgents()
    
    # Test handoff functions
    enhancer = factory.transfer_to_prompt_enhancer()
    processor = factory.transfer_to_prompt_processor()
    
    logger.info(f"Created enhancer: {enhancer.name}")
    logger.info(f"Created processor: {processor.name}")
    
    # Test tools
    test_prompt = "Tell me about quantum computing and its applications in cryptography"
    enhanced = factory.analyze_and_enhance_prompt(test_prompt)
    logger.info(f"Enhanced prompt: {enhanced[:100]}...")


if __name__ == "__main__":
    # Set up logging for testing
    logging.basicConfig(level=logging.INFO)
    
    # Test the system
    test_agent_handoffs()
    
    # Create full system
    system = create_prompt_enhancement_system()
    logger.info(f"Created system with agents: {list(system.keys())}") 