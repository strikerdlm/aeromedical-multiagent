"""
Perplexity API Client for PRISMA Systematic Review.

This module provides a client for interacting with Perplexity's API
for deep research and literature search capabilities.
Updated to match official Perplexity API documentation structure.
"""

from __future__ import annotations

import json
import time
import logging
from typing import Dict, Any, Optional, List, Union, Tuple
from functools import lru_cache
import requests
from requests.exceptions import RequestException

from .config import AppConfig, PRISMAConfig
from .utils import retry_with_exponential_backoff


logger = logging.getLogger(__name__)


class PerplexityAPIError(Exception):
    """Custom exception for Perplexity API errors."""
    pass


class ConfigurationError(Exception):
    """Custom exception for configuration errors."""
    pass


class PerplexityClient:
    """
    Client for interacting with Perplexity API for deep research.
    
    Provides methods for conducting literature searches, research queries,
    and systematic review support with proper error handling.
    Updated to match official Perplexity API documentation.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Perplexity client.
        
        Args:
            api_key: Perplexity API key (optional, uses config default)
        """
        self.api_key = api_key or AppConfig.PPLX_API_KEY
        if not self.api_key:
            raise ConfigurationError("Perplexity API key is not configured. Please set the PPLX_API_KEY environment variable.")

        self.base_url = PRISMAConfig.PERPLEXITY_BASE_URL
        self.model = PRISMAConfig.PERPLEXITY_MODEL
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.last_request_time = 0
    
    def search_literature(
        self,
        query: str,
        max_tokens: int = 4000,
        temperature: float = 0.3,
        reasoning_effort: str = "medium",
        search_mode: Optional[str] = "academic",
        include_citations: bool = True,
        focus_domains: Optional[List[str]] = None,
        search_after_date: Optional[str] = None,
        search_context_size: str = "medium",
        timeout_override: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Search literature using Perplexity's research capabilities.
        
        Args:
            query: Research query or search terms
            max_tokens: Maximum tokens in response (default: 4000)
            temperature: Response randomness (default: 0.3)
            reasoning_effort: "low" | "medium" | "high" (default: "medium")
            search_mode: "academic" for scholarly sources (default: "academic")
            include_citations: Whether to include citation information
            focus_domains: Specific domains to focus on (e.g., ['pubmed.com', 'scholar.google.com'])
            search_after_date: Date filter in format "1/1/2023"
            search_context_size: "low" | "medium" | "high" (default: "medium")
            timeout_override: Override timeout for fast-fail scenarios
            
        Returns:
            Dictionary containing search results and metadata
            
        Raises:
            PerplexityAPIError: If the API request fails
        """
        try:
            # Construct research-focused system prompt
            system_prompt = "You are a systematic review research assistant. Provide comprehensive, evidence-based information with proper citations from peer-reviewed sources."
            
            # Construct user prompt
            research_prompt = self._construct_research_prompt(query, include_citations)
            
            # Build payload according to official API documentation
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": research_prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.9,
                "stream": False
            }
            
            # Add optional parameters only if specified (following API docs)
            if reasoning_effort != "medium":  # Only add if not default
                payload["reasoning_effort"] = reasoning_effort
                
            if search_mode:
                payload["search_mode"] = search_mode
                
            if focus_domains:
                payload["search_domain_filter"] = focus_domains
                
            if search_after_date:
                payload["search_after_date_filter"] = search_after_date
                
            if search_context_size != "medium":  # Only add if not default
                payload["web_search_options"] = {"search_context_size": search_context_size}
            
            # Use fast-fail method for timeout overrides (better UX in query optimizer)
            if timeout_override is not None:
                response = self._make_api_request_fast_fail("/chat/completions", payload, timeout_override)
            else:
                response = self._make_api_request("/chat/completions", payload)
            
            return self._parse_literature_response(response)
            
        except Exception as e:
            logger.error(f"Error searching literature: {e}")
            raise PerplexityAPIError(f"Literature search failed: {str(e)}")
    
    def search_literature_async(
        self,
        query: str,
        max_tokens: int = 4000,
        temperature: float = 0.3,
        reasoning_effort: str = "high",  # Default to high for deep research
        search_mode: str = "academic",
        focus_domains: Optional[List[str]] = None,
        search_after_date: Optional[str] = None,
        search_context_size: str = "high"  # Default to high for comprehensive research
    ) -> Dict[str, Any]:
        """
        Submit async literature search for long-running research tasks.
        
        Args:
            query: Research query or search terms
            max_tokens: Maximum tokens in response (default: 4000)
            temperature: Response randomness (default: 0.3)
            reasoning_effort: "low" | "medium" | "high" (default: "high")
            search_mode: "academic" for scholarly sources (default: "academic")
            focus_domains: Specific domains to focus on
            search_after_date: Date filter in format "1/1/2023"
            search_context_size: "low" | "medium" | "high" (default: "high")
            
        Returns:
            Dictionary containing request ID and status
            
        Raises:
            PerplexityAPIError: If the API request fails
        """
        try:
            system_prompt = "You are a systematic review research assistant. Provide comprehensive, evidence-based information with proper citations from peer-reviewed sources."
            research_prompt = self._construct_research_prompt(query, True)
            
            # Build async request payload
            request_payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": research_prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.9,
                "reasoning_effort": reasoning_effort,
                "search_mode": search_mode,
                "web_search_options": {"search_context_size": search_context_size}
            }
            
            if focus_domains:
                request_payload["search_domain_filter"] = focus_domains
                
            if search_after_date:
                request_payload["search_after_date_filter"] = search_after_date
            
            # Wrap in request object for async API
            payload = {"request": request_payload}
            
            response = self._make_api_request("/async/chat/completions", payload)
            return response
            
        except Exception as e:
            logger.error(f"Error submitting async literature search: {e}")
            raise PerplexityAPIError(f"Async literature search failed: {str(e)}")
    
    def check_async_status(self, request_id: str) -> Dict[str, Any]:
        """
        Check status of async request.
        
        Args:
            request_id: Request ID from async submission
            
        Returns:
            Dictionary containing status and response (if completed)
            
        Raises:
            PerplexityAPIError: If the status check fails
        """
        try:
            url = f"{self.base_url}/async/chat/completions/{request_id}"
            response = self.session.get(url, timeout=AppConfig.TIMEOUT)
            
            if response.status_code == 200:
                return response.json()
            else:
                raise PerplexityAPIError(f"Status check failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error checking async status: {e}")
            raise PerplexityAPIError(f"Status check failed: {str(e)}")
    
    def poll_async_completion(self, request_id: str, max_wait_time: int = 300, poll_interval: int = 5) -> Dict[str, Any]:
        """
        Poll async request until completion.
        
        Args:
            request_id: Request ID from async submission
            max_wait_time: Maximum time to wait in seconds (default: 300)
            poll_interval: Polling interval in seconds (default: 5)
            
        Returns:
            Dictionary containing final response
            
        Raises:
            PerplexityAPIError: If polling fails or times out
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                status_response = self.check_async_status(request_id)
                status = status_response.get('status')
                
                if status == 'COMPLETED':
                    return status_response.get('response', {})
                elif status == 'FAILED':
                    error_msg = status_response.get('error_message', 'Unknown error')
                    raise PerplexityAPIError(f"Async request failed: {error_msg}")
                
                time.sleep(poll_interval)
                
            except Exception as e:
                if "Status check failed" not in str(e):
                    raise
                time.sleep(poll_interval)
        
        raise PerplexityAPIError(f"Async request timed out after {max_wait_time} seconds")
    
    def conduct_systematic_search(
        self,
        research_question: str,
        search_strategy: Dict[str, Any],
        inclusion_criteria: List[str],
        exclusion_criteria: List[str],
        reasoning_effort: str = "high",
        search_context_size: str = "high"
    ) -> Dict[str, Any]:
        """
        Conduct a systematic literature search for PRISMA compliance.
        
        Args:
            research_question: Primary research question
            search_strategy: Search strategy including keywords and databases
            inclusion_criteria: List of inclusion criteria
            exclusion_criteria: List of exclusion criteria
            reasoning_effort: "low" | "medium" | "high" (default: "high")
            search_context_size: "low" | "medium" | "high" (default: "high")
            
        Returns:
            Systematic search results with PRISMA-compliant documentation
            
        Raises:
            PerplexityAPIError: If the search process fails
        """
        try:
            # Construct systematic search prompt
            systematic_prompt = f"""
            Conduct a systematic literature search for the following research question:
            
            Research Question: {research_question}
            
            Search Strategy:
            {json.dumps(search_strategy, indent=2)}
            
            Inclusion Criteria:
            {chr(10).join(f"- {criteria}" for criteria in inclusion_criteria)}
            
            Exclusion Criteria:
            {chr(10).join(f"- {criteria}" for criteria in exclusion_criteria)}
            
            Please provide:
            1. Comprehensive literature search results
            2. Study characteristics and methodologies
            3. Quality assessment indicators
            4. Relevant citations in APA format
            5. Summary of findings organized by themes
            6. Assessment of study quality and bias risk
            
            Focus on peer-reviewed articles, systematic reviews, and high-quality evidence sources.
            Include at least 20-30 relevant studies if available.
            """
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert systematic review researcher following PRISMA guidelines. Provide comprehensive, methodologically sound literature reviews with proper citations."
                    },
                    {
                        "role": "user",
                        "content": systematic_prompt
                    }
                ],
                "max_tokens": 8000,
                "temperature": 0.2,
                "top_p": 0.9,
                "reasoning_effort": reasoning_effort,
                "search_mode": "academic",
                "web_search_options": {"search_context_size": search_context_size},
                "stream": False
            }
            
            response = self._make_api_request("/chat/completions", payload)
            
            return self._parse_systematic_response(response)
            
        except Exception as e:
            logger.error(f"Error conducting systematic search: {e}")
            raise PerplexityAPIError(f"Systematic search failed: {str(e)}")
    
    def extract_study_data(
        self,
        study_abstracts: List[str],
        extraction_template: Dict[str, Any],
        reasoning_effort: str = "high",
        response_format: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract data from study abstracts using structured templates.
        
        Args:
            study_abstracts: List of study abstracts to extract data from
            extraction_template: Template defining what data to extract
            reasoning_effort: "low" | "medium" | "high" (default: "high")
            response_format: Optional structured output format (JSON schema or regex)
            
        Returns:
            Extracted data organized according to template
            
        Raises:
            PerplexityAPIError: If data extraction fails
        """
        try:
            # Construct data extraction prompt
            extraction_prompt = f"""
            Extract data from the following study abstracts using the provided template:
            
            Extraction Template:
            {json.dumps(extraction_template, indent=2)}
            
            Study Abstracts:
            {chr(10).join(f"Abstract {i+1}: {abstract}" for i, abstract in enumerate(study_abstracts))}
            
            Please extract data systematically and provide:
            1. Study characteristics (authors, year, design, participants)
            2. Intervention details (if applicable)
            3. Outcome measures and results
            4. Quality indicators and limitations
            5. Risk of bias assessment
            6. Relevance to research question
            
            Format the output as structured data that can be used for meta-analysis.
            """
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a systematic review data extraction specialist. Extract data accurately and comprehensively following standardized templates."
                    },
                    {
                        "role": "user",
                        "content": extraction_prompt
                    }
                ],
                "max_tokens": 6000,
                "temperature": 0.1,
                "top_p": 0.9,
                "reasoning_effort": reasoning_effort,
                "search_mode": "academic",
                "stream": False
            }
            
            # Add structured output format if specified
            if response_format:
                payload["response_format"] = response_format
            
            response = self._make_api_request("/chat/completions", payload)
            
            return self._parse_extraction_response(response)
            
        except Exception as e:
            logger.error(f"Error extracting study data: {e}")
            raise PerplexityAPIError(f"Data extraction failed: {str(e)}")
    
    def _construct_research_prompt(
        self,
        query: str,
        include_citations: bool
    ) -> str:
        """Construct a research-focused prompt for literature search."""
        prompt = f"""
        Research Query: {query}
        
        Please provide a comprehensive literature search focusing on:
        1. Peer-reviewed academic articles
        2. Systematic reviews and meta-analyses
        3. Recent high-quality studies (prefer last 10 years)
        4. Authoritative sources and evidence-based findings
        
        Requirements:
        - Include up to 20 relevant studies
        - Provide proper citations in APA format
        - Include study methodologies and key findings
        - Assess study quality and relevance
        - Organize findings by themes or categories
        """
        
        if include_citations:
            prompt += "\n\nEnsure all sources are properly cited with full bibliographic information."
        
        return prompt
    
    @retry_with_exponential_backoff(allowed_exceptions=(requests.exceptions.RequestException,))
    def _make_api_request(self, endpoint: str, payload: Dict[str, Any], timeout_override: Optional[int] = None) -> Dict[str, Any]:
        """
        Make API request with retry logic and error handling.
        Updated to match official API documentation error codes.
        
        Args:
            endpoint: API endpoint to call
            payload: Request payload
            timeout_override: Override timeout value
            
        Returns:
            API response data
            
        Raises:
            PerplexityAPIError: If request fails after retries
        """
        # Rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < PRISMAConfig.PERPLEXITY_RATE_LIMIT_DELAY:
            time.sleep(PRISMAConfig.PERPLEXITY_RATE_LIMIT_DELAY - elapsed)

        url = f"{self.base_url}{endpoint}"
        
        # Use timeout override for faster failures when needed
        timeout = timeout_override if timeout_override is not None else AppConfig.TIMEOUT
        
        response = self.session.post(
            url,
            json=payload,
            timeout=timeout
        )
        
        self.last_request_time = time.time()

        # Handle successful responses
        if response.status_code == 200:
            return response.json()

        # Handle retryable errors (rate limiting and server errors)
        if response.status_code == 429:
            logger.warning("Rate limited - retrying with exponential backoff")
            response.raise_for_status()
        elif response.status_code >= 500:
            logger.warning(f"Server error {response.status_code} - retrying")
            response.raise_for_status()

        # Handle non-retryable client errors
        elif response.status_code == 401:
            raise PerplexityAPIError("Authentication failed - check API key")
        elif response.status_code == 400:
            try:
                error_detail = response.json().get('detail', response.text)
            except (ValueError, KeyError, TypeError):
                error_detail = response.text
            raise PerplexityAPIError(f"Bad request - validate payload structure: {error_detail}")
        else:
            logger.error(f"API error: {response.status_code}, {response.text}")
            raise PerplexityAPIError(f"API error: {response.status_code}")
    
    def _make_api_request_fast_fail(self, endpoint: str, payload: Dict[str, Any], timeout: int = 15) -> Dict[str, Any]:
        """
        Make API request with fast failure for better UX (no retries).
        Used specifically for query optimization where speed matters more than reliability.
        Updated to match official API documentation error codes.
        
        Args:
            endpoint: API endpoint to call
            payload: Request payload
            timeout: Request timeout in seconds
            
        Returns:
            API response data
            
        Raises:
            PerplexityAPIError: If request fails
        """
        # Rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < PRISMAConfig.PERPLEXITY_RATE_LIMIT_DELAY:
            time.sleep(PRISMAConfig.PERPLEXITY_RATE_LIMIT_DELAY - elapsed)

        url = f"{self.base_url}{endpoint}"
        
        response = self.session.post(
            url,
            json=payload,
            timeout=timeout
        )
        
        self.last_request_time = time.time()

        if response.status_code == 200:
            return response.json()

        # Fast failure - no retries, improved error messages
        elif response.status_code == 401:
            raise PerplexityAPIError("Authentication failed - check API key")
        elif response.status_code == 400:
            try:
                error_detail = response.json().get('detail', response.text)
            except (ValueError, KeyError, TypeError):
                error_detail = response.text
            raise PerplexityAPIError(f"Bad request - validate payload structure: {error_detail}")
        elif response.status_code == 429:
            raise PerplexityAPIError("Rate limited - implement exponential backoff")
        else:
            logger.error(f"API error: {response.status_code}, {response.text}")
            raise PerplexityAPIError(f"API error: {response.status_code}")
    
    def _parse_literature_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse literature search response according to new API structure."""
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            # Handle citations from new API structure
            citations = response.get("citations", [])
            
            # Handle search results from new API structure (important for URLs)
            search_results = response.get("search_results", [])
            
            return {
                "content": content,
                "citations": citations,
                "search_results": search_results,  # New field for accurate URLs
                "model_used": response.get("model", self.model),
                "usage": response.get("usage", {}),
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error parsing literature response: {e}")
            return {
                "content": "Error parsing response",
                "citations": [],
                "search_results": [],
                "error": str(e)
            }
    
    def _parse_systematic_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse systematic search response according to new API structure."""
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            citations = response.get("citations", [])
            search_results = response.get("search_results", [])
            
            return {
                "systematic_review": content,
                "citations": citations,
                "search_results": search_results,  # New field for accurate URLs
                "model_used": response.get("model", self.model),
                "usage": response.get("usage", {}),
                "timestamp": time.time(),
                "search_metadata": {
                    "total_sources": len(citations),
                    "search_results_count": len(search_results),
                    "search_completeness": "comprehensive" if len(citations) >= 20 else "moderate"
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing systematic response: {e}")
            return {
                "systematic_review": "Error parsing response",
                "citations": [],
                "search_results": [],
                "error": str(e)
            }
    
    def _parse_extraction_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse data extraction response according to new API structure."""
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            citations = response.get("citations", [])
            search_results = response.get("search_results", [])
            
            return {
                "extracted_data": content,
                "citations": citations,
                "search_results": search_results,  # New field for accurate URLs
                "model_used": response.get("model", self.model),
                "usage": response.get("usage", {}),
                "timestamp": time.time(),
                "extraction_metadata": {
                    "studies_processed": len(citations),
                    "search_results_count": len(search_results),
                    "extraction_completeness": "complete"
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing extraction response: {e}")
            return {
                "extracted_data": "Error parsing response",
                "citations": [],
                "search_results": [],
                "error": str(e)
            }


class PRISMAPerplexityRouter:
    """
    Specialized router for PRISMA systematic review using Perplexity.
    
    Provides domain-specific methods for different phases of systematic review.
    Updated to use new API parameters and features.
    """
    
    def __init__(self, client: Optional[PerplexityClient] = None):
        """
        Initialize the PRISMA router.
        
        Args:
            client: Optional Perplexity client (creates default if None)
        """
        self.client = client or PerplexityClient()
    
    @lru_cache(maxsize=32)
    def search_phase(
        self, 
        research_question: str, 
        keywords: Tuple[str, ...],
        use_async: bool = False,
        reasoning_effort: str = "high",
        search_after_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Conduct literature search phase for PRISMA using new API features.
        
        Args:
            research_question: Primary research question
            keywords: Tuple of search keywords
            use_async: Whether to use async API for deep research
            reasoning_effort: "low" | "medium" | "high" (default: "high")
            search_after_date: Optional date filter in format "1/1/2023"
        """
        search_strategy = {
            "keywords": list(keywords),
            "databases": ["PubMed", "Google Scholar", "Cochrane Library", "Web of Science"],
            "date_range": "2010-2024",
            "language": "English"
        }
        
        # Use async API for comprehensive research
        if use_async:
            return self.client.search_literature_async(
                query=research_question,
                max_tokens=8000,
                reasoning_effort=reasoning_effort,
                search_mode="academic",
                focus_domains=["pubmed.ncbi.nlm.nih.gov", "scholar.google.com", "cochranelibrary.com"],
                search_after_date=search_after_date,
                search_context_size="high"
            )
        else:
            return self.client.conduct_systematic_search(
                research_question=research_question,
                search_strategy=search_strategy,
                inclusion_criteria=[
                    "Peer-reviewed articles",
                    "Published in English",
                    "Published 2010-2024",
                    "Relevant to research question"
                ],
                exclusion_criteria=[
                    "Non-peer reviewed sources",
                    "Case reports with n<10",
                    "Opinion pieces",
                    "Duplicate publications"
                ],
                reasoning_effort=reasoning_effort,
                search_context_size="high"
            )
    
    @lru_cache(maxsize=32)
    def screening_phase(
        self, 
        abstracts: Tuple[str, ...],
        use_structured_output: bool = True,
        reasoning_effort: str = "high"
    ) -> Dict[str, Any]:
        """
        Conduct screening phase for PRISMA using structured outputs.
        
        Args:
            abstracts: Tuple of study abstracts
            use_structured_output: Whether to use JSON schema for structured response
            reasoning_effort: "low" | "medium" | "high" (default: "high")
        """
        template = {
            "study_id": "unique identifier",
            "authors": "list of authors",
            "year": "publication year",
            "title": "study title",
            "study_design": "methodology",
            "participants": "sample characteristics",
            "intervention": "intervention details",
            "outcomes": "primary outcomes",
            "relevance_score": "1-10 scale",
            "include_exclude": "decision with rationale"
        }
        
        # Use structured JSON output for better data extraction
        response_format = None
        if use_structured_output:
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "studies": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "study_id": {"type": "string"},
                                        "authors": {"type": "string"},
                                        "year": {"type": "integer"},
                                        "title": {"type": "string"},
                                        "study_design": {"type": "string"},
                                        "participants": {"type": "string"},
                                        "intervention": {"type": "string"},
                                        "outcomes": {"type": "string"},
                                        "relevance_score": {"type": "integer", "minimum": 1, "maximum": 10},
                                        "include_exclude": {"type": "string"}
                                    },
                                    "required": ["study_id", "title", "relevance_score", "include_exclude"]
                                }
                            }
                        },
                        "required": ["studies"]
                    }
                }
            }
        
        return self.client.extract_study_data(
            list(abstracts), 
            template, 
            reasoning_effort=reasoning_effort,
            response_format=response_format
        )
    
    def quality_assessment_phase(
        self, 
        included_studies: List[Dict[str, Any]],
        assessment_tool: str = "GRADE",
        reasoning_effort: str = "high"
    ) -> Dict[str, Any]:
        """
        Conduct quality assessment phase for PRISMA with specified assessment tool.
        
        Args:
            included_studies: List of included study data
            assessment_tool: Quality assessment tool ("GRADE", "Cochrane", "AMSTAR")
            reasoning_effort: "low" | "medium" | "high" (default: "high")
        """
        abstracts = [study.get("abstract", "") for study in included_studies]
        
        template = {
            "study_id": "unique identifier",
            "risk_of_bias": f"assessment using {assessment_tool} tool",
            "study_quality": "quality rating",
            "methodological_concerns": "identified limitations",
            "strength_of_evidence": f"{assessment_tool} assessment",
            "confidence_level": "confidence in results"
        }
        
        # Use structured output for quality assessment
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "schema": {
                    "type": "object",
                    "properties": {
                        "assessments": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "study_id": {"type": "string"},
                                    "risk_of_bias": {"type": "string"},
                                    "study_quality": {"type": "string"},
                                    "methodological_concerns": {"type": "string"},
                                    "strength_of_evidence": {"type": "string"},
                                    "confidence_level": {"type": "string"}
                                },
                                "required": ["study_id", "risk_of_bias", "study_quality"]
                            }
                        }
                    },
                    "required": ["assessments"]
                }
            }
        }
        
        return self.client.extract_study_data(
            abstracts, 
            template, 
            reasoning_effort=reasoning_effort,
            response_format=response_format
        )
    
    def async_comprehensive_review(
        self,
        research_question: str,
        keywords: Tuple[str, ...],
        max_wait_time: int = 600  # 10 minutes for comprehensive review
    ) -> Dict[str, Any]:
        """
        Conduct comprehensive async review for complex research questions.
        
        Args:
            research_question: Primary research question
            keywords: Tuple of search keywords
            max_wait_time: Maximum wait time in seconds (default: 600)
        """
        try:
            # Submit async request
            async_response = self.search_phase(
                research_question, 
                keywords, 
                use_async=True,
                reasoning_effort="high",
                search_after_date="1/1/2020"  # Last 4 years for comprehensive review
            )
            
            request_id = async_response.get("id")
            if not request_id:
                raise PerplexityAPIError("Failed to get request ID from async submission")
            
            # Poll for completion
            return self.client.poll_async_completion(request_id, max_wait_time)
            
        except Exception as e:
            logger.error(f"Error in async comprehensive review: {e}")
            raise PerplexityAPIError(f"Async comprehensive review failed: {str(e)}") 