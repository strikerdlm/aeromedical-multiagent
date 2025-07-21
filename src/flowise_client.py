"""
Flowise API Client for multi-agent prompt enhancement.

This module provides a simple client for interacting with Flowise chatflows,
using the exact same pattern as the working examples.
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional, Union, List
import requests

from .config import FlowiseConfig
from .utils import retry_with_exponential_backoff


logger = logging.getLogger(__name__)


class FlowiseAPIError(Exception):
    """Custom exception for Flowise API errors."""
    pass


class ConfigurationError(Exception):
    """Custom exception for configuration errors."""
    pass


class FlowiseClient:
    """
    Simple client for interacting with Flowise API.
    
    Uses the exact same pattern as the working examples:
    - Direct requests.post call
    - Simple headers with Authorization Bearer token
    - JSON payload with question
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
        
        if not self.api_key:
            raise ConfigurationError("Flowise API key is not configured. Please set the FLOWISE_API_KEY environment variable.")

        # Create headers exactly like the working examples
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    @retry_with_exponential_backoff(allowed_exceptions=(requests.exceptions.RequestException,))
    def query_chatflow(self, chatflow_id: str, question: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Query a specific Flowise chatflow.
        
        Uses the exact same pattern as the working examples:
        requests.post(API_URL, headers=headers, json=payload)
        
        Args:
            chatflow_id: The ID of the chatflow to query
            question: The question to ask
            session_id: The session ID for the conversation
            
        Returns:
            Response JSON from Flowise API
            
        Raises:
            FlowiseAPIError: If the API request fails
        """
        api_url = f"{self.base_url}/api/v1/prediction/{chatflow_id}"
        payload = {"question": question}
        if session_id:
            payload["overrideConfig"] = {"sessionId": session_id}
        
        logger.info(f"Querying Flowise chatflow {chatflow_id} with session {session_id}")
        response = requests.post(api_url, headers=self.headers, json=payload, timeout=20)
        
        if response.status_code == 200:
            result = response.json()
            logger.info("Flowise query completed successfully")
            return result
        
        # For server-side errors, rely on the decorator to retry
        if response.status_code >= 500:
            response.raise_for_status()

        # For client-side errors, fail immediately
        elif response.status_code == 401:
            raise FlowiseAPIError("Authentication failed - check API key")
        elif response.status_code == 404:
            raise FlowiseAPIError(f"Chatflow not found - check chatflow ID: {chatflow_id}")
        else:
            raise FlowiseAPIError(f"API error: {response.status_code} - {response.text}")

    def submit_job(self, chatflow_id: str, question: str, session_id: str) -> bool:
        """
        Submit a job to a Flowise chatflow without waiting for completion.
        
        Args:
            chatflow_id: The ID of the chatflow to query
            question: The question to ask
            session_id: The session ID for the job
            
        Returns:
            True if the job was submitted successfully, False otherwise
        """
        api_url = f"{self.base_url}/api/v1/prediction/{chatflow_id}"
        payload = {
            "question": question,
            "overrideConfig": {"sessionId": session_id}
        }
        
        try:
            # Use a short timeout to fire and forget
            response = requests.post(api_url, headers=self.headers, json=payload, timeout=2)
            # If we get a quick success, that's great
            return response.status_code == 200
        except requests.exceptions.Timeout:
            # A timeout is expected and indicates the job is running
            logger.info(f"Job submitted to Flowise chatflow {chatflow_id} with session {session_id} (timeout expected).")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to submit job to Flowise: {e}")
            return False

    def get_session_history(self, chatflow_id: str, session_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve the chat history for a specific session.
        Flowise organizes history by chatflow and session.

        Args:
            chatflow_id: The ID of the chatflow.
            session_id: The ID of the session.

        Returns:
            A list of chat messages for the session.
        """
        api_url = f"{self.base_url}/api/v1/chatmessage/{chatflow_id}?sessionId={session_id}"
        try:
            response = requests.get(api_url, headers=self.headers, timeout=20)
            if response.status_code == 200:
                # The API returns a list of messages directly
                return response.json()
            else:
                logger.error(f"Failed to get chat history for session {session_id}: {response.status_code} - {response.text}")
                return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed while getting chat history for session {session_id}: {e}")
            return []


class MedicalFlowiseRouter(FlowiseClient):
    """
    Specialized router for medical and research-focused chatflows.
    
    Provides domain-specific methods for the three available chatflows:
    1. Aeromedical Risk - Aviation medicine risk assessment
    2. Deep Research - Comprehensive research analysis  
    3. Aerospace Medicine RAG - Scientific articles and textbooks in aerospace medicine
    """
    
    def consult_deep_research(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Query the deep research chatflow for comprehensive analysis."""
        chatflow_id = FlowiseConfig.CHATFLOW_IDS["deep_research"]
        return self.query_chatflow(chatflow_id, query, session_id)
    
    def consult_aeromedical_risk(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Query aeromedical risk assessment chatflow."""
        chatflow_id = FlowiseConfig.CHATFLOW_IDS["aeromedical_risk"]
        return self.query_chatflow(chatflow_id, query, session_id)
    
    def consult_aerospace_medicine_rag(self, query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Query aerospace medicine RAG chatflow for scientific articles and textbooks."""
        chatflow_id = FlowiseConfig.CHATFLOW_IDS["aerospace_medicine_rag"]
        return self.query_chatflow(chatflow_id, query, session_id)
    
    def route_medical_query(self, query_type: str, question: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Route medical queries to appropriate specialized chatflows.
        
        Args:
            query_type: Type of query ('research', 'aeromedical', 'aerospace_medicine')
            question: The actual question to ask
            
        Returns:
            Response from the appropriate chatflow
            
        Raises:
            FlowiseAPIError: If query_type is unknown
        """
        routing_map = {
            "research": self.consult_deep_research,
            "aeromedical": self.consult_aeromedical_risk,
            "aerospace_medicine": self.consult_aerospace_medicine_rag,
            "medical": self.consult_aerospace_medicine_rag,  # Default medical queries to aerospace medicine RAG
        }
        
        if query_type not in routing_map:
            available_types = ", ".join(routing_map.keys())
            raise FlowiseAPIError(f"Unknown query type '{query_type}'. Available: {available_types}")
        
        return routing_map[query_type](question, session_id) 