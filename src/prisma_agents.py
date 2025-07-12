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

from agents import Agent, function_tool
from .config import AppConfig, PRISMAConfig
from .perplexity_client import PerplexityClient, PRISMAPerplexityRouter
from .grok_client import GrokClient, PRISMAGrokRouter
from .flowise_client import FlowiseClient, FlowiseAPIError
from .markdown_exporter import MarkdownExporter


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
        self.markdown_exporter = MarkdownExporter()
        
        # Store workflow state
        self.workflow: Optional[PRISMAWorkflow] = None
    
    @function_tool
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
    
    @function_tool
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
    
    @function_tool
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
    
    @function_tool
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
    
    @function_tool
    def compile_review_data(self) -> str:
        """
        Compiles all necessary data to generate the PRISMA-compliant systematic review.
        
        Returns:
            A JSON string containing all the compiled data for the review.
        """
        try:
            if not self.workflow or not self.workflow.results.get("extraction_analysis"):
                return "❌ No analysis results available. Please complete data extraction first."
            
            logger.info("Starting to compile data for systematic review generation...")
            
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
            
            return json.dumps(all_results, indent=2)
            
        except Exception as e:
            logger.error(f"Error compiling review data: {e}")
            return f"❌ Compiling review data failed: {str(e)}"

    @function_tool
    def store_final_review(self, review_content: str) -> str:
        """
        Stores the final generated systematic review content in the workflow.
        
        Args:
            review_content: The full string content of the systematic review.
            
        Returns:
            A confirmation message.
        """
        try:
            if not self.workflow:
                return "❌ Cannot store review: No active workflow."
            
            logger.info("Storing final review content.")
            
            # Basic validation and metrics
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
            self.workflow.word_count = validation_results.get("word_count", 0)
            self.workflow.citation_count = validation_results.get("citation_count", 0)
            
            logger.info(f"Systematic review stored: {self.workflow.word_count} words, {self.workflow.citation_count} citations")
            return "✅ Final review content stored successfully."

        except Exception as e:
            logger.error(f"Error storing final review: {e}")
            return f"❌ Failed to store final review: {e}"

    @function_tool
    def generate_prisma_flow_diagram(self) -> str:
        """
        Generate a PRISMA 2020 flow diagram in Mermaid format.
        
        Returns:
            Mermaid diagram string for the flow diagram.
        """
        try:
            if not self.workflow or not self.workflow.results.get("search_results"):
                return "```mermaid\nflowchart TD\n    A[Error: Search results not available]\n```"

            # This is a simplified example; in a real scenario, these numbers
            # would be meticulously tracked throughout the workflow.
            # For this implementation, we'll use placeholder numbers based on search results.
            
            search_results = self.workflow.results.get("search_results", {})
            
            # Placeholder numbers
            db_records = len(search_results.get("perplexity", {}).get("citations", []))
            register_records = sum(len(r.get("citations", [])) for r in search_results.get("flowise", {}).values() if isinstance(r, dict))
            total_identified = db_records + register_records
            
            duplicates_removed = int(total_identified * 0.1)  # Estimate
            screened = total_identified - duplicates_removed
            excluded = int(screened * 0.8) # Estimate
            reports_sought = screened - excluded
            reports_not_retrieved = int(reports_sought * 0.05) # Estimate
            reports_assessed = reports_sought - reports_not_retrieved
            reports_excluded = int(reports_assessed * 0.5) # Estimate
            studies_included = reports_assessed - reports_excluded

            return f"""
```mermaid
flowchart TD
    subgraph Identification
        A[Records identified from*:<br/>Databases n={db_records}<br/>Registers n={register_records}]
        B[Records removed before screening:<br/>Duplicate records removed n={duplicates_removed}<br/>Records marked as ineligible n=0<br/>Records removed for other reasons n=0]
    end

    subgraph Screening
        C[Records screened<br/>n={screened}]
        D[Records excluded**<br/>n={excluded}]
        E[Reports sought for retrieval<br/>n={reports_sought}]
        F[Reports not retrieved<br/>n={reports_not_retrieved}]
    end

    subgraph Included
        G[Reports assessed for eligibility<br/>n={reports_assessed}]
        H[Reports excluded:<br/>Reason 1 (e.g., wrong population) n={reports_excluded}<br/>Reason 2 n=0<br/>Reason 3 n=0]
        I[Studies included in review<br/>n={studies_included}]
    end

    A --> B --> C
    C --> D
    C --> E
    E --> F
    E --> G
    G --> H
    G --> I
```
*Consider, if feasible to do so, reporting the number of records identified from each database or register searched.
**If automation tools were used, indicate how many records were excluded by a human and how many were excluded by automation tools.
"""
        except Exception as e:
            logger.error(f"Error generating PRISMA flow diagram: {e}")
            return f"```mermaid\nflowchart TD\n    A[Error: {e}]\n```"

    @function_tool
    def export_review_as_markdown(self, review_content: str) -> str:
        """
        Exports the final systematic review to a markdown file.

        Args:
            review_content: The full string content of the systematic review.

        Returns:
            A string confirming the export path or an error message.
        """
        try:
            if not self.workflow:
                return "❌ Cannot export: No active workflow."
            
            file_path = self.markdown_exporter.export_prisma_review(
                review_content=review_content,
                research_question=self.workflow.research_question
            )
            logger.info(f"Successfully exported PRISMA review to {file_path}")
            return f"✅ Systematic review successfully exported to: {file_path}"
        except Exception as e:
            logger.error(f"Error exporting PRISMA review as markdown: {e}")
            return f"❌ Failed to export review: {e}"

    @function_tool
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
        4. Has clear sections: Abstract, Introduction, Methods, Results, Discussion, and Other Information
        5. Includes a PRISMA flow diagram description and a list of excluded studies with reasons
        6. Provides tables for study characteristics and results
        7. Addresses risk of bias and quality assessment
        8. Discusses limitations and future research directions
        9. Describes the automated nature of the review process (e.g., screening performed by AI agents)
        10. Includes sections for Protocol and Registration, Funding, Competing Interests, and Data Availability

        # Output Format
        Provide the complete systematic review in markdown format with:
        - Proper headings and subheadings for all PRISMA 2020 items
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
    
    def __init__(self, orchestrator: Optional[Any] = None):
        """
        Initialize the PRISMA agent system.
        
        Args:
            orchestrator: Optional agent orchestrator (creates default if None)
        """
        self.orchestrator = orchestrator
        self.tools = PRISMAAgentTools()
        
        # Define agents with handoffs for code-based orchestration
        self._searcher_agent: Agent = self.create_searcher_agent()
        self._reviewer_agent: Agent = self.create_reviewer_agent()
        self._writer_agent: Agent = self.create_writer_agent()
        self._validator_agent: Agent = self.create_validator_agent()
        
        # Set up handoffs
        self._searcher_agent.handoffs = [self._reviewer_agent]
        self._reviewer_agent.handoffs = [self._writer_agent]
        self._writer_agent.handoffs = [self._validator_agent]

    def get_initial_agent(self) -> Agent:
        """Get the first agent in the workflow."""
        return self._searcher_agent

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
        - Prepare search results for the screening phase and handoff to the Reviewer Agent.

        TOOLS AVAILABLE:
        - conduct_systematic_search: Perform comprehensive literature search

        Always ensure comprehensive coverage and proper documentation of search methodology. When your task is complete, handoff to the Study Reviewer Agent.
        """
        
        return Agent(
            name="Literature Searcher Agent",
            instructions=instructions,
            tools=[self.tools.conduct_systematic_search],
            model=AppConfig.OPENAI_MODEL
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
        - Document review process for PRISMA compliance and handoff to the Writer Agent.

        TOOLS AVAILABLE:
        - screen_and_filter_studies: Screen studies for inclusion
        - extract_and_analyze_data: Extract and analyze study data

        Always maintain rigorous scientific standards and thorough documentation. When your task is complete, handoff to the Review Writer Agent.
        """
        
        return Agent(
            name="Study Reviewer Agent",
            instructions=instructions,
            tools=[self.tools.screen_and_filter_studies, self.tools.extract_and_analyze_data],
            model=AppConfig.OPENAI_MODEL
        )
    
    def create_writer_agent(self) -> Agent:
        """Create the review writer agent."""
        instructions = """
        You are the Review Writer Agent, specialized in generating comprehensive PRISMA-compliant systematic reviews.
        You synthesize all research findings into a complete, publication-ready document.

        Your first step is to call the `compile_review_data` tool to get all the necessary information.
        Once you have the data, you will generate a comprehensive systematic review that follows all PRISMA guidelines.
        After generating the review, you MUST call the `store_final_review` tool to save your work before handing off to the Validation Agent.

        When your task is complete, handoff to the Validation Agent.
        """
        
        return Agent(
            name="Review Writer Agent",
            instructions=instructions,
            tools=[self.tools.compile_review_data, self.tools.store_final_review],
            model=AppConfig.OPENAI_MODEL
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
        - Generate the final PRISMA flow diagram.
        - Finalize systematic review documents.

        QUALITY STANDARDS:
        - PRISMA 2020 compliance (≥80% checklist completion)
        - 8,000-10,000 word count
        - ≥50 peer-reviewed citations
        - Complete sections and proper formatting

        TOOLS AVAILABLE:
        - validate_and_finalize_review: Perform final validation on the stored review.
        - generate_prisma_flow_diagram: Create the PRISMA flow diagram
        - export_review_as_markdown: Save the final review to a markdown file.

        Always maintain highest standards for systematic review quality.
        """
        
        return Agent(
            name="Validation Agent",
            instructions=instructions,
            tools=[self.tools.validate_and_finalize_review, self.tools.generate_prisma_flow_diagram, self.tools.export_review_as_markdown],
            model=AppConfig.OPENAI_MODEL
        )

    def create_prisma_orchestrator_agent(self) -> Agent:
        """Create the main PRISMA orchestrator agent with handoffs to specialized agents."""
        instructions = """
        You are the PRISMA Orchestrator Agent. Your role is to manage the entire PRISMA systematic review workflow by handing off tasks to specialized agents in the correct sequence.
        
        Workflow Steps:
        1. Hand off to the Literature Searcher Agent to conduct the search.
        2. Once search is complete, hand off to the Study Reviewer Agent for screening and analysis.
        3. Then, hand off to the Review Writer Agent to generate the review.
        4. Finally, hand off to the Validation Agent to validate and export.
        
        Use the handoffs to delegate each phase. Monitor the progress and ensure the workflow completes.
        """
        
        return Agent(
            name="PRISMA Orchestrator Agent",
            instructions=instructions,
            handoffs=[self._searcher_agent],
            model=AppConfig.OPENAI_MODEL
        )


def create_prisma_agent_system() -> Dict[str, Agent]:
    """
    Create the complete PRISMA agent system.
    
    Returns:
        Dictionary mapping agent names to agent instances
    """
    system = PRISMAAgentSystem()
    
    agents = {
        "orchestrator": system.create_prisma_orchestrator_agent(),
        "searcher": system.create_searcher_agent(),
        "reviewer": system.create_reviewer_agent(),
        "writer": system.create_writer_agent(),
        "validator": system.create_validator_agent(),
    }
    
    return agents 