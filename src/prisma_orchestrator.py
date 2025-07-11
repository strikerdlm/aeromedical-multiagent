"""
PRISMA Systematic Review Orchestrator.

This module provides the main orchestration interface for the PRISMA
systematic review feature, integrating all AI models and agents.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import asdict

from .agents import AgentOrchestrator
from .config import AppConfig, PRISMAConfig
from .prisma_agents import PRISMAAgentSystem, PRISMAWorkflow, create_prisma_agent_system
from .perplexity_client import PerplexityClient
from .grok_client import GrokClient
from .flowise_client import FlowiseClient
from .openai_enhanced_client import EnhancedOpenAIClient, create_enhanced_openai_client


logger = logging.getLogger(__name__)


class PRISMAOrchestrator:
    """
    Main orchestrator for PRISMA systematic review generation.
    
    This class coordinates all AI models and agents to produce
    comprehensive, PRISMA-compliant systematic reviews.
    """
    
    def __init__(self):
        """Initialize the PRISMA orchestrator with all required components."""
        # Validate environment before initialization
        if not AppConfig.validate_prisma_environment():
            raise ValueError("PRISMA environment validation failed. Please check API keys.")
        
        # Initialize core components
        self.agent_orchestrator = AgentOrchestrator()
        self.prisma_agents = create_prisma_agent_system()
        self.prisma_system = PRISMAAgentSystem(self.agent_orchestrator)
        
        # Initialize AI clients
        self.openai_client = create_enhanced_openai_client()
        self.perplexity_client = PerplexityClient()
        self.grok_client = GrokClient()
        self.flowise_client = FlowiseClient()
        
        # Track current workflow
        self.current_workflow: Optional[PRISMAWorkflow] = None
        self.session_history: List[Dict[str, Any]] = []
        
        logger.info("PRISMA orchestrator initialized successfully")
    
    def create_systematic_review(
        self,
        research_question: str,
        search_keywords: List[str],
        inclusion_criteria: List[str],
        exclusion_criteria: List[str],
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a complete PRISMA systematic review using code-based orchestration.
        
        Args:
            research_question: Primary research question
            search_keywords: Keywords for literature search
            inclusion_criteria: Study inclusion criteria
            exclusion_criteria: Study exclusion criteria
            additional_context: Additional context or requirements
            
        Returns:
            Complete systematic review with metadata
        """
        try:
            logger.info(f"Starting PRISMA systematic review creation for: {research_question}")
            
            # Initialize workflow state and tools
            search_strategy = {
                "keywords": search_keywords,
                "databases": ["PubMed", "Google Scholar", "Cochrane Library", "Web of Science"],
                "date_range": "2010-2024",
                "language": "English",
                "additional_context": additional_context
            }
            self.prisma_system.tools.initialize_workflow(
                research_question, search_strategy, inclusion_criteria, exclusion_criteria
            )

            # --- Code-based Agent Orchestration ---
            
            # 1. Searcher Agent
            searcher_agent = self.prisma_system.create_searcher_agent()
            search_task = self.agent_orchestrator.run_full_turn(
                agent=searcher_agent,
                messages=[{"role": "user", "content": "Conduct a systematic literature search based on the initialized workflow."}]
            )
            
            # 2. Reviewer Agent
            reviewer_agent = self.prisma_system.create_reviewer_agent()
            review_task = self.agent_orchestrator.run_full_turn(
                agent=reviewer_agent,
                messages=search_task.messages + [{"role": "user", "content": "Screen the search results and then extract and analyze the data."}]
            )

            # 3. Writer Agent
            writer_agent = self.prisma_system.create_writer_agent()
            write_task = self.agent_orchestrator.run_full_turn(
                agent=writer_agent,
                messages=review_task.messages + [{"role": "user", "content": "Generate the complete systematic review document."}]
            )
            
            # 4. Validator Agent
            validator_agent = self.prisma_system.create_validator_agent()
            validation_task = self.agent_orchestrator.run_full_turn(
                agent=validator_agent,
                messages=write_task.messages + [{"role": "user", "content": "Validate the final review, generate the PRISMA flow diagram, and then export the final review document to a markdown file."}]
            )

            # --- End Orchestration ---

            # Extract final outputs from the entire workflow
            final_validation_summary = validation_task.messages[-1].get("content", "")
            systematic_review = ""
            for msg in reversed(write_task.messages):
                if msg.get("role") == "assistant":
                    systematic_review = msg.get("content", "")
                    break

            flow_diagram = self.prisma_system.tools.generate_prisma_flow_diagram()

            final_report = f"{systematic_review}\n\n# PRISMA Flow Diagram\n\n{flow_diagram}"

            # The export path will be in the validation summary
            export_path_message = final_validation_summary
            
            # Compile workflow results
            workflow_results = {
                "systematic_review": final_report,
                "export_path": export_path_message,
                "research_question": research_question,
                "search_strategy": search_strategy,
                "inclusion_criteria": inclusion_criteria,
                "exclusion_criteria": exclusion_criteria,
                "workflow_metadata": {
                    "total_messages": len(validation_task.messages),
                    "agents_used": ["Searcher", "Reviewer", "Writer", "Validator"],
                    "completion_time": time.time(),
                    "word_count": len(final_report.split()),
                    "estimated_citations": final_report.count("(") + final_report.count("[")
                },
                "validation_status": self._validate_systematic_review(final_report),
                "session_id": f"prisma_{int(time.time())}"
            }
            
            # Store in session history
            self.session_history.append(workflow_results)
            
            logger.info(f"PRISMA systematic review completed: {workflow_results['workflow_metadata']['word_count']} words")
            return workflow_results
            
        except Exception as e:
            logger.error(f"Error creating systematic review: {e}")
            return {
                "error": str(e),
                "research_question": research_question,
                "status": "failed",
                "timestamp": time.time()
            }
    
    def quick_prisma_review(self, topic: str) -> Dict[str, Any]:
        """
        Generate a quick PRISMA review for a given topic.
        
        Args:
            topic: Research topic or question
            
        Returns:
            Quick systematic review results
        """
        try:
            # Auto-generate criteria based on topic
            search_keywords = self._extract_keywords(topic)
            inclusion_criteria = [
                "Peer-reviewed articles",
                "Published in English",
                "Published 2015-2024",
                "Relevant to research question",
                "Adequate sample size (n≥10)"
            ]
            exclusion_criteria = [
                "Non-peer reviewed sources",
                "Case reports with n<10",
                "Opinion pieces",
                "Duplicate publications",
                "Studies with major methodological flaws"
            ]
            
            return self.create_systematic_review(
                research_question=f"What is the current evidence on {topic}?",
                search_keywords=search_keywords,
                inclusion_criteria=inclusion_criteria,
                exclusion_criteria=exclusion_criteria,
                additional_context=f"Focus on recent high-quality evidence for {topic}"
            )
            
        except Exception as e:
            logger.error(f"Error in quick PRISMA review: {e}")
            return {
                "error": str(e),
                "topic": topic,
                "status": "failed",
                "timestamp": time.time()
            }
    
    def get_prisma_status(self) -> Dict[str, Any]:
        """
        Get current PRISMA system status and capabilities.
        
        Returns:
            System status and configuration
        """
        try:
            # Check API connectivity
            api_status = {
                "openai": self._check_openai_connectivity(),
                "perplexity": self._check_perplexity_connectivity(),
                "grok": self._check_grok_connectivity(),
                "flowise": self._check_flowise_connectivity()
            }
            
            # System capabilities
            capabilities = {
                "models_available": {
                    "o3_deep_research": PRISMAConfig.O3_HIGH_REASONING.model_name,
                    "perplexity_research": PRISMAConfig.PERPLEXITY_MODEL,
                    "grok_reasoning": PRISMAConfig.GROK_MODEL,
                    "flowise_chatflows": list(PRISMAConfig.PRISMA_CHATFLOWS.keys())
                },
                "target_specifications": {
                    "word_count_range": f"{PRISMAConfig.TARGET_WORD_COUNT}-{PRISMAConfig.MAX_WORD_COUNT}",
                    "minimum_citations": PRISMAConfig.MIN_CITATIONS,
                    "prisma_compliance": "PRISMA 2020 guidelines"
                },
                "workflow_phases": [
                    "Planning", "Literature Search", "Screening", 
                    "Data Extraction", "Analysis", "Writing", "Validation"
                ]
            }
            
            return {
                "status": "active",
                "api_connectivity": api_status,
                "capabilities": capabilities,
                "session_history_count": len(self.session_history),
                "current_workflow_active": self.current_workflow is not None,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error getting PRISMA status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": time.time()
            }
    
    def list_recent_reviews(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List recent PRISMA reviews from session history.
        
        Args:
            limit: Maximum number of reviews to return
            
        Returns:
            List of recent review summaries
        """
        try:
            recent_reviews = []
            
            for review in self.session_history[-limit:]:
                summary = {
                    "session_id": review.get("session_id"),
                    "research_question": review.get("research_question"),
                    "word_count": review.get("workflow_metadata", {}).get("word_count", 0),
                    "estimated_citations": review.get("workflow_metadata", {}).get("estimated_citations", 0),
                    "validation_status": review.get("validation_status", {}),
                    "completion_time": review.get("workflow_metadata", {}).get("completion_time"),
                    "status": "completed" if "systematic_review" in review else "failed"
                }
                recent_reviews.append(summary)
            
            return recent_reviews
            
        except Exception as e:
            logger.error(f"Error listing recent reviews: {e}")
            return []
    
    def export_review(self, session_id: str, format: str = "markdown") -> Optional[str]:
        """
        Export a systematic review by session ID.
        
        Args:
            session_id: Session ID of the review to export
            format: Export format ('markdown', 'json')
            
        Returns:
            Exported review content or None if not found
        """
        try:
            # Find the review by session ID
            review = None
            for r in self.session_history:
                if r.get("session_id") == session_id:
                    review = r
                    break
            
            if not review:
                logger.warning(f"Review not found for session ID: {session_id}")
                return None
            
            if format == "markdown":
                return review.get("systematic_review", "")
            elif format == "json":
                return json.dumps(review, indent=2)
            else:
                logger.error(f"Unsupported export format: {format}")
                return None
                
        except Exception as e:
            logger.error(f"Error exporting review: {e}")
            return None
    
    def _extract_keywords(self, topic: str) -> List[str]:
        """Extract relevant keywords from a topic."""
        try:
            # Simple keyword extraction - could be enhanced with NLP
            topic_lower = topic.lower()
            
            # Common research keywords
            common_keywords = [
                "systematic review", "meta-analysis", "randomized controlled trial",
                "clinical trial", "cohort study", "case-control study",
                "intervention", "treatment", "therapy", "prevention"
            ]
            
            # Extract key terms from topic
            words = topic_lower.split()
            keywords = [word for word in words if len(word) > 3]
            
            # Add some topic-specific terms
            keywords.extend([topic, topic_lower])
            
            return list(set(keywords))[:10]  # Limit to 10 keywords
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return [topic]
    
    def _validate_systematic_review(self, review_content: str) -> Dict[str, Any]:
        """Validate systematic review content."""
        try:
            word_count = len(review_content.split())
            estimated_citations = review_content.count("(") + review_content.count("[")
            
            # Check for required sections
            required_sections = ["abstract", "introduction", "methods", "results", "discussion"]
            sections_present = {
                section: section.lower() in review_content.lower()
                for section in required_sections
            }
            
            # Check PRISMA compliance
            prisma_elements = ["prisma", "systematic review", "search strategy", "inclusion criteria"]
            prisma_present = {
                element: element.lower() in review_content.lower()
                for element in prisma_elements
            }
            
            # Calculate overall score
            section_score = sum(sections_present.values()) / len(sections_present)
            prisma_score = sum(prisma_present.values()) / len(prisma_elements)
            word_score = min(word_count / PRISMAConfig.TARGET_WORD_COUNT, 1.0)
            citation_score = min(estimated_citations / PRISMAConfig.MIN_CITATIONS, 1.0)
            
            overall_score = (section_score + prisma_score + word_score + citation_score) / 4
            
            return {
                "word_count": word_count,
                "estimated_citations": estimated_citations,
                "sections_present": sections_present,
                "prisma_elements": prisma_present,
                "scores": {
                    "sections": section_score,
                    "prisma": prisma_score,
                    "word_count": word_score,
                    "citations": citation_score,
                    "overall": overall_score
                },
                "meets_minimum_requirements": (
                    word_count >= PRISMAConfig.TARGET_WORD_COUNT * 0.8 and
                    estimated_citations >= PRISMAConfig.MIN_CITATIONS * 0.8 and
                    overall_score >= 0.7
                ),
                "validation_timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error validating systematic review: {e}")
            return {
                "error": str(e),
                "validation_timestamp": time.time()
            }
    
    def _check_openai_connectivity(self) -> Dict[str, Any]:
        """Check OpenAI API connectivity."""
        try:
            response = self.openai_client.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            return {"status": "connected", "model": "gpt-4o-mini"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _check_perplexity_connectivity(self) -> Dict[str, Any]:
        """Check Perplexity API connectivity."""
        try:
            # Simple connectivity test
            if AppConfig.PPLX_API_KEY:
                return {"status": "configured", "model": PRISMAConfig.PERPLEXITY_MODEL}
            else:
                return {"status": "not_configured", "error": "API key missing"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _check_grok_connectivity(self) -> Dict[str, Any]:
        """Check Grok API connectivity."""
        try:
            # Simple connectivity test
            if AppConfig.XAI_API_KEY:
                return {"status": "configured", "model": PRISMAConfig.GROK_MODEL}
            else:
                return {"status": "not_configured", "error": "API key missing"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    def _check_flowise_connectivity(self) -> Dict[str, Any]:
        """Check Flowise API connectivity."""
        try:
            # Test connection to Flowise
            if AppConfig.FLOWISE_API_KEY:
                return {
                    "status": "configured",
                    "chatflows": list(PRISMAConfig.PRISMA_CHATFLOWS.keys())
                }
            else:
                return {"status": "not_configured", "error": "API key missing"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}


# Factory function for creating PRISMA orchestrator
def create_prisma_orchestrator() -> PRISMAOrchestrator:
    """
    Create and initialize a PRISMA orchestrator.
    
    Returns:
        Configured PRISMA orchestrator instance
        
    Raises:
        ValueError: If environment validation fails
    """
    try:
        return PRISMAOrchestrator()
    except Exception as e:
        logger.error(f"Failed to create PRISMA orchestrator: {e}")
        raise ValueError(f"PRISMA orchestrator creation failed: {str(e)}")


# Testing and validation functions
def test_prisma_system() -> Dict[str, Any]:
    """Test the PRISMA system with a simple example."""
    try:
        orchestrator = create_prisma_orchestrator()
        
        # Test system status
        status = orchestrator.get_prisma_status()
        
        # Test quick review (if APIs are available)
        if status.get("api_connectivity", {}).get("openai", {}).get("status") == "connected":
            quick_review = orchestrator.quick_prisma_review("machine learning in healthcare")
            return {
                "status": "success",
                "system_status": status,
                "test_review": quick_review
            }
        else:
            return {
                "status": "partial",
                "system_status": status,
                "message": "APIs not fully configured for testing"
            }
            
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e)
        }


if __name__ == "__main__":
    # Run system test
    logging.basicConfig(level=logging.INFO)
    test_results = test_prisma_system()
    print(json.dumps(test_results, indent=2)) 