"""
Enhanced OpenAI Client for Advanced Model Routing.

This module provides integration with OpenAI's advanced models including
o3-deep-research and o3 with web search capabilities.
"""

from __future__ import annotations

import json
import logging
import requests
from typing import Dict, Any, List, Optional, Generator, Union
from openai import OpenAI

from .config import AppConfig, OpenAIModelsConfig


logger = logging.getLogger(__name__)


class WebSearchTool:
    """Simple web search tool for enhancing o3 responses."""
    
    def __init__(self, api_key: str = None, search_engine_id: str = None):
        """Initialize web search tool."""
        self.api_key = api_key or AppConfig.SEARCH_API_KEY
        self.search_engine_id = search_engine_id or AppConfig.SEARCH_ENGINE_ID
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Perform web search and return results.
        
        Args:
            query: Search query
            num_results: Number of results to return
            
        Returns:
            List of search results with title, link, and snippet
        """
        if not self.api_key or not self.search_engine_id:
            logger.warning("Web search not configured - using mock results")
            return [{
                "title": "Web Search Not Configured",
                "link": "https://example.com",
                "snippet": "Web search requires SEARCH_API_KEY and SEARCH_ENGINE_ID environment variables."
            }]
        
        try:
            params = {
                "key": self.api_key,
                "cx": self.search_engine_id,
                "q": query,
                "num": min(num_results, 10)
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("items", []):
                results.append({
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "snippet": item.get("snippet", "")
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Web search error: {e}")
            return [{
                "title": "Search Error",
                "link": "https://example.com",
                "snippet": f"Error performing web search: {str(e)}"
            }]


class QuestionClassifier:
    """Classifies questions to determine appropriate model routing."""
    
    def __init__(self):
        """Initialize the question classifier."""
        self.science_tech_keywords = AppConfig.SCIENCE_TECH_KEYWORDS
    
    def is_science_tech_question(self, question: str) -> bool:
        """
        Determine if a question is science/technology related.
        
        Args:
            question: The question to classify
            
        Returns:
            True if science/tech question, False otherwise
        """
        question_lower = question.lower()
        
        # Check for science/tech keywords
        keyword_score = sum(1 for keyword in self.science_tech_keywords 
                          if keyword in question_lower)
        
        # Additional heuristics
        complex_indicators = [
            "how does", "why does", "what causes", "explain the mechanism",
            "research shows", "studies indicate", "analysis of", "data suggests",
            "in-depth", "comprehensive", "detailed analysis", "systematic review"
        ]
        
        complexity_score = sum(1 for indicator in complex_indicators 
                             if indicator in question_lower)
        
        # Decision logic
        is_science_tech = keyword_score >= 1 or complexity_score >= 1
        
        logger.info(f"Question classification - Science/Tech: {is_science_tech}, "
                   f"Keyword score: {keyword_score}, Complexity score: {complexity_score}")
        
        return is_science_tech
    
    def requires_deep_research(self, question: str) -> bool:
        """
        Determine if a question requires deep research capabilities.
        
        Args:
            question: The question to analyze
            
        Returns:
            True if deep research is needed
        """
        deep_research_indicators = [
            "comprehensive analysis", "in-depth study", "systematic review",
            "meta-analysis", "research paper", "literature review",
            "compare and contrast", "pros and cons", "advantages and disadvantages",
            "multiple perspectives", "various approaches", "different methods"
        ]
        
        question_lower = question.lower()
        return any(indicator in question_lower for indicator in deep_research_indicators)


class EnhancedOpenAIClient:
    """Enhanced OpenAI client with advanced model routing and web search."""
    
    def __init__(self, client: Optional[OpenAI] = None):
        """
        Initialize the enhanced OpenAI client.
        
        Args:
            client: Optional OpenAI client instance
        """
        self.client = client or OpenAI(api_key=AppConfig.OPENAI_API_KEY)
        self.classifier = QuestionClassifier()
        self.web_search = WebSearchTool()
    
    def process_with_deep_research(self, enhanced_prompt: str) -> str:
        """
        Process prompt using o3-deep-research model via responses endpoint.
        
        Args:
            enhanced_prompt: The enhanced prompt to process
            
        Returns:
            Response from o3-deep-research model
        """
        try:
            logger.info("Processing with o3-deep-research model")
            
            config = OpenAIModelsConfig.O3_DEEP_RESEARCH
            
            # Use the responses endpoint for deep research
            response = self.client.responses.create(
                model=config.model_name,
                messages=[{
                    "role": "user",
                    "content": enhanced_prompt
                }],
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                reasoning_effort=config.reasoning_effort
            )
            
            # Extract the response content
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                return content or "Deep research completed successfully."
            else:
                return "No response generated from deep research model."
                
        except Exception as e:
            logger.error(f"Error in deep research processing: {e}")
            return f"Error processing with deep research model: {str(e)}"
    
    def process_with_o3_and_web_search(self, enhanced_prompt: str) -> str:
        """
        Process prompt using o3 with web search capabilities.
        
        Args:
            enhanced_prompt: The enhanced prompt to process
            
        Returns:
            Response from o3 model enhanced with web search
        """
        try:
            logger.info("Processing with o3 + web search")
            
            # Extract search queries from the prompt
            search_queries = self._extract_search_queries(enhanced_prompt)
            
            # Perform web searches
            search_results = []
            for query in search_queries[:3]:  # Limit to 3 searches
                results = self.web_search.search(query, num_results=3)
                search_results.extend(results)
            
            # Create enhanced prompt with search results
            enhanced_with_search = self._create_prompt_with_search_results(
                enhanced_prompt, search_results
            )
            
            config = OpenAIModelsConfig.O3_REASONING
            
            # Use o3 model with the search-enhanced prompt
            response = self.client.chat.completions.create(
                model=config.model_name,
                messages=[{
                    "role": "user",
                    "content": enhanced_with_search
                }],
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                reasoning_effort=config.reasoning_effort
            )
            
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                return content or "O3 processing with web search completed successfully."
            else:
                return "No response generated from o3 model."
                
        except Exception as e:
            logger.error(f"Error in o3 + web search processing: {e}")
            return f"Error processing with o3 + web search: {str(e)}"
    
    def _extract_search_queries(self, prompt: str) -> List[str]:
        """
        Extract relevant search queries from the enhanced prompt.
        
        Args:
            prompt: The enhanced prompt
            
        Returns:
            List of search queries
        """
        # Simple extraction logic - in practice, you might use a more sophisticated approach
        queries = []
        
        # Look for question words and extract key phrases
        lines = prompt.split('\n')
        for line in lines:
            if any(word in line.lower() for word in ['what', 'how', 'why', 'when', 'where', 'who']):
                # Extract key terms (this is a simplified approach)
                words = line.split()
                if len(words) > 3:
                    # Take the line as a potential search query, cleaned up
                    clean_query = ' '.join(words[:10])  # Limit to first 10 words
                    queries.append(clean_query)
        
        # If no questions found, create a general search query
        if not queries:
            # Extract key nouns and terms from the first part of the prompt
            words = prompt.split()[:20]  # First 20 words
            key_terms = [word for word in words if len(word) > 3 and word.isalpha()]
            if key_terms:
                queries.append(' '.join(key_terms[:5]))
        
        return queries[:3]  # Return up to 3 queries
    
    def _create_prompt_with_search_results(self, original_prompt: str, search_results: List[Dict[str, Any]]) -> str:
        """
        Create an enhanced prompt that includes web search results.
        
        Args:
            original_prompt: The original enhanced prompt
            search_results: Web search results
            
        Returns:
            Prompt enhanced with search results
        """
        if not search_results:
            return original_prompt
        
        search_context = "\n\n--- WEB SEARCH RESULTS ---\n"
        for i, result in enumerate(search_results[:5], 1):
            search_context += f"\n{i}. {result['title']}\n"
            search_context += f"   URL: {result['link']}\n"
            search_context += f"   Summary: {result['snippet']}\n"
        
        search_context += "\n--- END SEARCH RESULTS ---\n\n"
        
        enhanced_prompt = f"{search_context}{original_prompt}\n\n"
        enhanced_prompt += "Please provide a comprehensive response that incorporates relevant information from the web search results above, while ensuring accuracy and providing proper context."
        
        return enhanced_prompt
    
    def route_and_process(self, enhanced_prompt: str, original_question: str = "") -> str:
        """
        Route the enhanced prompt to the appropriate model and process.
        
        Args:
            enhanced_prompt: The enhanced prompt to process
            original_question: The original user question for classification
            
        Returns:
            Processed response from the appropriate model
        """
        try:
            # Use the original question for classification, fall back to enhanced prompt
            question_to_classify = original_question or enhanced_prompt
            
            # Classify question type
            is_science_tech = self.classifier.is_science_tech_question(question_to_classify)
            requires_deep_research = self.classifier.requires_deep_research(question_to_classify)
            
            logger.info(f"Routing decision - Science/Tech: {is_science_tech}, "
                       f"Deep Research: {requires_deep_research}")
            
            # Route to appropriate model
            if is_science_tech or requires_deep_research:
                logger.info("Routing to o3-deep-research model")
                return self.process_with_deep_research(enhanced_prompt)
            else:
                logger.info("Routing to o3 with web search")
                return self.process_with_o3_and_web_search(enhanced_prompt)
                
        except Exception as e:
            logger.error(f"Error in routing and processing: {e}")
            return f"Error in model routing: {str(e)}"


# Convenience functions for backward compatibility
def create_enhanced_openai_client() -> EnhancedOpenAIClient:
    """Create an enhanced OpenAI client instance."""
    return EnhancedOpenAIClient()


def process_enhanced_prompt(enhanced_prompt: str, original_question: str = "") -> str:
    """
    Process an enhanced prompt using the appropriate OpenAI model.
    
    Args:
        enhanced_prompt: The enhanced prompt to process
        original_question: The original user question for classification
        
    Returns:
        Processed response
    """
    client = create_enhanced_openai_client()
    return client.route_and_process(enhanced_prompt, original_question) 