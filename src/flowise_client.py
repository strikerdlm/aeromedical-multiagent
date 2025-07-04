"""
Flowise API Client for multi-agent prompt enhancement.

This module provides a robust client for interacting with Flowise chatflows,
including error handling, retry logic, and streaming support.
"""

from __future__ import annotations

import json
import time
import logging
from typing import Dict, Any, Optional, Generator, Union
import requests
from requests.exceptions import RequestException

from .config import FlowiseConfig, ChatflowConfig, AppConfig


logger = logging.getLogger(__name__)


class FlowiseAPIError(Exception):
    """Custom exception for Flowise API errors."""
    pass


class FlowiseClient:
    """
    Robust client for interacting with Flowise API.
    
    Provides methods for sending messages to chatflows with proper error
    handling, retry logic, and streaming support.
    """
    
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the Flowise client.
        
        Args:
            base_url: Flowise API base URL (optional, uses config default)
            api_key: Flowise API key (optional, uses config default)
        """
        self.base_url = base_url or FlowiseConfig.BASE_URL
        self.api_key = api_key or FlowiseConfig.API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def send_message(
        self,
        chatflow_id: str,
        question: str,
        config: Optional[Dict[str, Any]] = None,
        streaming: bool = False
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        Send a message to a specific Flowise chatflow.
        
        Args:
            chatflow_id: The ID of the chatflow to send the message to
            question: The question/prompt to send
            config: Optional configuration overrides
            streaming: Whether to use streaming response
            
        Returns:
            Response data (dict) or streaming generator
            
        Raises:
            FlowiseAPIError: If the API request fails
        """
        url = f"{self.base_url}/api/v1/prediction/{chatflow_id}"
        
        payload = {
            "question": question,
            "streaming": streaming
        }
        
        # Add configuration if provided
        if config:
            payload.update(config)
        
        if streaming:
            return self._send_streaming_message(url, payload)
        else:
            return self._send_regular_message(url, payload)
    
    def send_message_with_config(
        self,
        flow_type: str,
        question: str,
        **kwargs
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """
        Send message using predefined chatflow configuration.
        
        Args:
            flow_type: The type of chatflow (e.g., 'deep_research', 'agentic_rag')
            question: The question/prompt to send
            **kwargs: Additional configuration overrides
            
        Returns:
            Response data or streaming generator
            
        Raises:
            FlowiseAPIError: If the chatflow type is unknown or API request fails
        """
        config = FlowiseConfig.get_chatflow_config(flow_type)
        if not config:
            raise FlowiseAPIError(f"Unknown chatflow type: {flow_type}")
        
        # Prepare payload with config
        payload = {
            "sessionId": config.session_id,
            "returnSourceDocuments": config.return_source_documents,
            "streaming": config.streaming,
            "overrideConfig": {
                "temperature": config.temperature,
                "maxTokens": config.max_tokens
            }
        }
        
        # Apply any overrides
        payload.update(kwargs)
        
        return self.send_message(
            config.chatflow_id,
            question,
            payload,
            streaming=config.streaming
        )
    
    def _send_regular_message(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send a regular (non-streaming) message with retry logic."""
        return self._safe_api_call(
            lambda: self.session.post(url, json=payload, timeout=AppConfig.TIMEOUT)
        )
    
    def _send_streaming_message(
        self,
        url: str,
        payload: Dict[str, Any]
    ) -> Generator[Dict[str, Any], None, None]:
        """Send a streaming message and yield chunks."""
        def make_request():
            return self.session.post(
                url,
                json=payload,
                stream=True,
                timeout=AppConfig.TIMEOUT
            )
        
        response = self._safe_api_call(make_request, return_raw=True)
        
        try:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        if data != '[DONE]':
                            try:
                                yield json.loads(data)
                            except json.JSONDecodeError:
                                yield {"event": "data", "data": data}
        except Exception as e:
            logger.error(f"Error processing streaming response: {e}")
            raise FlowiseAPIError(f"Streaming error: {e}")
        finally:
            response.close()
    
    def _safe_api_call(
        self,
        func,
        max_retries: Optional[int] = None,
        delay: Optional[float] = None,
        return_raw: bool = False
    ) -> Union[Dict[str, Any], requests.Response]:
        """
        Make API call with retry logic and error handling.
        
        Args:
            func: Function to execute (should return requests.Response)
            max_retries: Maximum number of retries
            delay: Delay between retries
            return_raw: Whether to return raw response or JSON
            
        Returns:
            Response data or raw response object
            
        Raises:
            FlowiseAPIError: If all retries are exhausted or critical error occurs
        """
        max_retries = max_retries or AppConfig.MAX_RETRIES
        delay = delay or AppConfig.RETRY_DELAY
        
        for attempt in range(max_retries):
            try:
                response = func()
                
                if response.status_code == 200:
                    if return_raw:
                        return response
                    return response.json()
                elif response.status_code == 429:  # Rate limit
                    logger.warning(f"Rate limited, attempt {attempt + 1}/{max_retries}")
                    time.sleep(delay * (2 ** attempt))
                    continue
                elif response.status_code == 401:
                    raise FlowiseAPIError("Authentication failed - check API key")
                elif response.status_code == 404:
                    raise FlowiseAPIError("Chatflow not found - check chatflow ID")
                else:
                    logger.error(f"API error: {response.status_code}, {response.text}")
                    raise FlowiseAPIError(f"API error: {response.status_code}")
                    
            except RequestException as e:
                logger.error(f"Request exception on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise FlowiseAPIError(f"Request failed after {max_retries} attempts: {e}")
                time.sleep(delay * (2 ** attempt))
        
        raise FlowiseAPIError("Max retries exceeded")
    
    def get_all_chatflows(self) -> Dict[str, Any]:
        """
        Retrieve all available chatflows.
        
        Returns:
            Dictionary containing all chatflows
            
        Raises:
            FlowiseAPIError: If the API request fails
        """
        url = f"{self.base_url}/api/v1/chatflows"
        return self._safe_api_call(lambda: self.session.get(url, timeout=AppConfig.TIMEOUT))
    
    def get_chatflow(self, chatflow_id: str) -> Dict[str, Any]:
        """
        Get details of a specific chatflow.
        
        Args:
            chatflow_id: The ID of the chatflow
            
        Returns:
            Chatflow details
            
        Raises:
            FlowiseAPIError: If the API request fails
        """
        url = f"{self.base_url}/api/v1/chatflows/{chatflow_id}"
        return self._safe_api_call(lambda: self.session.get(url, timeout=AppConfig.TIMEOUT))


class MedicalFlowiseRouter(FlowiseClient):
    """
    Specialized router for medical and research-focused chatflows.
    
    Provides domain-specific methods for different types of medical
    and research queries.
    """
    
    def consult_deep_research(self, query: str) -> Generator[Dict[str, Any], None, None]:
        """Query the deep research chatflow for comprehensive analysis."""
        return self.send_message_with_config("deep_research", query)
    
    def consult_agentic_rag(self, query: str) -> Generator[Dict[str, Any], None, None]:
        """Query the agentic RAG system for enhanced responses."""
        return self.send_message_with_config("agentic_rag", query)
    
    def consult_pubmed(self, query: str) -> Dict[str, Any]:
        """Query PubMed medical literature (non-streaming)."""
        return self.send_message_with_config("pubmed", query, streaming=False)
    
    def consult_nasa_hrp(self, query: str) -> Dict[str, Any]:
        """Query NASA Human Research Program data."""
        return self.send_message_with_config("nasa_hrp", query)
    
    def consult_aeromedical_risk(self, query: str) -> Dict[str, Any]:
        """Query aeromedical risk assessment chatflow."""
        return self.send_message_with_config("aeromedical_risk", query)
    
    def route_medical_query(self, query_type: str, question: str) -> Union[Dict[str, Any], Generator]:
        """
        Route medical queries to appropriate specialized chatflows.
        
        Args:
            query_type: Type of query ('research', 'medical', 'nasa', etc.)
            question: The actual question to ask
            
        Returns:
            Response from the appropriate chatflow
            
        Raises:
            FlowiseAPIError: If query_type is unknown
        """
        routing_map = {
            "research": "deep_research",
            "medical": "physiology_rag",
            "nasa": "nasa_hrp",
            "agentic": "agentic_rag",
            "pubmed": "pubmed",
            "aeromedical": "aeromedical_risk",
        }
        
        if query_type not in routing_map:
            available_types = ", ".join(routing_map.keys())
            raise FlowiseAPIError(f"Unknown query type '{query_type}'. Available: {available_types}")
        
        flow_type = routing_map[query_type]
        return self.send_message_with_config(flow_type, question) 