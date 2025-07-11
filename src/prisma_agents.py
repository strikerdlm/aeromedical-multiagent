"""
PRISMA Systematic Review Multi-Agent System.

This module implements a comprehensive multi-agent framework for creating
PRISMA-compliant systematic reviews and meta-analyses using OpenAI Agents SDK.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Dict, Any, List, Optional, Generator, Union
from dataclasses import dataclass
from openai import OpenAI

from .agents import Agent, AgentOrchestrator
from .config import AppConfig, PRISMAConfig
from .perplexity_client import PerplexityClient, PRISMAPerplexityRouter
from .grok_client import GrokClient, PRISMAGrokRouter
from .flowise_client import FlowiseClient, FlowiseAPIError


logger = logging.getLogger(__name__)


@dataclass
class PRISMAWorkflow:
    """Data class for PRISMA workflow state and progress."""
    
    research_question: str
    search_strategy: Dict[str, Any]
    inclusion_criteria: List[str]
    exclusion_criteria: List[str]
    current_phase: str = "planning"
    progress: Dict[str, Any] = None
    results: Dict[str, Any] = None
    word_count: int = 0
    citation_count: int = 0
    
    def __post_init__(self):
        if self.progress is None:
            self.progress = {
                "planning": False,
                "searching": False,
                "screening": False,
                "extraction": False,
                "analysis": False,
                "writing": False,
                "validation": False
            }
        if self.results is None:
            self.results = {}


class PRISMAAgentTools:
    """
    Tools for PRISMA systematic review agents.
    
    Provides comprehensive tools for literature search, data extraction,
    analysis, and review generation.
    """
    
    def __init__(self):
        """Initialize PRISMA tools with all required clients."""
        self.openai_client = OpenAI(api_key=AppConfig.OPENAI_API_KEY)
        self.perplexity_client = PerplexityClient()
        self.perplexity_router = PRISMAPerplexityRouter(self.perplexity_client)
        self.grok_client = GrokClient()
        self.grok_router = PRISMAGrokRouter(self.grok_client)
        self.flowise_client = FlowiseClient()
        
        # Store workflow state
        self.workflow: Optional[PRISMAWorkflow] = None
    
    def initialize_workflow(
        self,
        research_question: str,
        search_strategy: Dict[str, Any],
        inclusion_criteria: List[str],
        exclusion_criteria: List[str]
    ) -> str:
        """
        Initialize a new PRISMA systematic review workflow.
        
        Args:
            research_question: Primary research question
            search_strategy: Search strategy configuration
            inclusion_criteria: Study inclusion criteria
            exclusion_criteria: Study exclusion criteria
            
        Returns:
            Workflow initialization confirmation
        """
        try:
            self.workflow = PRISMAWorkflow(
                research_question=research_question,
                search_strategy=search_strategy,
                inclusion_criteria=inclusion_criteria,
                exclusion_criteria=exclusion_criteria
            )
            
            logger.info(f"Initialized PRISMA workflow for: {research_question}")
            return f"✅ PRISMA workflow initialized for research question: {research_question}"
            
        except Exception as e:
            logger.error(f"Error initializing workflow: {e}")
            return f"❌ Failed to initialize workflow: {str(e)}"
    
    def conduct_systematic_search(self) -> str:
        """
        Conduct systematic literature search using multiple sources.
        
        Returns:
            Search results summary
        """
        try:
            if not self.workflow:
                return "❌ No workflow initialized. Please initialize workflow first."
            
            logger.info("Starting systematic literature search...")
            
            # Phase 1: Perplexity deep research
            keywords = self.workflow.search_strategy.get("keywords", [])
            perplexity_results = self.perplexity_router.search_phase(
                self.workflow.research_question, keywords
            )
            
            # Phase 2: Flowise chatflow consultation
            flowise_results = {}
            for chatflow_name, chatflow_id in PRISMAConfig.PRISMA_CHATFLOWS.items():
                try:
                    result = self.flowise_client.send_message(
                        chatflow_id=chatflow_id,
                        question=f"Conduct a systematic literature search for: {self.workflow.research_question}",
                        streaming=False
                    )
                    flowise_results[chatflow_name] = result
                except FlowiseAPIError as e:
                    logger.warning(f"Flowise chatflow {chatflow_name} failed: {e}")
                    flowise_results[chatflow_name] = {"error": str(e)}
            
            # Store search results
            self.workflow.results["search_results"] = {
                "perplexity": perplexity_results,
                "flowise": flowise_results,
                "timestamp": time.time()
            }
            
            self.workflow.progress["searching"] = True
            self.workflow.current_phase = "screening"
            
            # Count initial citations
            perplexity_citations = len(perplexity_results.get("citations", []))
            flowise_citations = sum(
                len(result.get("citations", [])) if isinstance(result, dict) else 0
                for result in flowise_results.values()
            )
            
            total_citations = perplexity_citations + flowise_citations
            
            logger.info(f"Literature search completed with {total_citations} citations")
            return f"✅ Literature search completed. Found {total_citations} potential citations."
            
        except Exception as e:
            logger.error(f"Error in systematic search: {e}")
            return f"❌ Literature search failed: {str(e)}"
    
    def screen_and_filter_studies(self) -> str:
        """
        Screen and filter studies based on inclusion/exclusion criteria.
        
        Returns:
            Screening results summary
        """
        try:
            if not self.workflow or not self.workflow.results.get("search_results"):
                return "❌ No search results available. Please conduct literature search first."
            
            logger.info("Starting study screening and filtering...")
            
            # Extract abstracts from search results
            search_results = self.workflow.results["search_results"]
            abstracts = []
            
            # Process Perplexity results
            perplexity_content = search_results.get("perplexity", {}).get("systematic_review", "")
            if perplexity_content:
                abstracts.append(perplexity_content)
            
            # Process Flowise results
            for chatflow_name, result in search_results.get("flowise", {}).items():
                if isinstance(result, dict) and "text" in result:
                    abstracts.append(result["text"])
            
            # Conduct screening using Perplexity
            screening_results = self.perplexity_router.screening_phase(abstracts)
            
            # Critical analysis using Grok
            grok_analysis = self.grok_router.review_search_strategy(
                self.workflow.search_strategy
            )
            
            # Store screening results
            self.workflow.results["screening_results"] = {
                "perplexity_screening": screening_results,
                "grok_analysis": grok_analysis,
                "timestamp": time.time()
            }
            
            self.workflow.progress["screening"] = True
            self.workflow.current_phase = "extraction"
            
            logger.info("Study screening completed")
            return "✅ Study screening completed. Moving to data extraction phase."
            
        except Exception as e:
            logger.error(f"Error in study screening: {e}")
            return f"❌ Study screening failed: {str(e)}"
    
    def extract_and_analyze_data(self) -> str:
        """
        Extract data from included studies and perform analysis.
        
        Returns:
            Data extraction and analysis summary
        """
        try:
            if not self.workflow or not self.workflow.results.get("screening_results"):
                return "❌ No screening results available. Please complete screening first."
            
            logger.info("Starting data extraction and analysis...")
            
            # Get screening results
            screening_results = self.workflow.results["screening_results"]
            
            # Conduct quality assessment using Grok
            study_collection = []
            if "perplexity_screening" in screening_results:
                study_collection.append(screening_results["perplexity_screening"])
            
            quality_assessment = self.grok_router.assess_study_quality({
                "studies": study_collection,
                "research_question": self.workflow.research_question
            })
            
            # Bias detection using Grok
            bias_assessment = self.grok_router.detect_publication_bias(study_collection)
            
            # Evidence synthesis using Grok
            synthesis_results = self.grok_client.synthesis_reasoning(
                study_findings=study_collection,
                synthesis_approach="narrative"
            )
            
            # Store extraction and analysis results
            self.workflow.results["extraction_analysis"] = {
                "quality_assessment": quality_assessment,
                "bias_assessment": bias_assessment,
                "synthesis_results": synthesis_results,
                "timestamp": time.time()
            }
            
            self.workflow.progress["extraction"] = True
            self.workflow.progress["analysis"] = True
            self.workflow.current_phase = "writing"
            
            logger.info("Data extraction and analysis completed")
            return "✅ Data extraction and analysis completed. Ready for systematic review writing."
            
        except Exception as e:
            logger.error(f"Error in data extraction/analysis: {e}")
            return f"❌ Data extraction/analysis failed: {str(e)}"
    
    def generate_systematic_review(self) -> str:
        """
        Generate the complete PRISMA-compliant systematic review.
        
        Returns:
            Complete systematic review document
        """
        try:
            if not self.workflow or not self.workflow.results.get("extraction_analysis"):
                return "❌ No analysis results available. Please complete data extraction first."
            
            logger.info("Starting systematic review generation...")
            
            # Compile all results
            all_results = {
                "research_question": self.workflow.research_question,
                "search_strategy": self.workflow.search_strategy,
                "inclusion_criteria": self.workflow.inclusion_criteria,
                "exclusion_criteria": self.workflow.exclusion_criteria,
                "search_results": self.workflow.results.get("search_results", {}),
                "screening_results": self.workflow.results.get("screening_results", {}),
                "extraction_analysis": self.workflow.results.get("extraction_analysis", {})
            }
            
            # Generate comprehensive review using O3 high reasoning
            review_prompt = self._construct_systematic_review_prompt(all_results)
            
            response = self.openai_client.chat.completions.create(
                model=PRISMAConfig.O3_HIGH_REASONING.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert systematic review author following PRISMA 2020 guidelines. Generate comprehensive, methodologically sound systematic reviews with proper citations and structure."
                    },
                    {
                        "role": "user",
                        "content": review_prompt
                    }
                ],
                max_tokens=PRISMAConfig.O3_HIGH_REASONING.max_tokens,
                temperature=PRISMAConfig.O3_HIGH_REASONING.temperature,
                # Note: reasoning_effort would be added if supported by the API
            )
            
            review_content = response.choices[0].message.content
            
            # Validate and enhance the review
            validation_results = self._validate_review(review_content)
            
            # Store final review
            self.workflow.results["final_review"] = {
                "content": review_content,
                "validation": validation_results,
                "timestamp": time.time()
            }
            
            self.workflow.progress["writing"] = True
            self.workflow.current_phase = "validation"
            
            # Update metrics
            self.workflow.word_count = len(review_content.split())
            self.workflow.citation_count = review_content.count("(") + review_content.count("[")
            
            logger.info(f"Systematic review generated: {self.workflow.word_count} words, {self.workflow.citation_count} citations")
            return review_content
            
        except Exception as e:
            logger.error(f"Error generating systematic review: {e}")
            return f"❌ Systematic review generation failed: {str(e)}"
    
    def validate_and_finalize_review(self) -> str:
        """
        Validate the systematic review for PRISMA compliance and finalize.
        
        Returns:
            Validation results and final review status
        """
        try:
            if not self.workflow or not self.workflow.results.get("final_review"):
                return "❌ No final review available. Please generate review first."
            
            logger.info("Starting final validation...")
            
            review_content = self.workflow.results["final_review"]["content"]
            
            # Comprehensive validation using Grok
            final_critique = self.grok_router.final_review_critique(review_content)
            
            # Check PRISMA compliance
            prisma_compliance = self._check_prisma_compliance(review_content)
            
            # Final validation results
            validation_summary = {
                "word_count": self.workflow.word_count,
                "citation_count": self.workflow.citation_count,
                "prisma_compliance": prisma_compliance,
                "grok_critique": final_critique,
                "meets_requirements": (
                    self.workflow.word_count >= PRISMAConfig.TARGET_WORD_COUNT and
                    self.workflow.citation_count >= PRISMAConfig.MIN_CITATIONS and
                    prisma_compliance["compliance_score"] >= 0.8
                ),
                "timestamp": time.time()
            }
            
            self.workflow.results["validation_results"] = validation_summary
            self.workflow.progress["validation"] = True
            
            if validation_summary["meets_requirements"]:
                status = "✅ PRISMA systematic review completed successfully!"
                logger.info("PRISMA review validation passed")
            else:
                status = "⚠️ Review generated but needs improvements to meet all requirements."
                logger.warning("PRISMA review validation flagged issues")
            
            return f"{status}\n\nValidation Summary:\n{json.dumps(validation_summary, indent=2)}"
            
        except Exception as e:
            logger.error(f"Error in final validation: {e}")
            return f"❌ Final validation failed: {str(e)}"
    
    def _construct_systematic_review_prompt(self, results: Dict[str, Any]) -> str:
        """Construct the comprehensive systematic review prompt."""
        return f"""
        You are tasked with creating a comprehensive PRISMA-compliant systematic review and meta-analysis.

        # Research Question
        {results['research_question']}

        # Search Strategy
        {json.dumps(results['search_strategy'], indent=2)}

        # Inclusion Criteria
        {chr(10).join(f"- {criteria}" for criteria in results['inclusion_criteria'])}

        # Exclusion Criteria
        {chr(10).join(f"- {criteria}" for criteria in results['exclusion_criteria'])}

        # Search Results Summary
        {json.dumps(results['search_results'], indent=2)}

        # Screening and Quality Assessment
        {json.dumps(results['screening_results'], indent=2)}

        # Data Extraction and Analysis
        {json.dumps(results['extraction_analysis'], indent=2)}

        # Requirements
        Create a comprehensive systematic review that:
        1. Follows PRISMA 2020 guidelines exactly
        2. Contains 8,000-10,000 words
        3. Includes ≥50 peer-reviewed citations in APA format
        4. Has clear sections: Abstract, Introduction, Methods, Results, Discussion
        5. Includes PRISMA flow diagram description
        6. Provides tables for study characteristics and results
        7. Addresses risk of bias and quality assessment
        8. Discusses limitations and future research directions

        # Output Format
        Provide the complete systematic review in markdown format with:
        - Proper headings and subheadings
        - APA-formatted citations throughout
        - Tables and figures as needed
        - Professional academic tone
        - Comprehensive coverage of all aspects

        Begin the systematic review now:
        """
    
    def _validate_review(self, review_content: str) -> Dict[str, Any]:
        """Validate the generated review for quality and compliance."""
        try:
            # Basic metrics
            word_count = len(review_content.split())
            citation_count = review_content.count("(") + review_content.count("[")
            
            # Section checks
            required_sections = ["Abstract", "Introduction", "Methods", "Results", "Discussion"]
            sections_present = {
                section: f"# {section}" in review_content or f"## {section}" in review_content
                for section in required_sections
            }
            
            # PRISMA elements check
            prisma_elements = [
                "PRISMA", "systematic review", "meta-analysis", "search strategy",
                "inclusion criteria", "exclusion criteria", "risk of bias"
            ]
            prisma_compliance = {
                element: element.lower() in review_content.lower()
                for element in prisma_elements
            }
            
            return {
                "word_count": word_count,
                "citation_count": citation_count,
                "sections_present": sections_present,
                "prisma_compliance": prisma_compliance,
                "validation_score": (
                    sum(sections_present.values()) / len(sections_present) +
                    sum(prisma_compliance.values()) / len(prisma_compliance)
                ) / 2
            }
            
        except Exception as e:
            logger.error(f"Error validating review: {e}")
            return {"error": str(e), "validation_score": 0.0}
    
    def _check_prisma_compliance(self, review_content: str) -> Dict[str, Any]:
        """Check PRISMA 2020 compliance in detail."""
        try:
            # PRISMA 2020 checklist items
            prisma_checklist = {
                "title": "systematic review" in review_content.lower(),
                "abstract": "abstract" in review_content.lower(),
                "introduction": "introduction" in review_content.lower(),
                "methods": "methods" in review_content.lower(),
                "results": "results" in review_content.lower(),
                "discussion": "discussion" in review_content.lower(),
                "search_strategy": "search strategy" in review_content.lower(),
                "selection_criteria": "inclusion criteria" in review_content.lower(),
                "data_extraction": "data extraction" in review_content.lower(),
                "risk_of_bias": "risk of bias" in review_content.lower(),
                "synthesis": "synthesis" in review_content.lower(),
                "limitations": "limitations" in review_content.lower(),
                "conclusions": "conclusions" in review_content.lower(),
                "funding": "funding" in review_content.lower() or "financial" in review_content.lower()
            }
            
            compliance_score = sum(prisma_checklist.values()) / len(prisma_checklist)
            
            return {
                "checklist": prisma_checklist,
                "compliance_score": compliance_score,
                "missing_elements": [k for k, v in prisma_checklist.items() if not v]
            }
            
        except Exception as e:
            logger.error(f"Error checking PRISMA compliance: {e}")
            return {"error": str(e), "compliance_score": 0.0}


class PRISMAAgentSystem:
    """
    Main PRISMA agent system orchestrator.
    
    Manages the complete systematic review workflow using OpenAI Agents SDK.
    """
    
    def __init__(self, orchestrator: Optional[AgentOrchestrator] = None):
        """
        Initialize the PRISMA agent system.
        
        Args:
            orchestrator: Optional agent orchestrator (creates default if None)
        """
        self.orchestrator = orchestrator or AgentOrchestrator()
        self.tools = PRISMAAgentTools()
        
        # Store agents for handoffs
        self._planner_agent: Optional[Agent] = None
        self._searcher_agent: Optional[Agent] = None
        self._reviewer_agent: Optional[Agent] = None
        self._writer_agent: Optional[Agent] = None
        self._validator_agent: Optional[Agent] = None
    
    def transfer_to_searcher(self) -> Agent:
        """Transfer to the literature searcher agent."""
        if not self._searcher_agent:
            self._searcher_agent = self.create_searcher_agent()
        return self._searcher_agent
    
    def transfer_to_reviewer(self) -> Agent:
        """Transfer to the study reviewer agent."""
        if not self._reviewer_agent:
            self._reviewer_agent = self.create_reviewer_agent()
        return self._reviewer_agent
    
    def transfer_to_writer(self) -> Agent:
        """Transfer to the review writer agent."""
        if not self._writer_agent:
            self._writer_agent = self.create_writer_agent()
        return self._writer_agent
    
    def transfer_to_validator(self) -> Agent:
        """Transfer to the validation agent."""
        if not self._validator_agent:
            self._validator_agent = self.create_validator_agent()
        return self._validator_agent
    
    def transfer_to_planner(self) -> Agent:
        """Transfer back to the planner agent."""
        if not self._planner_agent:
            self._planner_agent = self.create_planner_agent()
        return self._planner_agent
    
    def create_planner_agent(self) -> Agent:
        """Create the PRISMA planning agent."""
        instructions = """
        You are the PRISMA Planning Agent, responsible for orchestrating the entire systematic review process.
        You coordinate with specialized agents to create comprehensive, PRISMA-compliant systematic reviews.

        WORKFLOW PHASES:
        1. Planning: Initialize workflow with research question and criteria
        2. Literature Search: Coordinate comprehensive search across multiple sources
        3. Screening: Review and filter studies based on inclusion/exclusion criteria
        4. Data Extraction: Extract and analyze relevant data from included studies
        5. Writing: Generate the complete systematic review document
        6. Validation: Ensure PRISMA compliance and quality standards

        CORE RESPONSIBILITIES:
        - Initialize systematic review workflows
        - Coordinate between specialized agents
        - Monitor progress and quality at each phase
        - Ensure PRISMA 2020 compliance throughout
        - Manage handoffs between agents

        TOOLS AVAILABLE:
        - initialize_workflow: Start new systematic review project
        - Agent handoff tools for specialized tasks

        Always maintain scientific rigor and ensure the final output meets all PRISMA requirements:
        - 8,000-10,000 words
        - ≥50 peer-reviewed citations
        - Complete PRISMA sections and compliance
        """
        
        tools = [
            self.tools.initialize_workflow,
            self.transfer_to_searcher,
            self.transfer_to_reviewer,
            self.transfer_to_writer,
            self.transfer_to_validator,
        ]
        
        return Agent(
            name="PRISMA Planning Agent",
            instructions=instructions,
            tools=tools
        )
    
    def create_searcher_agent(self) -> Agent:
        """Create the literature searcher agent."""
        instructions = """
        You are the Literature Searcher Agent, specialized in conducting comprehensive systematic literature searches.
        You use multiple AI models and databases to find relevant studies for systematic reviews.

        SEARCH CAPABILITIES:
        - Perplexity deep research for comprehensive literature search
        - Flowise chatflow integration for specialized databases
        - Multi-source search strategy implementation
        - Citation and reference management

        CORE RESPONSIBILITIES:
        - Conduct systematic literature searches across multiple databases
        - Implement comprehensive search strategies
        - Identify relevant peer-reviewed studies
        - Document search process for PRISMA compliance
        - Prepare search results for screening phase

        TOOLS AVAILABLE:
        - conduct_systematic_search: Perform comprehensive literature search
        - Agent handoff tools for next phase

        Always ensure comprehensive coverage and proper documentation of search methodology.
        """
        
        tools = [
            self.tools.conduct_systematic_search,
            self.transfer_to_reviewer,
            self.transfer_to_planner,
        ]
        
        return Agent(
            name="Literature Searcher Agent",
            instructions=instructions,
            tools=tools
        )
    
    def create_reviewer_agent(self) -> Agent:
        """Create the study reviewer agent."""
        instructions = """
        You are the Study Reviewer Agent, specialized in screening, filtering, and quality assessment of studies.
        You use advanced reasoning models to evaluate study quality and relevance.

        REVIEW CAPABILITIES:
        - Perplexity-based study screening and filtering
        - Grok-powered critical analysis and bias detection
        - Quality assessment using established standards
        - Risk of bias evaluation

        CORE RESPONSIBILITIES:
        - Screen studies based on inclusion/exclusion criteria
        - Assess study quality and methodology
        - Detect potential biases and limitations
        - Prepare data for extraction and analysis
        - Document review process for PRISMA compliance

        TOOLS AVAILABLE:
        - screen_and_filter_studies: Screen studies for inclusion
        - extract_and_analyze_data: Extract and analyze study data
        - Agent handoff tools for next phase

        Always maintain rigorous scientific standards and thorough documentation.
        """
        
        tools = [
            self.tools.screen_and_filter_studies,
            self.tools.extract_and_analyze_data,
            self.transfer_to_writer,
            self.transfer_to_planner,
        ]
        
        return Agent(
            name="Study Reviewer Agent",
            instructions=instructions,
            tools=tools
        )
    
    def create_writer_agent(self) -> Agent:
        """Create the review writer agent."""
        instructions = """
        You are the Review Writer Agent, specialized in generating comprehensive PRISMA-compliant systematic reviews.
        You synthesize all research findings into a complete, publication-ready document.

        WRITING CAPABILITIES:
        - O3 high reasoning for comprehensive synthesis
        - PRISMA 2020 guideline compliance
        - Academic writing with proper citations
        - Structured document generation

        CORE RESPONSIBILITIES:
        - Generate complete systematic review documents
        - Ensure PRISMA 2020 compliance
        - Synthesize findings from all research phases
        - Create properly formatted academic text
        - Include all required sections and elements

        REQUIREMENTS:
        - 8,000-10,000 words
        - ≥50 peer-reviewed citations in APA format
        - Complete PRISMA sections (Abstract, Introduction, Methods, Results, Discussion)
        - Professional academic tone

        TOOLS AVAILABLE:
        - generate_systematic_review: Create complete systematic review
        - Agent handoff tools for validation

        Always ensure scientific accuracy and comprehensive coverage.
        """
        
        tools = [
            self.tools.generate_systematic_review,
            self.transfer_to_validator,
            self.transfer_to_planner,
        ]
        
        return Agent(
            name="Review Writer Agent",
            instructions=instructions,
            tools=tools
        )
    
    def create_validator_agent(self) -> Agent:
        """Create the validation agent."""
        instructions = """
        You are the Validation Agent, specialized in ensuring PRISMA compliance and quality standards.
        You perform final quality checks and validation of systematic reviews.

        VALIDATION CAPABILITIES:
        - Grok-powered critical analysis and review
        - PRISMA 2020 compliance checking
        - Quality assessment and recommendations
        - Final document validation

        CORE RESPONSIBILITIES:
        - Validate PRISMA compliance
        - Check word count and citation requirements
        - Assess overall quality and completeness
        - Provide recommendations for improvements
        - Finalize systematic review documents

        QUALITY STANDARDS:
        - PRISMA 2020 compliance (≥80% checklist completion)
        - 8,000-10,000 word count
        - ≥50 peer-reviewed citations
        - Complete sections and proper formatting

        TOOLS AVAILABLE:
        - validate_and_finalize_review: Perform final validation
        - Agent handoff tools if revisions needed

        Always maintain highest standards for systematic review quality.
        """
        
        tools = [
            self.tools.validate_and_finalize_review,
            self.transfer_to_writer,
            self.transfer_to_planner,
        ]
        
        return Agent(
            name="Validation Agent",
            instructions=instructions,
            tools=tools
        )


def create_prisma_agent_system() -> Dict[str, Agent]:
    """
    Create the complete PRISMA agent system.
    
    Returns:
        Dictionary mapping agent names to agent instances
    """
    system = PRISMAAgentSystem()
    
    agents = {
        "planner": system.create_planner_agent(),
        "searcher": system.create_searcher_agent(),
        "reviewer": system.create_reviewer_agent(),
        "writer": system.create_writer_agent(),
        "validator": system.create_validator_agent(),
    }
    
    return agents 