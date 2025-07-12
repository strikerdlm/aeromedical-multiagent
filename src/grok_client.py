"""
Grok (XAI) API Client for PRISMA Systematic Review.

This module provides a client for interacting with Grok's API
for high-reasoning tasks and critical analysis support.
"""

from __future__ import annotations

import json
import time
import logging
from typing import Dict, Any, Optional, List, Union
import requests
from requests.exceptions import RequestException

from .config import AppConfig, PRISMAConfig
from .utils import retry_with_exponential_backoff


logger = logging.getLogger(__name__)


class GrokAPIError(Exception):
    """Custom exception for Grok API errors."""
    pass


class ConfigurationError(Exception):
    """Custom exception for configuration errors."""
    pass


class GrokClient:
    """
    Client for interacting with Grok API for high-reasoning tasks.
    
    Provides methods for critical analysis, reasoning, and systematic
    review support with proper error handling.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Grok client.
        
        Args:
            api_key: Grok API key (optional, uses config default)
        """
        self.api_key = api_key or AppConfig.XAI_API_KEY
        if not self.api_key:
            raise ConfigurationError("Grok API key is not configured. Please set the XAI_API_KEY environment variable.")

        self.base_url = PRISMAConfig.GROK_BASE_URL
        self.model = PRISMAConfig.GROK_MODEL
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "PRISMA-Review-System/1.0"
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def critical_analysis(
        self,
        content: str,
        analysis_type: str = "systematic_review",
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform critical analysis using Grok's reasoning capabilities.
        
        Args:
            content: Content to analyze
            analysis_type: Type of analysis (e.g., 'systematic_review', 'methodology', 'bias')
            focus_areas: Specific areas to focus critical analysis on
            
        Returns:
            Dictionary containing critical analysis results
            
        Raises:
            GrokAPIError: If the API request fails
        """
        try:
            # Construct critical analysis prompt
            analysis_prompt = self._construct_critical_analysis_prompt(
                content, analysis_type, focus_areas
            )
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a critical analysis expert with deep reasoning capabilities. Provide thorough, evidence-based analysis with identification of strengths, weaknesses, and areas for improvement."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                "max_tokens": 6000,
                "temperature": 0.2,
                "top_p": 0.9,
                "stream": False
            }
            
            response = self._make_api_request("/chat/completions", payload)
            
            return self._parse_analysis_response(response)
            
        except Exception as e:
            logger.error(f"Error in critical analysis: {e}")
            raise GrokAPIError(f"Critical analysis failed: {str(e)}")
    
    def methodology_review(
        self,
        study_details: Dict[str, Any],
        review_standards: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Review study methodology using Grok's reasoning capabilities.
        
        Args:
            study_details: Details of the study to review
            review_standards: Standards to apply (e.g., CONSORT, STROBE)
            
        Returns:
            Methodology review results
            
        Raises:
            GrokAPIError: If the review process fails
        """
        try:
            # Construct methodology review prompt
            review_prompt = f"""
            Review the methodology of the following study using rigorous scientific standards:
            
            Study Details:
            {json.dumps(study_details, indent=2)}
            
            Review Standards:
            {chr(10).join(f"- {standard}" for standard in (review_standards or ["General scientific rigor"]))}
            
            Please provide a comprehensive methodology review including:
            1. Study design appropriateness
            2. Sample size and power analysis
            3. Data collection methods
            4. Statistical analysis approach
            5. Bias assessment and mitigation
            6. Validity and reliability considerations
            7. Ethical considerations
            8. Reporting quality
            9. Strengths and limitations
            10. Overall methodology rating
            
            Be thorough and critical in your assessment while maintaining scientific objectivity.
            """
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a methodology review expert with extensive knowledge of research design, statistical analysis, and scientific standards. Provide detailed, constructive criticism and recommendations."
                    },
                    {
                        "role": "user",
                        "content": review_prompt
                    }
                ],
                "max_tokens": 6000,
                "temperature": 0.1,
                "top_p": 0.9,
                "stream": False
            }
            
            response = self._make_api_request("/chat/completions", payload)
            
            return self._parse_methodology_response(response)
            
        except Exception as e:
            logger.error(f"Error in methodology review: {e}")
            raise GrokAPIError(f"Methodology review failed: {str(e)}")
    
    def synthesis_reasoning(
        self,
        study_findings: List[Dict[str, Any]],
        synthesis_approach: str = "narrative"
    ) -> Dict[str, Any]:
        """
        Synthesize study findings using advanced reasoning.
        
        Args:
            study_findings: List of study findings to synthesize
            synthesis_approach: Approach to synthesis ('narrative', 'quantitative', 'mixed')
            
        Returns:
            Synthesis results with reasoning
            
        Raises:
            GrokAPIError: If synthesis fails
        """
        try:
            # Construct synthesis prompt
            synthesis_prompt = f"""
            Synthesize the following study findings using advanced reasoning and critical analysis:
            
            Study Findings:
            {json.dumps(study_findings, indent=2)}
            
            Synthesis Approach: {synthesis_approach}
            
            Please provide a comprehensive synthesis including:
            1. Overall patterns and trends
            2. Areas of agreement and disagreement
            3. Quality of evidence assessment
            4. Strength of conclusions
            5. Heterogeneity analysis
            6. Subgroup considerations
            7. Clinical significance
            8. Practical implications
            9. Limitations and uncertainties
            10. Future research recommendations
            
            Use rigorous reasoning to identify the most reliable and clinically meaningful conclusions.
            """
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a synthesis expert with advanced reasoning capabilities. Provide comprehensive, evidence-based synthesis with clear reasoning chains and identification of the most reliable conclusions."
                    },
                    {
                        "role": "user",
                        "content": synthesis_prompt
                    }
                ],
                "max_tokens": 8000,
                "temperature": 0.3,
                "top_p": 0.9,
                "stream": False
            }
            
            response = self._make_api_request("/chat/completions", payload)
            
            return self._parse_synthesis_response(response)
            
        except Exception as e:
            logger.error(f"Error in synthesis reasoning: {e}")
            raise GrokAPIError(f"Synthesis reasoning failed: {str(e)}")
    
    def bias_detection(
        self,
        study_content: str,
        bias_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Detect potential biases in study content.
        
        Args:
            study_content: Content to analyze for bias
            bias_types: Specific types of bias to look for
            
        Returns:
            Bias detection results
            
        Raises:
            GrokAPIError: If bias detection fails
        """
        try:
            bias_types = bias_types or [
                "selection bias", "performance bias", "detection bias",
                "attrition bias", "reporting bias", "publication bias"
            ]
            
            # Construct bias detection prompt
            bias_prompt = f"""
            Analyze the following study content for potential biases:
            
            Study Content:
            {study_content}
            
            Bias Types to Evaluate:
            {chr(10).join(f"- {bias_type}" for bias_type in bias_types)}
            
            Please provide a comprehensive bias assessment including:
            1. Identified potential biases
            2. Evidence supporting bias concerns
            3. Severity assessment (low, moderate, high)
            4. Impact on study validity
            5. Mitigation strategies employed
            6. Recommendations for addressing biases
            7. Overall bias risk rating
            
            Be thorough and specific in your analysis.
            """
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a bias detection expert with deep knowledge of research methodology and systematic review standards. Identify and analyze potential biases with high precision and clear reasoning."
                    },
                    {
                        "role": "user",
                        "content": bias_prompt
                    }
                ],
                "max_tokens": 5000,
                "temperature": 0.1,
                "top_p": 0.9,
                "stream": False
            }
            
            response = self._make_api_request("/chat/completions", payload)
            
            return self._parse_bias_response(response)
            
        except Exception as e:
            logger.error(f"Error in bias detection: {e}")
            raise GrokAPIError(f"Bias detection failed: {str(e)}")
    
    def _construct_critical_analysis_prompt(
        self,
        content: str,
        analysis_type: str,
        focus_areas: Optional[List[str]]
    ) -> str:
        """Construct a critical analysis prompt."""
        prompt = f"""
        Perform a critical analysis of the following content:
        
        Content:
        {content}
        
        Analysis Type: {analysis_type}
        
        Please provide a comprehensive critical analysis including:
        1. Strengths and positive aspects
        2. Weaknesses and limitations
        3. Methodological concerns
        4. Evidence quality assessment
        5. Logical consistency
        6. Completeness of coverage
        7. Bias or perspective issues
        8. Recommendations for improvement
        9. Overall assessment and rating
        """
        
        if focus_areas:
            prompt += f"\n\nFocus particularly on these areas: {', '.join(focus_areas)}"
        
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
            GrokAPIError: If request fails after retries
        """
        url = f"{self.base_url}{endpoint}"
        
        response = self.session.post(
            url,
            json=payload,
            timeout=AppConfig.TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()

        if response.status_code == 429 or response.status_code >= 500:
            logger.warning(f"Retryable error: {response.status_code}. Decorator will handle retry.")
            response.raise_for_status()

        elif response.status_code == 401:
            raise GrokAPIError("Authentication failed - check API key")
        elif response.status_code == 400:
            raise GrokAPIError(f"Bad request: {response.text}")
        else:
            logger.error(f"API error: {response.status_code}, {response.text}")
            raise GrokAPIError(f"API error: {response.status_code}")
    
    def _parse_analysis_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse critical analysis response."""
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return {
                "analysis": content,
                "model_used": response.get("model", self.model),
                "usage": response.get("usage", {}),
                "timestamp": time.time(),
                "analysis_type": "critical_analysis"
            }
            
        except Exception as e:
            logger.error(f"Error parsing analysis response: {e}")
            return {
                "analysis": "Error parsing response",
                "error": str(e)
            }
    
    def _parse_methodology_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse methodology review response."""
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return {
                "methodology_review": content,
                "model_used": response.get("model", self.model),
                "usage": response.get("usage", {}),
                "timestamp": time.time(),
                "review_type": "methodology"
            }
            
        except Exception as e:
            logger.error(f"Error parsing methodology response: {e}")
            return {
                "methodology_review": "Error parsing response",
                "error": str(e)
            }
    
    def _parse_synthesis_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse synthesis reasoning response."""
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return {
                "synthesis": content,
                "model_used": response.get("model", self.model),
                "usage": response.get("usage", {}),
                "timestamp": time.time(),
                "synthesis_type": "advanced_reasoning"
            }
            
        except Exception as e:
            logger.error(f"Error parsing synthesis response: {e}")
            return {
                "synthesis": "Error parsing response",
                "error": str(e)
            }
    
    def _parse_bias_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse bias detection response."""
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return {
                "bias_assessment": content,
                "model_used": response.get("model", self.model),
                "usage": response.get("usage", {}),
                "timestamp": time.time(),
                "assessment_type": "bias_detection"
            }
            
        except Exception as e:
            logger.error(f"Error parsing bias response: {e}")
            return {
                "bias_assessment": "Error parsing response",
                "error": str(e)
            }


class PRISMAGrokRouter:
    """
    Specialized router for PRISMA systematic review using Grok.
    
    Provides domain-specific methods for different phases of critical analysis.
    """
    
    def __init__(self, client: Optional[GrokClient] = None):
        """
        Initialize the PRISMA Grok router.
        
        Args:
            client: Optional Grok client (creates default if None)
        """
        self.client = client or GrokClient()
    
    def review_search_strategy(self, search_strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Review and critique search strategy."""
        return self.client.critical_analysis(
            content=json.dumps(search_strategy, indent=2),
            analysis_type="search_strategy",
            focus_areas=["comprehensiveness", "bias_reduction", "database_selection"]
        )
    
    def assess_study_quality(self, study_details: Dict[str, Any]) -> Dict[str, Any]:
        """Assess individual study quality."""
        return self.client.methodology_review(
            study_details=study_details,
            review_standards=["CONSORT", "STROBE", "PRISMA-P"]
        )
    
    def analyze_evidence_synthesis(self, synthesis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze evidence synthesis for quality and completeness."""
        return self.client.critical_analysis(
            content=json.dumps(synthesis_data, indent=2),
            analysis_type="evidence_synthesis",
            focus_areas=["completeness", "bias_assessment", "strength_of_evidence"]
        )
    
    def detect_publication_bias(self, study_collection: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect potential publication bias in study collection."""
        return self.client.bias_detection(
            study_content=json.dumps(study_collection, indent=2),
            bias_types=["publication_bias", "selection_bias", "reporting_bias"]
        )
    
    def final_review_critique(self, complete_review: str) -> Dict[str, Any]:
        """Provide final critique of complete systematic review."""
        return self.client.critical_analysis(
            content=complete_review,
            analysis_type="complete_review",
            focus_areas=["PRISMA_compliance", "scientific_rigor", "clinical_relevance"]
        ) 