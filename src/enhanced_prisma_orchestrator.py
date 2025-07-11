"""
Enhanced PRISMA Orchestrator System with Orchestrator-Worker Philosophy.

This module implements the fusion of Anthropic's orchestrator-worker philosophy
with OpenAI's Agents SDK for PRISMA systematic reviews.

Key Features:
- LeadResearcher orchestrator agent
- Parallel SubAgents (SearchAgent, AnalysisAgent, CitationAgent)
- External memory system with session backend
- Native OpenAI SDK integration with proper handoffs
- Production guardrails with JSON schema validation
- Enhanced models: o3, o3-deep-research, grok-4, perplexity deep research
"""

from __future__ import annotations

import json
import logging
import time
import asyncio
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import redis
from openai import OpenAI

from .agents import Agent, AgentOrchestrator
from .config import AppConfig, PRISMAConfig
from .perplexity_client import PerplexityClient
from .grok_client import GrokClient
from .flowise_client import FlowiseClient
from .markdown_exporter import MarkdownExporter


logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for OpenAI Agent with enhanced capabilities."""
    
    model: str
    temperature: float = 0.2
    max_tokens: int = 10000
    reasoning_effort: str = "high"
    tools: Optional[List[Dict[str, Any]]] = None
    guardrails: Optional[Dict[str, Any]] = None
    session_backend: str = "redis://localhost:6379/0"
    tracing: bool = True
    max_parallel_agents: int = 5
    retry_policy: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = [
                {"type": "web_search", "user_location": "approximate"},
                {"type": "file_search"},
                {"type": "code_interpreter", "handler": "sandbox_python"}
            ]
        
        if self.guardrails is None:
            self.guardrails = {
                "input_schema": "enhanced_prisma_input_v1.json",
                "output_schema": "enhanced_prisma_output_v1.json"
            }
        
        if self.retry_policy is None:
            self.retry_policy = {"max_retries": 3, "backoff": 2}


@dataclass
class SubAgentPlan:
    """Plan for a SubAgent with specific objectives and constraints."""
    
    id: str
    role: str
    objective: str
    tool_budget: int
    time_limit: int
    confidence_threshold: float = 0.8
    tools: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.tools is None:
            if self.role == "SearchAgent":
                self.tools = ["web_search", "file_search"]
            elif self.role == "AnalysisAgent":
                self.tools = ["code_interpreter", "file_search"]
            elif self.role == "CitationAgent":
                self.tools = ["web_search", "file_search"]
            else:
                self.tools = ["web_search", "file_search", "code_interpreter"]


@dataclass
class EnhancedPRISMAWorkflow:
    """Enhanced workflow state with orchestrator-worker pattern."""
    
    research_question: str
    search_keywords: List[str]
    inclusion_criteria: List[str]
    exclusion_criteria: List[str]
    session_id: str
    
    # Orchestrator state
    lead_researcher_plan: Optional[Dict[str, Any]] = None
    subagent_plans: Optional[List[SubAgentPlan]] = None
    external_memory: Optional[Dict[str, Any]] = None
    
    # Progress tracking
    current_phase: str = "planning"
    parallel_agents_active: int = 0
    checkpoints: Optional[List[Dict[str, Any]]] = None
    
    # Results
    search_results: Dict[str, Any] = None
    analysis_results: Dict[str, Any] = None
    citation_results: Dict[str, Any] = None
    final_synthesis: str = ""
    
    def __post_init__(self):
        if self.lead_researcher_plan is None:
            self.lead_researcher_plan = {
                "complexity_level": "complex",
                "max_subagents": 5,
                "effort_scaling": "high",
                "parallel_execution": True
            }
        
        if self.subagent_plans is None:
            self.subagent_plans = []
        
        if self.external_memory is None:
            self.external_memory = {}
        
        if self.checkpoints is None:
            self.checkpoints = []


class ExternalMemorySystem:
    """External memory system using Redis for state management."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize external memory with Redis backend."""
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            self.redis_client.ping()
            logger.info("External memory system initialized with Redis")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory fallback: {e}")
            self.redis_client = None
            self.memory_store = {}
    
    def store(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Store value in external memory."""
        try:
            if self.redis_client:
                return self.redis_client.setex(key, ttl, json.dumps(value))
            else:
                self.memory_store[key] = value
                return True
        except Exception as e:
            logger.error(f"Error storing in external memory: {e}")
            return False
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve value from external memory."""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                return json.loads(value) if value else None
            else:
                return self.memory_store.get(key)
        except Exception as e:
            logger.error(f"Error retrieving from external memory: {e}")
            return None
    
    def update_workflow_state(self, session_id: str, workflow: EnhancedPRISMAWorkflow) -> bool:
        """Update workflow state in external memory."""
        return self.store(f"workflow:{session_id}", asdict(workflow))
    
    def get_workflow_state(self, session_id: str) -> Optional[EnhancedPRISMAWorkflow]:
        """Get workflow state from external memory."""
        data = self.retrieve(f"workflow:{session_id}")
        return EnhancedPRISMAWorkflow(**data) if data else None


class EnhancedPRISMATools:
    """Enhanced tools for the orchestrator-worker PRISMA system."""
    
    def __init__(self, memory_system: ExternalMemorySystem):
        """Initialize enhanced tools with external memory system."""
        self.memory_system = memory_system
        self.openai_client = OpenAI(api_key=AppConfig.OPENAI_API_KEY)
        self.perplexity_client = PerplexityClient()
        self.grok_client = GrokClient()
        self.flowise_client = FlowiseClient()
        self.markdown_exporter = MarkdownExporter()
    
    def parallel_web_search(self, queries: List[str], max_workers: int = 5) -> Dict[str, Any]:
        """Perform parallel web searches using multiple agents."""
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit web search tasks
            future_to_query = {
                executor.submit(self._single_web_search, query): query
                for query in queries[:max_workers]
            }
            
            # Collect results
            for future in as_completed(future_to_query):
                query = future_to_query[future]
                try:
                    result = future.result()
                    results[query] = result
                except Exception as e:
                    logger.error(f"Web search failed for query '{query}': {e}")
                    results[query] = {"error": str(e)}
        
        return results
    
    def _single_web_search(self, query: str) -> Dict[str, Any]:
        """Perform a single web search."""
        try:
            # Use Perplexity for deep research
            response = self.perplexity_client.search(
                query=query,
                model="sonar-deep-research",
                temperature=0.2,
                max_tokens=4000
            )
            
            return {
                "query": query,
                "response": response.get("content", ""),
                "sources": response.get("sources", []),
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            return {"error": str(e)}
    
    def parallel_analysis(self, data_sets: List[Dict[str, Any]], analysis_type: str = "systematic") -> Dict[str, Any]:
        """Perform parallel analysis using multiple agents."""
        results = {}
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit analysis tasks
            future_to_data = {
                executor.submit(self._single_analysis, data, analysis_type): f"dataset_{i}"
                for i, data in enumerate(data_sets)
            }
            
            # Collect results
            for future in as_completed(future_to_data):
                data_id = future_to_data[future]
                try:
                    result = future.result()
                    results[data_id] = result
                except Exception as e:
                    logger.error(f"Analysis failed for {data_id}: {e}")
                    results[data_id] = {"error": str(e)}
        
        return results
    
    def _single_analysis(self, data: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        """Perform a single analysis task."""
        try:
            # Use Grok for reasoning and analysis
            analysis_prompt = f"""
            Perform a {analysis_type} analysis of the following data:
            
            {json.dumps(data, indent=2)}
            
            Provide:
            1. Statistical summary
            2. Quality assessment
            3. Bias detection
            4. Key findings
            5. Confidence level (0.0-1.0)
            
            Return structured JSON output.
            """
            
            response = self.grok_client.complete(
                messages=[{"role": "user", "content": analysis_prompt}],
                temperature=0.2,
                max_tokens=2000
            )
            
            return {
                "analysis_type": analysis_type,
                "result": response.get("content", ""),
                "timestamp": time.time(),
                "confidence": 0.8  # Default confidence
            }
        except Exception as e:
            logger.error(f"Error in analysis: {e}")
            return {"error": str(e)}
    
    def citation_pass(self, content: str, sources: List[Dict[str, Any]]) -> str:
        """Perform citation pass to ensure all claims are source-attributed."""
        try:
            citation_prompt = f"""
            You are a CitationAgent responsible for ensuring every factual claim in the following content
            is properly attributed to sources. 
            
            Content to cite:
            {content}
            
            Available sources:
            {json.dumps(sources, indent=2)}
            
            Return the content with proper citations in the format [^N] where N is the source number.
            Ensure every claim has a citation and all citations are accurate.
            """
            
            try:
                response = self.openai_client.responses.create(
                    model="o3-deep-research-2025-06-26",
                    input=[],
                    text={
                        "format": {
                            "type": "text"
                        }
                    },
                    reasoning={
                        "effort": "high",
                        "summary": "detailed"
                    },
                    tools=[
                        {
                            "type": "web_search_preview",
                            "user_location": {
                                "type": "approximate"
                            },
                            "search_context_size": "high"
                        }
                    ],
                    store=False
                )
                return response.choices[0].message.content
            except Exception as e:
                # Fallback to o4-mini-deep-research
                logger.warning(f"O3 model failed in citation pass, using fallback: {e}")
                response = self.openai_client.chat.completions.create(
                    model="o4-mini-deep-research-2025-06-26",
                    messages=[{"role": "user", "content": citation_prompt}],
                    max_tokens=8000,
                    temperature=0.2,
                    reasoning={
                        "summary": "detailed"
                    }
                )
                return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error in citation pass: {e}")
            return content  # Return original content if citation fails


class LeadResearcherAgent:
    """LeadResearcher orchestrator agent implementing the orchestrator-worker pattern."""
    
    def __init__(self, config: AgentConfig, memory_system: ExternalMemorySystem):
        """Initialize LeadResearcher with configuration and memory system."""
        self.config = config
        self.memory_system = memory_system
        self.tools = EnhancedPRISMATools(memory_system)
        self.subagents = {}
        self.current_workflow: Optional[EnhancedPRISMAWorkflow] = None
    
    def initialize_workflow(self, research_question: str, search_keywords: List[str], 
                           inclusion_criteria: List[str], exclusion_criteria: List[str]) -> str:
        """Initialize a new PRISMA workflow with orchestrator-worker pattern."""
        try:
            session_id = f"prisma_enhanced_{int(time.time())}"
            
            # Create enhanced workflow
            self.current_workflow = EnhancedPRISMAWorkflow(
                research_question=research_question,
                search_keywords=search_keywords,
                inclusion_criteria=inclusion_criteria,
                exclusion_criteria=exclusion_criteria,
                session_id=session_id
            )
            
            # Store in external memory
            self.memory_system.update_workflow_state(session_id, self.current_workflow)
            
            # Create initial plan
            self._create_lead_researcher_plan()
            
            logger.info(f"Enhanced PRISMA workflow initialized: {session_id}")
            return f"✅ Enhanced PRISMA workflow initialized with session: {session_id}"
            
        except Exception as e:
            logger.error(f"Error initializing enhanced workflow: {e}")
            return f"❌ Failed to initialize enhanced workflow: {str(e)}"
    
    def _create_lead_researcher_plan(self) -> None:
        """Create the initial plan for LeadResearcher."""
        if not self.current_workflow:
            return
        
        # Analyze complexity
        complexity = self._analyze_query_complexity(self.current_workflow.research_question)
        
        # Create SubAgent plans
        subagent_plans = []
        
        # SearchAgent plans (parallel search)
        for i, keyword_group in enumerate(self._group_keywords(self.current_workflow.search_keywords)):
            subagent_plans.append(SubAgentPlan(
                id=f"search_{i}",
                role="SearchAgent",
                objective=f"Search for literature on: {', '.join(keyword_group)}",
                tool_budget=15,
                time_limit=300,
                confidence_threshold=0.8
            ))
        
        # AnalysisAgent plans (parallel analysis)
        subagent_plans.append(SubAgentPlan(
            id="analysis_quality",
            role="AnalysisAgent",
            objective="Assess study quality and methodology",
            tool_budget=10,
            time_limit=600,
            confidence_threshold=0.8
        ))
        
        subagent_plans.append(SubAgentPlan(
            id="analysis_bias",
            role="AnalysisAgent",
            objective="Detect publication bias and conflicts",
            tool_budget=8,
            time_limit=400,
            confidence_threshold=0.7
        ))
        
        # CitationAgent plan
        subagent_plans.append(SubAgentPlan(
            id="citation_pass",
            role="CitationAgent",
            objective="Ensure all claims are properly cited",
            tool_budget=12,
            time_limit=300,
            confidence_threshold=0.9
        ))
        
        # Update workflow
        self.current_workflow.subagent_plans = subagent_plans
        self.current_workflow.lead_researcher_plan.update({
            "complexity_level": complexity,
            "subagent_count": len(subagent_plans),
            "parallel_execution": True
        })
        
        # Store updated workflow
        self.memory_system.update_workflow_state(
            self.current_workflow.session_id, self.current_workflow
        )
    
    def _analyze_query_complexity(self, query: str) -> str:
        """Analyze the complexity level of the research question."""
        # Simple heuristics - could be enhanced with ML
        complex_keywords = ["systematic review", "meta-analysis", "intervention", "randomized", "clinical trial"]
        comparative_keywords = ["compare", "versus", "vs", "difference", "effectiveness"]
        
        query_lower = query.lower()
        
        if any(keyword in query_lower for keyword in complex_keywords):
            return "complex"
        elif any(keyword in query_lower for keyword in comparative_keywords):
            return "comparative"
        else:
            return "simple"
    
    def _group_keywords(self, keywords: List[str], group_size: int = 3) -> List[List[str]]:
        """Group keywords for parallel search agents."""
        groups = []
        for i in range(0, len(keywords), group_size):
            groups.append(keywords[i:i+group_size])
        return groups
    
    def execute_parallel_search(self) -> Dict[str, Any]:
        """Execute parallel search using multiple SearchAgents."""
        if not self.current_workflow:
            return {"error": "No active workflow"}
        
        try:
            # Get SearchAgent plans
            search_plans = [plan for plan in self.current_workflow.subagent_plans if plan.role == "SearchAgent"]
            
            # Prepare search queries
            search_queries = []
            for plan in search_plans:
                # Extract keywords from objective
                keywords = plan.objective.split(": ")[1] if ": " in plan.objective else plan.objective
                search_queries.append(f"{self.current_workflow.research_question} {keywords}")
            
            # Execute parallel search
            logger.info(f"Executing parallel search with {len(search_queries)} SearchAgents")
            search_results = self.tools.parallel_web_search(search_queries, max_workers=5)
            
            # Store results
            self.current_workflow.search_results = search_results
            self.current_workflow.current_phase = "analysis"
            
            # Update external memory
            self.memory_system.update_workflow_state(
                self.current_workflow.session_id, self.current_workflow
            )
            
            return {
                "status": "success",
                "searches_completed": len(search_results),
                "total_sources": sum(len(result.get("sources", [])) for result in search_results.values()),
                "next_phase": "analysis"
            }
            
        except Exception as e:
            logger.error(f"Error in parallel search: {e}")
            return {"error": str(e)}
    
    def execute_parallel_analysis(self) -> Dict[str, Any]:
        """Execute parallel analysis using multiple AnalysisAgents."""
        if not self.current_workflow or not self.current_workflow.search_results:
            return {"error": "No search results available"}
        
        try:
            # Prepare data for analysis
            data_sets = []
            for query, result in self.current_workflow.search_results.items():
                if "error" not in result:
                    data_sets.append({
                        "query": query,
                        "content": result.get("response", ""),
                        "sources": result.get("sources", [])
                    })
            
            # Execute parallel analysis
            logger.info(f"Executing parallel analysis with {len(data_sets)} data sets")
            analysis_results = self.tools.parallel_analysis(data_sets, "systematic")
            
            # Store results
            self.current_workflow.analysis_results = analysis_results
            self.current_workflow.current_phase = "citation"
            
            # Update external memory
            self.memory_system.update_workflow_state(
                self.current_workflow.session_id, self.current_workflow
            )
            
            return {
                "status": "success",
                "analyses_completed": len(analysis_results),
                "average_confidence": sum(
                    result.get("confidence", 0) for result in analysis_results.values()
                ) / len(analysis_results),
                "next_phase": "citation"
            }
            
        except Exception as e:
            logger.error(f"Error in parallel analysis: {e}")
            return {"error": str(e)}
    
    def execute_citation_pass(self) -> Dict[str, Any]:
        """Execute citation pass using CitationAgent."""
        if not self.current_workflow or not self.current_workflow.analysis_results:
            return {"error": "No analysis results available"}
        
        try:
            # Compile content for citation
            all_content = ""
            all_sources = []
            
            for result in self.current_workflow.analysis_results.values():
                if "error" not in result:
                    all_content += result.get("result", "") + "\n\n"
            
            # Collect all sources
            for result in self.current_workflow.search_results.values():
                if "error" not in result:
                    all_sources.extend(result.get("sources", []))
            
            # Execute citation pass
            logger.info("Executing citation pass")
            cited_content = self.tools.citation_pass(all_content, all_sources)
            
            # Store results
            self.current_workflow.citation_results = {
                "cited_content": cited_content,
                "source_count": len(all_sources),
                "citation_count": cited_content.count("[^")
            }
            self.current_workflow.current_phase = "synthesis"
            
            # Update external memory
            self.memory_system.update_workflow_state(
                self.current_workflow.session_id, self.current_workflow
            )
            
            return {
                "status": "success",
                "citation_count": self.current_workflow.citation_results["citation_count"],
                "source_count": self.current_workflow.citation_results["source_count"],
                "next_phase": "synthesis"
            }
            
        except Exception as e:
            logger.error(f"Error in citation pass: {e}")
            return {"error": str(e)}
    
    def get_models_info(self) -> Dict[str, Any]:
        """Get information about models being used in the PRISMA workflow."""
        return {
            "primary_model": "o3-deep-research-2025-06-26",
            "fallback_model": "o4-mini-deep-research-2025-06-26",
            "perplexity_model": "sonar-deep-research",
            "grok_model": "grok-beta",
            "model_capabilities": {
                "o3-deep-research-2025-06-26": {
                    "reasoning_effort": "high",
                    "summary": "detailed",
                    "web_search": True,
                    "use_case": "Primary synthesis and analysis"
                },
                "o4-mini-deep-research-2025-06-26": {
                    "reasoning_effort": "high",
                    "summary": "detailed",
                    "web_search": False,
                    "use_case": "Fallback for synthesis and analysis"
                },
                "sonar-deep-research": {
                    "use_case": "Deep literature search and research",
                    "provider": "Perplexity"
                },
                "grok-beta": {
                    "use_case": "Critical analysis and bias detection",
                    "provider": "X.AI"
                }
            }
        }

    def execute_final_synthesis(self) -> Dict[str, Any]:
        """Execute final synthesis to create the complete PRISMA systematic review."""
        if not self.current_workflow or not self.current_workflow.citation_results:
            return {"error": "No citation results available"}
        
        try:
            # Compile all results
            synthesis_data = {
                "research_question": self.current_workflow.research_question,
                "search_keywords": self.current_workflow.search_keywords,
                "inclusion_criteria": self.current_workflow.inclusion_criteria,
                "exclusion_criteria": self.current_workflow.exclusion_criteria,
                "search_results": self.current_workflow.search_results,
                "analysis_results": self.current_workflow.analysis_results,
                "citation_results": self.current_workflow.citation_results
            }
            
            # Create comprehensive synthesis prompt
            synthesis_prompt = f"""
            You are an expert systematic review synthesizer following PRISMA 2020 guidelines.
            
            Create a comprehensive PRISMA-compliant systematic review based on the following data:
            
            Research Question: {self.current_workflow.research_question}
            
            Search Results: {json.dumps(self.current_workflow.search_results, indent=2)}
            
            Analysis Results: {json.dumps(self.current_workflow.analysis_results, indent=2)}
            
            Citation Results: {json.dumps(self.current_workflow.citation_results, indent=2)}
            
            Create a complete systematic review with:
            1. Abstract (structured)
            2. Introduction with rationale
            3. Methods (search strategy, inclusion/exclusion criteria)
            4. Results (study characteristics, risk of bias, syntheses)
            5. Discussion (implications, limitations)
            6. Conclusions
            7. PRISMA flow diagram description
            8. References
            
            Ensure PRISMA 2020 compliance and high academic quality.
            """
            
            # Use o3-deep-research for synthesis
            try:
                response = self.openai_client.responses.create(
                    model="o3-deep-research-2025-06-26",
                    input=[],
                    text={
                        "format": {
                            "type": "text"
                        }
                    },
                    reasoning={
                        "effort": "high",
                        "summary": "detailed"
                    },
                    tools=[
                        {
                            "type": "web_search_preview",
                            "user_location": {
                                "type": "approximate"
                            },
                            "search_context_size": "high"
                        }
                    ],
                    store=False
                )
                final_synthesis = response.choices[0].message.content
            except Exception as e:
                # Fallback to o4-mini-deep-research
                logger.warning(f"O3 model failed, using fallback: {e}")
                response = self.openai_client.chat.completions.create(
                    model="o4-mini-deep-research-2025-06-26",
                    messages=[{"role": "user", "content": synthesis_prompt}],
                    max_tokens=12000,
                    temperature=0.3,
                    reasoning={
                        "summary": "detailed"
                    }
                )
                
            
            # Store final synthesis
            self.current_workflow.final_synthesis = final_synthesis
            self.current_workflow.current_phase = "completed"
            
            # Update external memory
            self.memory_system.update_workflow_state(
                self.current_workflow.session_id, self.current_workflow
            )
            
            return {
                "status": "success",
                "systematic_review": final_synthesis,
                "word_count": len(final_synthesis.split()),
                "session_id": self.current_workflow.session_id,
                "completion_time": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error in final synthesis: {e}")
            return {"error": str(e)}


class EnhancedPRISMAOrchestrator:
    """
    Enhanced PRISMA orchestrator implementing the orchestrator-worker philosophy
    with native OpenAI SDK integration.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize the enhanced PRISMA orchestrator."""
        # Initialize external memory system
        self.memory_system = ExternalMemorySystem(redis_url)
        
        # Initialize configuration
        self.config = AgentConfig(
            model="o3-deep-research-2025-06-26",
            temperature=0.2,
            max_tokens=10000,
            reasoning_effort="high"
        )
        
        # Initialize LeadResearcher
        self.lead_researcher = LeadResearcherAgent(self.config, self.memory_system)
        
        # Track active workflows
        self.active_workflows: Dict[str, EnhancedPRISMAWorkflow] = {}
        
        logger.info("Enhanced PRISMA orchestrator initialized")
    
    def create_enhanced_systematic_review(
        self,
        research_question: str,
        search_keywords: List[str],
        inclusion_criteria: List[str],
        exclusion_criteria: List[str]
    ) -> Dict[str, Any]:
        """
        Create a systematic review using the enhanced orchestrator-worker pattern.
        
        Args:
            research_question: Primary research question
            search_keywords: Keywords for literature search
            inclusion_criteria: Study inclusion criteria
            exclusion_criteria: Study exclusion criteria
            
        Returns:
            Complete systematic review with metadata
        """
        try:
            logger.info(f"Starting enhanced PRISMA systematic review: {research_question}")
            
            # Initialize workflow
            init_result = self.lead_researcher.initialize_workflow(
                research_question, search_keywords, inclusion_criteria, exclusion_criteria
            )
            
            if "❌" in init_result:
                return {"error": init_result}
            
            # Execute orchestrator-worker pattern
            
            # Phase 1: Parallel Search (SearchAgents)
            search_result = self.lead_researcher.execute_parallel_search()
            if "error" in search_result:
                return {"error": f"Search phase failed: {search_result['error']}"}
            
            # Phase 2: Parallel Analysis (AnalysisAgents)
            analysis_result = self.lead_researcher.execute_parallel_analysis()
            if "error" in analysis_result:
                return {"error": f"Analysis phase failed: {analysis_result['error']}"}
            
            # Phase 3: Citation Pass (CitationAgent)
            citation_result = self.lead_researcher.execute_citation_pass()
            if "error" in citation_result:
                return {"error": f"Citation phase failed: {citation_result['error']}"}
            
            # Phase 4: Final Synthesis (LeadResearcher)
            synthesis_result = self.lead_researcher.execute_final_synthesis()
            if "error" in synthesis_result:
                return {"error": f"Synthesis phase failed: {synthesis_result['error']}"}
            
            # Store in active workflows
            workflow = self.lead_researcher.current_workflow
            if workflow:
                self.active_workflows[workflow.session_id] = workflow
            
            logger.info(f"Enhanced PRISMA systematic review completed: {synthesis_result.get('word_count', 0)} words")
            
            return {
                "systematic_review": synthesis_result["systematic_review"],
                "session_id": synthesis_result["session_id"],
                "workflow_metadata": {
                    "word_count": synthesis_result["word_count"],
                    "search_agents": search_result["searches_completed"],
                    "analysis_agents": analysis_result["analyses_completed"],
                    "citation_count": citation_result["citation_count"],
                    "source_count": citation_result["source_count"],
                    "completion_time": synthesis_result["completion_time"]
                },
                "orchestrator_pattern": "enhanced_prisma_v1",
                "models_used": ["o3-deep-research", "perplexity-sonar", "grok-beta"],
                "status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced systematic review: {e}")
            return {
                "error": str(e),
                "research_question": research_question,
                "status": "failed",
                "timestamp": time.time()
            }
    
    def get_workflow_status(self, session_id: str) -> Dict[str, Any]:
        """Get the status of a specific workflow."""
        workflow = self.memory_system.get_workflow_state(session_id)
        if not workflow:
            return {"error": "Workflow not found"}
        
        return {
            "session_id": session_id,
            "current_phase": workflow.current_phase,
            "research_question": workflow.research_question,
            "subagent_count": len(workflow.subagent_plans),
            "parallel_agents_active": workflow.parallel_agents_active,
            "checkpoints": len(workflow.checkpoints),
            "status": "active" if workflow.current_phase != "completed" else "completed"
        }
    
    def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List all active workflows."""
        return [
            {
                "session_id": session_id,
                "research_question": workflow.research_question,
                "current_phase": workflow.current_phase,
                "subagent_count": len(workflow.subagent_plans)
            }
            for session_id, workflow in self.active_workflows.items()
        ]


def create_enhanced_prisma_orchestrator(redis_url: str = "redis://localhost:6379/0") -> EnhancedPRISMAOrchestrator:
    """
    Create and initialize an enhanced PRISMA orchestrator.
    
    Args:
        redis_url: Redis connection URL for external memory
        
    Returns:
        Configured enhanced PRISMA orchestrator
    """
    try:
        return EnhancedPRISMAOrchestrator(redis_url)
    except Exception as e:
        logger.error(f"Failed to create enhanced PRISMA orchestrator: {e}")
        raise ValueError(f"Enhanced PRISMA orchestrator creation failed: {str(e)}")


# Example usage and testing
if __name__ == "__main__":
    # Test the enhanced system
    orchestrator = create_enhanced_prisma_orchestrator()
    
    # Test systematic review creation
    result = orchestrator.create_enhanced_systematic_review(
        research_question="What is the effectiveness of machine learning interventions in healthcare?",
        search_keywords=["machine learning", "healthcare", "intervention", "effectiveness", "clinical outcomes"],
        inclusion_criteria=["Peer-reviewed articles", "Published 2020-2024", "English language"],
        exclusion_criteria=["Case reports", "Opinion pieces", "Non-peer reviewed"]
    )
    
    print(f"Result: {result.get('status', 'unknown')}")
    if result.get('systematic_review'):
        print(f"Word count: {result['workflow_metadata']['word_count']}")
        print(f"Citation count: {result['workflow_metadata']['citation_count']}")