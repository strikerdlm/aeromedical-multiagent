"""
Configuration module for the Multi-Agent Prompt Enhancer.

This module manages API keys, OpenAI model configurations,
and application settings.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Any, Optional
# The python-dotenv package is optional for basic operation. If it is not
# installed (as may be the case in restricted test environments) fall back to
# a no-op implementation so the module can still be imported.
try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover - fallback stub
    def load_dotenv(*args, **kwargs):
        return False

# Load environment variables
load_dotenv()


@dataclass
class ModelConfig:
    """Configuration for OpenAI models."""
    
    model_name: str
    max_tokens: int = 4000
    temperature: float = 0.3
    reasoning_effort: str = "medium"  # For reasoning models
    
    
class OpenAIModelsConfig:
    """Configuration for OpenAI models used in the system."""
    
    # Enhanced OpenAI Models
    O3_DEEP_RESEARCH: ModelConfig = ModelConfig(
        model_name="o3-deep-research-2025-06-26",
        max_tokens=8000,
        temperature=0.4,
        reasoning_effort="high"
    )
    
    O3_REASONING: ModelConfig = ModelConfig(
        model_name="o3",
        max_tokens=4000,
        temperature=0.3,
        reasoning_effort="high"
    )
    
    # Fallback model for PRISMA
    O4_MINI_DEEP_RESEARCH: ModelConfig = ModelConfig(
        model_name="o4-mini-deep-research-2025-06-26",
        max_tokens=8000,
        temperature=0.3,
        reasoning_effort="high"
    )
    
    # Standard models for enhancement
    GPT4_MINI: ModelConfig = ModelConfig(
        model_name="gpt-4o-mini",
        max_tokens=2000,
        temperature=0.2
    )


@dataclass
class ChatflowConfig:
    """Configuration for a specific Flowise chatflow."""
    
    chatflow_id: str
    session_id: str
    return_source_documents: bool = True
    streaming: bool = True
    temperature: float = 0.3
    max_tokens: int = 2000


class PRISMAConfig:
    """Configuration for PRISMA systematic review feature."""
    
    # Required models and reasoning effort
    O3_HIGH_REASONING = ModelConfig(
        model_name="o3-deep-research-2025-06-26",
        max_tokens=10000,
        temperature=0.3,
        reasoning_effort="high"
    )
    
    # Fallback model for PRISMA
    O4_MINI_FALLBACK = ModelConfig(
        model_name="o4-mini-deep-research-2025-06-26",
        max_tokens=10000,
        temperature=0.3,
        reasoning_effort="high"
    )
    
    # Perplexity configuration
    PERPLEXITY_BASE_URL: str = "https://api.perplexity.ai"
    PERPLEXITY_MODEL: str = "sonar-deep-research"
    
    # Grok configuration
    GROK_BASE_URL: str = "https://api.x.ai/v1"
    GROK_MODEL: str = "grok-beta"
    
    # PRISMA-specific settings
    TARGET_WORD_COUNT: int = 8000  # Minimum target word count
    MAX_WORD_COUNT: int = 10000  # Maximum target word count
    MIN_CITATIONS: int = 50  # Minimum required citations
    
    # Chatflow configurations for PRISMA
    PRISMA_CHATFLOWS: Dict[str, str] = {
        "research_1": "43677137-d307-4ff4-96c9-5019b6e10879",
        "research_2": "d0bf0d84-1343-4f3b-a887-780d20f9e3c6"
    }


class FlowiseConfig:
    """Central configuration for Flowise API integration."""
    
    # Base configuration
    BASE_URL: str = os.getenv("FLOWISE_API_URL", "https://cloud.flowiseai.com")
    API_KEY: str = os.getenv("FLOWISE_API_KEY", "")
    
    # Chatflow IDs mapping - Only the three available chatflows
    CHATFLOW_IDS: Dict[str, str] = {
        "aeromedical_risk": os.getenv("CHATFLOW_AEROMEDICAL_RISK", ""),
        "deep_research": os.getenv("CHATFLOW_DEEP_RESEARCH", ""),
        "aerospace_medicine_rag": os.getenv("CHATFLOW_AEROSPACE_MEDICINE_RAG", ""),
    }
    
    # Chatflow configurations
    CHATFLOW_CONFIGS: Dict[str, ChatflowConfig] = {
        "aeromedical_risk": ChatflowConfig(
            chatflow_id=CHATFLOW_IDS["aeromedical_risk"],
            session_id="aeromedical_session",
            temperature=0.2,  # Conservative for risk assessment
            max_tokens=2000
        ),
        "deep_research": ChatflowConfig(
            chatflow_id=CHATFLOW_IDS["deep_research"],
            session_id="research_session",
            temperature=0.4,
            max_tokens=4000
        ),
        "aerospace_medicine_rag": ChatflowConfig(
            chatflow_id=CHATFLOW_IDS["aerospace_medicine_rag"],
            session_id="aerospace_medicine_session",
            temperature=0.3,
            max_tokens=3000
        ),
    }
    
    @classmethod
    def get_headers(cls) -> Dict[str, str]:
        """Get HTTP headers for Flowise API requests."""
        return {
            "Authorization": f"Bearer {cls.API_KEY}",
            "Content-Type": "application/json"
        }
    
    @classmethod
    def get_chatflow_config(cls, flow_type: str) -> Optional[ChatflowConfig]:
        """Get configuration for a specific chatflow type."""
        return cls.CHATFLOW_CONFIGS.get(flow_type)


class AppConfig:
    """Application-wide configuration settings."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    # Web Search Configuration (for o3 with web search)
    SEARCH_API_KEY: str = os.getenv("SEARCH_API_KEY", "")  # For web search functionality
    SEARCH_ENGINE_ID: str = os.getenv("SEARCH_ENGINE_ID", "")  # Google Custom Search ID
    
    # PRISMA-specific API configurations
    PPLX_API_KEY: str = os.getenv("PPLX_API_KEY", "")  # Perplexity API key
    XAI_API_KEY: str = os.getenv("XAI_API_KEY", "")  # Grok API key
    
    # Application settings
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY: float = float(os.getenv("RETRY_DELAY", "1.0"))
    TIMEOUT: int = int(os.getenv("TIMEOUT", "60"))  # Increased for reasoning models
    
    # Logging configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Model routing configuration
    SCIENCE_TECH_KEYWORDS: list = [
        "science", "technology", "research", "study", "analysis", "data",
        "biology", "chemistry", "physics", "engineering", "mathematics",
        "computer", "AI", "machine learning", "quantum", "molecular",
        "genetic", "medical", "clinical", "pharmaceutical", "biomedical",
        "space", "astronomy", "aerospace", "environmental", "climate"
    ]
    
    @classmethod
    def validate_environment(cls) -> bool:
        """
        Validate that required environment variables are set.
        
        Returns:
            True if all required variables are set, False otherwise
        """
        missing_vars = []
        
        # Check required variables
        if not cls.OPENAI_API_KEY:
            missing_vars.append("OPENAI_API_KEY")
        
        if not FlowiseConfig.API_KEY:
            missing_vars.append("FLOWISE_API_KEY")
        
        if missing_vars:
            print("❌ Error: Missing required environment variables:")
            for var in missing_vars:
                print(f"   - {var}")
            print("\n📝 Please create a .env file with the required variables.")
            print("   See the README.md for setup instructions.")
            return False
        
        return True
    
    @classmethod
    def validate_prisma_environment(cls) -> bool:
        """
        Validate that PRISMA-specific environment variables are set.
        
        Returns:
            True if all PRISMA variables are set, False otherwise
        """
        missing_vars = []
        
        # Check PRISMA-specific variables
        if not cls.OPENAI_API_KEY:
            missing_vars.append("OPENAI_API_KEY")
        
        if not FlowiseConfig.API_KEY:
            missing_vars.append("FLOWISE_API_KEY")
        
        if not cls.PPLX_API_KEY:
            missing_vars.append("PPLX_API_KEY")
        
        if not cls.XAI_API_KEY:
            missing_vars.append("XAI_API_KEY")
        
        if missing_vars:
            print("❌ Error: Missing PRISMA-specific environment variables:")
            for var in missing_vars:
                print(f"   - {var}")
            print("\n📝 Please configure all required API keys for PRISMA functionality.")
            print("   PRISMA requires: OpenAI, Flowise, Perplexity, and Grok API keys.")
            return False
        
        return True
    
    @classmethod
    def validate_chatflow_ids(cls) -> Dict[str, bool]:
        """
        Validate that chatflow IDs are configured for available features.
        
        Returns:
            Dictionary mapping chatflow names to availability status
        """
        chatflow_status = {}
        
        for name, chatflow_id in FlowiseConfig.CHATFLOW_IDS.items():
            chatflow_status[name] = bool(chatflow_id)
        
        return chatflow_status 