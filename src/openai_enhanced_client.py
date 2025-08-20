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
# Similar to src.agents, OpenAI may not be installed in the execution
# environment used for automated tests. Provide a small stub so that the
# module can be imported without the dependency.
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

    def process_with_deep_research_model(self, enhanced_prompt: str) -> str:
        """
        Process prompt using o3-deep-research model with high reasoning effort.

        Args:
            enhanced_prompt: The enhanced prompt to process

        Returns:
            Response from o3-deep-research model
        """
        try:
            logger.info("Processing with o3-deep-research model")
            
            config = OpenAIModelsConfig.O3_DEEP_RESEARCH

            # Use Responses API for o3 models with reasoning effort
            if hasattr(config, 'reasoning_effort') and config.reasoning_effort:
                tools: List[Dict[str, Any]] = []
                if AppConfig.OPENAI_USE_WEB_SEARCH_PREVIEW:
                    tool_def: Dict[str, Any] = {
                        "type": "web_search_preview",
                        "search_context_size": AppConfig.OPENAI_WEB_SEARCH_CONTEXT_SIZE,
                    }
                    if AppConfig.OPENAI_USE_APPROXIMATE_LOCATION:
                        tool_def["user_location"] = {"type": "approximate"}
                    tools.append(tool_def)

                response = self.client.responses.create(
                    model=config.model_name,
                    input=enhanced_prompt,
                    text={
                        "format": {"type": "text"},
                        "verbosity": "high"
                    },
                    max_output_tokens=config.max_tokens,
                    temperature=config.temperature,
                    reasoning={
                        "effort": config.reasoning_effort,
                        "summary": "auto"
                    },
                    tools=tools or None,
                    store=False
                )
                
                # Extract the response from the Responses API format
                if hasattr(response, 'output') and response.output:
                    for output_item in response.output:
                        if hasattr(output_item, 'type') and output_item.type == 'text':
                            return getattr(output_item, 'content', None) or "Deep research completed successfully."
                        elif hasattr(output_item, 'content') and output_item.content:
                            return output_item.content
                
                # Fallback to regular response if no text output found
                return "Deep research completed with reasoning."
            else:
                # Fallback to regular chat completions for models without reasoning effort
                response = self.client.chat.completions.create(
                    model=config.model_name,
                    messages=[{
                        "role": "user",
                        "content": enhanced_prompt
                    }],
                    max_tokens=config.max_tokens,
                    temperature=config.temperature
                )

                # Extract the response content
                if getattr(response, 'choices', None) and len(response.choices) > 0:
                    content = response.choices[0].message.content
                    return content or "Deep research completed successfully."
                else:
                    return "No response generated from deep research model."

        except Exception as e:
            logger.error(f"Error in deep research processing: {e}")
            return f"Error processing with deep research model: {str(e)}"

    def process_with_o3_and_web_search(self, enhanced_prompt: str) -> str:
        """
        Process prompt using GPT-5 with optional OpenAI web search preview tool.

        Args:
            enhanced_prompt: The enhanced prompt to process

        Returns:
            Response from GPT-5 (optionally enhanced with web search)
        """
        try:
            logger.info("Processing with GPT-5 + web search (if enabled)")

            config = OpenAIModelsConfig.O3_REASONING  # Now configured to GPT-5

            if AppConfig.OPENAI_USE_WEB_SEARCH_PREVIEW:
                tools: List[Dict[str, Any]] = [{
                    "type": "web_search_preview",
                    "search_context_size": AppConfig.OPENAI_WEB_SEARCH_CONTEXT_SIZE,
                    **({"user_location": {"type": "approximate"}} if AppConfig.OPENAI_USE_APPROXIMATE_LOCATION else {}),
                }]

                response = self.client.responses.create(
                    model=config.model_name,
                    input=enhanced_prompt,
                    text={
                        "format": {"type": "text"},
                        "verbosity": "high"
                    },
                    max_output_tokens=config.max_tokens,
                    temperature=config.temperature,
                    reasoning={
                        "effort": config.reasoning_effort,
                        "summary": "auto"
                    },
                    tools=tools,
                    store=False
                )

                if hasattr(response, 'output') and response.output:
                    for output_item in response.output:
                        if hasattr(output_item, 'type') and output_item.type == 'text':
                            return getattr(output_item, 'content', None) or "Processing completed successfully."
                        elif hasattr(output_item, 'content') and output_item.content:
                            return output_item.content
                return "Processing completed with reasoning."

            # Fallback path: custom Google CSE based web search enrichment
            logger.info("OpenAI web_search_preview disabled; using manual web search enrichment")

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

            # Use Responses API for GPT-5 with reasoning effort
            response = self.client.responses.create(
                model=config.model_name,
                input=enhanced_with_search,
                text={
                    "format": {"type": "text"},
                    "verbosity": "high"
                },
                max_output_tokens=config.max_tokens,
                temperature=config.temperature,
                reasoning={
                    "effort": config.reasoning_effort,
                    "summary": "auto"
                },
                store=False
            )
            
            if hasattr(response, 'output') and response.output:
                for output_item in response.output:
                    if hasattr(output_item, 'type') and output_item.type == 'text':
                        return getattr(output_item, 'content', None) or "Processing completed successfully."
                    elif hasattr(output_item, 'content') and output_item.content:
                        return output_item.content
            return "Processing completed with reasoning."

        except Exception as e:
            logger.error(f"Error in GPT-5 + web search processing: {e}")
            return f"Error processing with GPT-5 + web search: {str(e)}"

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

            logger.info(f"Routing decision - Science/Tech: {is_science_tech}, Deep Research: {requires_deep_research}")

            # Route to appropriate model
            if is_science_tech or requires_deep_research:
                logger.info("Routing to o3-deep-research model")
                return self.process_with_deep_research_model(enhanced_prompt)
            else:
                logger.info("Routing to GPT-5 with web search (if enabled)")
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
