"""
Perplexity API Client for PRISMA Systematic Review.

This module provides a client for interacting with Perplexity's API
for deep research and literature search capabilities.
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
            "Content-Type": "application/json",
            "User-Agent": "PRISMA-Review-System/1.0"
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def search_literature(
        self,
        query: str,
        max_results: int = 20,
        include_citations: bool = True,
        focus_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search literature using Perplexity's research capabilities.
        
        Args:
            query: Research query or search terms
            max_results: Maximum number of results to return
            include_citations: Whether to include citation information
            focus_domains: Specific domains to focus on (e.g., ['pubmed', 'scholar'])
            
        Returns:
            Dictionary containing search results and metadata
            
        Raises:
            PerplexityAPIError: If the API request fails
        """
        try:
            # Construct research-focused prompt
            research_prompt = self._construct_research_prompt(
                query, max_results, include_citations, focus_domains
            )
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a systematic review research assistant. Provide comprehensive, evidence-based information with proper citations."
                    },
                    {
                        "role": "user",
                        "content": research_prompt
                    }
                ],
                "max_tokens": 4000,
                "temperature": 0.3,
                "top_p": 0.9,
                "return_citations": include_citations,
                "return_images": False
            }
            
            response = self._make_api_request("/chat/completions", payload)
            
            return self._parse_literature_response(response)
            
        except Exception as e:
            logger.error(f"Error searching literature: {e}")
            raise PerplexityAPIError(f"Literature search failed: {str(e)}")
    
    def conduct_systematic_search(
        self,
        research_question: str,
        search_strategy: Dict[str, Any],
        inclusion_criteria: List[str],
        exclusion_criteria: List[str]
    ) -> Dict[str, Any]:
        """
        Conduct a systematic literature search for PRISMA compliance.
        
        Args:
            research_question: Primary research question
            search_strategy: Search strategy including keywords and databases
            inclusion_criteria: List of inclusion criteria
            exclusion_criteria: List of exclusion criteria
            
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
                "return_citations": True,
                "return_images": False
            }
            
            response = self._make_api_request("/chat/completions", payload)
            
            return self._parse_systematic_response(response)
            
        except Exception as e:
            logger.error(f"Error conducting systematic search: {e}")
            raise PerplexityAPIError(f"Systematic search failed: {str(e)}")
    
    def extract_study_data(
        self,
        study_abstracts: List[str],
        extraction_template: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract data from study abstracts using structured templates.
        
        Args:
            study_abstracts: List of study abstracts to extract data from
            extraction_template: Template defining what data to extract
            
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
                "return_citations": True,
                "return_images": False
            }
            
            response = self._make_api_request("/chat/completions", payload)
            
            return self._parse_extraction_response(response)
            
        except Exception as e:
            logger.error(f"Error extracting study data: {e}")
            raise PerplexityAPIError(f"Data extraction failed: {str(e)}")
    
    def _construct_research_prompt(
        self,
        query: str,
        max_results: int,
        include_citations: bool,
        focus_domains: Optional[List[str]]
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
        - Include up to {max_results} relevant studies
        - Provide proper citations in APA format
        - Include study methodologies and key findings
        - Assess study quality and relevance
        - Organize findings by themes or categories
        """
        
        if focus_domains:
            prompt += f"\n\nFocus on these specific domains: {', '.join(focus_domains)}"
        
        if include_citations:
            prompt += "\n\nEnsure all sources are properly cited with full bibliographic information."
        
        return prompt
    
    @retry_with_exponential_backoff(allowed_exceptions=(requests.exceptions.RequestException,))
    def _make_api_request(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make API request with retry logic and error handling.
        
        Args:
            endpoint: API endpoint to call
            payload: Request payload
            
        Returns:
            API response data
            
        Raises:
            PerplexityAPIError: If request fails after retries
        """
        url = f"{self.base_url}{endpoint}"
        
        response = self.session.post(
            url,
            json=payload,
            timeout=AppConfig.TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()

        # For retryable errors, raise an exception that the decorator will catch.
        if response.status_code == 429 or response.status_code >= 500:
            logger.warning(f"Retryable error: {response.status_code}. Decorator will handle retry.")
            response.raise_for_status()

        # For non-retryable client errors, raise a specific exception.
        elif response.status_code == 401:
            raise PerplexityAPIError("Authentication failed - check API key")
        elif response.status_code == 400:
            raise PerplexityAPIError(f"Bad request: {response.text}")
        else:
            logger.error(f"API error: {response.status_code}, {response.text}")
            raise PerplexityAPIError(f"API error: {response.status_code}")
    
    def _parse_literature_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse literature search response."""
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            citations = response.get("citations", [])
            
            return {
                "content": content,
                "citations": citations,
                "model_used": response.get("model", self.model),
                "usage": response.get("usage", {}),
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error parsing literature response: {e}")
            return {
                "content": "Error parsing response",
                "citations": [],
                "error": str(e)
            }
    
    def _parse_systematic_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse systematic search response."""
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            citations = response.get("citations", [])
            
            return {
                "systematic_review": content,
                "citations": citations,
                "model_used": response.get("model", self.model),
                "usage": response.get("usage", {}),
                "timestamp": time.time(),
                "search_metadata": {
                    "total_sources": len(citations),
                    "search_completeness": "comprehensive" if len(citations) >= 20 else "moderate"
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing systematic response: {e}")
            return {
                "systematic_review": "Error parsing response",
                "citations": [],
                "error": str(e)
            }
    
    def _parse_extraction_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse data extraction response."""
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            citations = response.get("citations", [])
            
            return {
                "extracted_data": content,
                "citations": citations,
                "model_used": response.get("model", self.model),
                "usage": response.get("usage", {}),
                "timestamp": time.time(),
                "extraction_metadata": {
                    "studies_processed": len(citations),
                    "extraction_completeness": "complete"
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing extraction response: {e}")
            return {
                "extracted_data": "Error parsing response",
                "citations": [],
                "error": str(e)
            }


class PRISMAPerplexityRouter:
    """
    Specialized router for PRISMA systematic review using Perplexity.
    
    Provides domain-specific methods for different phases of systematic review.
    """
    
    def __init__(self, client: Optional[PerplexityClient] = None):
        """
        Initialize the PRISMA router.
        
        Args:
            client: Optional Perplexity client (creates default if None)
        """
        self.client = client or PerplexityClient()
    
    @lru_cache(maxsize=32)
    def search_phase(self, research_question: str, keywords: Tuple[str, ...]) -> Dict[str, Any]:
        """Conduct literature search phase for PRISMA."""
        search_strategy = {
            "keywords": list(keywords),
            "databases": ["PubMed", "Google Scholar", "Cochrane Library", "Web of Science"],
            "date_range": "2010-2024",
            "language": "English"
        }
        
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
            ]
        )
    
    @lru_cache(maxsize=32)
    def screening_phase(self, abstracts: Tuple[str, ...]) -> Dict[str, Any]:
        """Conduct screening phase for PRISMA."""
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
        
        return self.client.extract_study_data(list(abstracts), template)
    
    def quality_assessment_phase(self, included_studies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Conduct quality assessment phase for PRISMA."""
        abstracts = [study.get("abstract", "") for study in included_studies]
        
        template = {
            "study_id": "unique identifier",
            "risk_of_bias": "assessment using appropriate tool",
            "study_quality": "quality rating",
            "methodological_concerns": "identified limitations",
            "strength_of_evidence": "GRADE assessment",
            "confidence_level": "confidence in results"
        }
        
        return self.client.extract_study_data(abstracts, template) 