"""
Query Optimization Agent System for Scientific Research Alignment.

This module implements the first-stage agent that optimizes all user queries 
to align with scientific research standards, incorporate reputable sources,
and ensure proper citation practices before passing to downstream agents.
"""

from __future__ import annotations

import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from agents import Agent, function_tool
from pydantic import BaseModel

from .config import AppConfig, OpenAIModelsConfig
from .perplexity_client import PerplexityClient
from .openai_enhanced_client import create_enhanced_openai_client


logger = logging.getLogger(__name__)


class OptimizedQuery(BaseModel):
    """Structured output for optimized queries."""
    optimized_query: str
    research_context: str
    key_terms: List[str]
    expected_sources: List[str]
    research_methodology: str
    citation_requirements: str
    
    class Config:
        extra = "forbid"  # Strict schema for OpenAI Agents compatibility


class QueryAnalysis(BaseModel):
    """Analysis of the original query."""
    domain: str
    complexity_level: str
    research_type: str
    requires_current_data: bool
    scientific_rigor_needed: bool
    
    class Config:
        extra = "forbid"  # Strict schema for OpenAI Agents compatibility


@function_tool
def analyze_query_for_research_alignment(user_query: str) -> QueryAnalysis:
    """
    Analyze the user query to determine research requirements and alignment needs.
    
    Args:
        user_query: The original user query to analyze
        
    Returns:
        Detailed analysis of the query's research requirements
    """
    try:
        logger.info(f"Analyzing query for research alignment: {user_query[:100]}")
        
        # Basic domain detection
        medical_keywords = ['medical', 'medicine', 'clinical', 'patient', 'disease', 'treatment', 'therapy', 'diagnosis', 'aeromedical', 'aviation medicine', 'aerospace medicine']
        aviation_keywords = ['aviation', 'aircraft', 'pilot', 'flight', 'aerospace', 'cockpit', 'air traffic']
        research_keywords = ['study', 'research', 'analysis', 'systematic review', 'meta-analysis', 'evidence', 'literature']
        
        query_lower = user_query.lower()
        
        # Determine domain
        domain = "general"
        if any(keyword in query_lower for keyword in medical_keywords):
            domain = "medical"
        elif any(keyword in query_lower for keyword in aviation_keywords):
            domain = "aviation"
        elif any(keyword in query_lower for keyword in research_keywords):
            domain = "research"
            
        # Determine complexity and research type
        complexity_level = "moderate"
        if len(user_query.split()) > 30 or any(word in query_lower for word in ['systematic', 'meta-analysis', 'comprehensive']):
            complexity_level = "high"
        elif len(user_query.split()) < 10:
            complexity_level = "simple"
            
        research_type = "exploratory"
        if any(word in query_lower for word in ['compare', 'effectiveness', 'outcome']):
            research_type = "comparative"
        elif any(word in query_lower for word in ['systematic', 'review', 'evidence']):
            research_type = "systematic_review"
        elif any(word in query_lower for word in ['risk', 'safety', 'assessment']):
            research_type = "risk_assessment"
            
        # Determine data and rigor requirements
        current_data_indicators = ['recent', 'current', 'latest', '2024', '2023', 'new', 'emerging']
        requires_current_data = any(indicator in query_lower for indicator in current_data_indicators)
        
        scientific_rigor_needed = domain in ["medical", "aviation"] or research_type in ["systematic_review", "risk_assessment"]
        
        analysis = QueryAnalysis(
            domain=domain,
            complexity_level=complexity_level,
            research_type=research_type,
            requires_current_data=requires_current_data,
            scientific_rigor_needed=scientific_rigor_needed
        )
        
        logger.info(f"Query analysis completed: {analysis}")
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing query: {e}")
        # Return default analysis
        return QueryAnalysis(
            domain="general",
            complexity_level="moderate", 
            research_type="exploratory",
            requires_current_data=False,
            scientific_rigor_needed=True
        )


@function_tool
def gather_research_context_and_sources(query: str, analysis_domain: str, analysis_requires_current_data: bool, analysis_scientific_rigor_needed: bool) -> str:
    """
    Gather research context and identify reputable sources using Perplexity.
    
    Args:
        query: The user query
        analysis_domain: Domain from analysis (medical, aviation, research, general)
        analysis_requires_current_data: Whether current data is needed
        analysis_scientific_rigor_needed: Whether scientific rigor is needed
        
    Returns:
        JSON string containing research context and sources
    """
    try:
        logger.info("Gathering research context and sources")
        
        import json
        
        # Create research-focused query for Perplexity
        research_query = f"""
        Provide current scientific research context for: {query}
        
        Domain: {analysis_domain}
        Current data needed: {analysis_requires_current_data}
        Scientific rigor needed: {analysis_scientific_rigor_needed}
        
        Please include:
        1. Key recent studies and publications (with specific citations)
        2. Current research consensus and gaps
        3. Reputable organizations and institutions in this field
        4. Methodological considerations
        5. Data quality standards
        
        Focus on peer-reviewed sources, systematic reviews, and authoritative medical/scientific organizations.
        """
        
        if AppConfig.PPLX_API_KEY:
            try:
                perplexity_client = PerplexityClient()
                context_response = perplexity_client.query(research_query)
                
                # Extract citations and sources from Perplexity response
                citations = extract_citations_from_text(context_response)
                reputable_sources = identify_reputable_sources(context_response)
                
                result = {
                    "research_context": context_response,
                    "identified_citations": citations,
                    "reputable_sources": reputable_sources,
                    "data_source": "perplexity_live"
                }
                return json.dumps(result)
                
            except Exception as e:
                logger.warning(f"Perplexity query failed: {e}")
                
        # Fallback: Generate research context using OpenAI
        fallback_context = generate_research_context_fallback_simple(query, analysis_domain)
        return json.dumps(fallback_context)
        
    except Exception as e:
        import json
        logger.error(f"Error gathering research context: {e}")
        error_result = {
            "research_context": f"Research context gathering failed for: {query}",
            "identified_citations": [],
            "reputable_sources": [],
            "data_source": "error"
        }
        return json.dumps(error_result)


def extract_citations_from_text(text: str) -> List[str]:
    """Extract citation patterns from text."""
    # Common citation patterns
    citation_patterns = [
        r'\([A-Za-z]+\s+et\s+al\.?,?\s+\d{4}\)',  # (Smith et al., 2024)
        r'\([A-Za-z]+\s+&\s+[A-Za-z]+,?\s+\d{4}\)',  # (Smith & Jones, 2024)  
        r'\([A-Za-z]+,?\s+\d{4}\)',  # (Smith, 2024)
        r'doi:\s*10\.\d+\/[^\s]+',  # DOI patterns
        r'PMID:\s*\d+',  # PubMed IDs
    ]
    
    citations = []
    for pattern in citation_patterns:
        matches = re.findall(pattern, text)
        citations.extend(matches)
    
    return list(set(citations))  # Remove duplicates


def identify_reputable_sources(text: str) -> List[str]:
    """Identify reputable sources mentioned in the text."""
    reputable_sources = [
        "PubMed", "Cochrane", "NEJM", "Nature", "Science", "Lancet", "JAMA",
        "BMJ", "Cell", "Nature Medicine", "PLOS", "Oxford", "Cambridge",
        "Harvard", "Mayo Clinic", "NIH", "CDC", "WHO", "FDA", "EMA",
        "FAA", "EASA", "ICAO", "AsMA", "Aerospace Medical Association"
    ]
    
    found_sources = []
    text_lower = text.lower()
    
    for source in reputable_sources:
        if source.lower() in text_lower:
            found_sources.append(source)
            
    return found_sources


def generate_research_context_fallback_simple(query: str, analysis_domain: str) -> Dict[str, Any]:
    """Generate research context using OpenAI when Perplexity is unavailable."""
    try:
        openai_client = create_enhanced_openai_client()
        
        context_prompt = f"""
        As a scientific research expert, provide comprehensive research context for: {query}
        
        Domain: {analysis_domain}
        
        Please include:
        1. Current research landscape and key studies
        2. Methodological standards for this type of research
        3. Reputable journals and organizations in this field
        4. Data quality considerations
        5. Common research gaps and limitations
        
        Focus on evidence-based information and cite specific methodological frameworks where applicable.
        """
        
        context_response = openai_client.process_with_o3_and_web_search(context_prompt)
        
        return {
            "research_context": context_response,
            "identified_citations": extract_citations_from_text(context_response),
            "reputable_sources": identify_reputable_sources(context_response),
            "data_source": "openai_web_search"
        }
        
    except Exception as e:
        logger.error(f"Fallback context generation failed: {e}")
        return {
            "research_context": f"Unable to gather comprehensive research context. Please ensure your query includes specific research parameters for: {query}",
            "identified_citations": [],
            "reputable_sources": ["PubMed", "Cochrane", "NIH", "WHO"],
            "data_source": "minimal_fallback"
        }


@function_tool
def optimize_query_for_scientific_research(
    original_query: str,
    analysis_domain: str,
    analysis_research_type: str,
    analysis_scientific_rigor_needed: bool,
    research_context_json: str
) -> OptimizedQuery:
    """
    Optimize the query for scientific research standards and proper methodology.
    
    Args:
        original_query: The original user query
        analysis_domain: Domain from analysis
        analysis_research_type: Research type from analysis
        analysis_scientific_rigor_needed: Whether scientific rigor is needed
        research_context_json: JSON string containing research context and sources
        
    Returns:
        Optimized query with research alignment
    """
    try:
        import json
        logger.info("Optimizing query for scientific research standards")
        
        # Parse research context
        try:
            research_context = json.loads(research_context_json)
        except json.JSONDecodeError:
            research_context = {"research_context": "No context available", "reputable_sources": [], "identified_citations": []}
        
        # Build optimized query components
        research_methodology = determine_research_methodology_simple(analysis_research_type)
        citation_requirements = generate_citation_requirements_simple(analysis_scientific_rigor_needed, research_context)
        key_terms = extract_key_research_terms(original_query, research_context)
        
        # Create research-optimized query
        optimized_query_parts = [
            f"Research Question: {original_query}",
            "",
            f"Research Context: {research_context.get('research_context', 'No context available')[:500]}...",
            "",
            "Requirements:",
            "- Provide evidence-based analysis with specific citations",
            "- Include recent peer-reviewed research findings",
            "- Reference authoritative medical/scientific organizations",
            "- Apply appropriate research methodology standards",
            "- Identify research gaps and limitations",
            "- Ensure clinical or practical applicability where relevant"
        ]
        
        if research_context.get('reputable_sources'):
            optimized_query_parts.extend([
                "",
                f"Preferred Sources: {', '.join(research_context['reputable_sources'])}"
            ])
            
        if research_context.get('identified_citations'):
            optimized_query_parts.extend([
                "",
                f"Consider these existing citations: {'; '.join(research_context['identified_citations'][:5])}"
            ])
        
        optimized_query = "\n".join(optimized_query_parts)
        
        expected_sources = research_context.get('reputable_sources', []) + [
            "Peer-reviewed journals",
            "Systematic reviews",
            "Clinical practice guidelines",
            "Government health agencies",
            "Professional medical organizations"
        ]
        
        result = OptimizedQuery(
            optimized_query=optimized_query,
            research_context=research_context.get('research_context', ''),
            key_terms=key_terms,
            expected_sources=expected_sources,
            research_methodology=research_methodology,
            citation_requirements=citation_requirements
        )
        
        logger.info("Query optimization completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Error optimizing query: {e}")
        # Return minimal optimization
        return OptimizedQuery(
            optimized_query=f"Please provide a comprehensive, evidence-based response to: {original_query}. Include citations from reputable sources.",
            research_context="Research context unavailable",
            key_terms=original_query.split()[:10],
            expected_sources=["PubMed", "Cochrane"],
            research_methodology="Evidence-based analysis",
            citation_requirements="Include specific citations for all claims"
        )


def determine_research_methodology_simple(research_type: str) -> str:
    """Determine appropriate research methodology based on research type."""
    methodology_map = {
        "systematic_review": "PRISMA-compliant systematic review methodology with comprehensive literature search, quality assessment, and evidence synthesis",
        "risk_assessment": "Structured risk assessment framework with hazard identification, exposure assessment, and risk characterization",
        "comparative": "Comparative effectiveness research with controlled methodology and outcome measures",
        "exploratory": "Exploratory research with comprehensive literature review and expert consensus analysis"
    }
    
    return methodology_map.get(research_type, "Evidence-based research methodology")


def generate_citation_requirements_simple(scientific_rigor_needed: bool, research_context: Dict[str, Any]) -> str:
    """Generate specific citation requirements based on the research context."""
    base_requirements = [
        "Use APA or Vancouver citation style",
        "Include DOI or PMID when available",
        "Prioritize peer-reviewed sources",
        "Include publication dates",
    ]
    
    if scientific_rigor_needed:
        base_requirements.extend([
            "Include systematic reviews and meta-analyses when available",
            "Reference clinical practice guidelines",
            "Cite authoritative medical/scientific organizations"
        ])
        
    # Always prioritize recent sources for scientific research
    base_requirements.append("Prioritize sources from the last 5 years")
        
    return "; ".join(base_requirements)


def extract_key_research_terms(query: str, research_context: Dict[str, Any]) -> List[str]:
    """Extract key research terms from the query and context."""
    # Basic term extraction - could be enhanced with NLP
    query_terms = [word.strip('.,!?') for word in query.split() if len(word) > 3]
    
    # Add terms from research context if available
    context_text = research_context.get('research_context', '')
    if context_text:
        # Simple extraction of potential key terms
        important_words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', context_text)
        query_terms.extend(important_words[:10])
    
    return list(set(query_terms))[:15]  # Limit and deduplicate


def create_query_optimizer_agent() -> Agent:
    """
    Create the main Query Optimizer Agent that orchestrates the optimization process.
    
    This agent coordinates all optimization steps and produces the final optimized query.
    """
    instructions = """
    You are the Query Optimizer Agent - the first agent in our research pipeline. Your critical role is to transform user queries into scientifically rigorous, well-researched questions that will produce high-quality, evidence-based responses.

    CORE MISSION:
    Transform every user query to align with scientific research standards, incorporate reputable sources, and ensure proper citation practices.

    OPTIMIZATION WORKFLOW:
    1. Use analyze_query_for_research_alignment() to understand the query's research requirements
    2. Use gather_research_context_and_sources() to gather current research context and identify sources
    3. Use optimize_query_for_scientific_research() to create the final optimized query

    OUTPUT REQUIREMENTS:
    - Always output a comprehensive OptimizedQuery structure
    - Include specific research methodology guidance
    - Provide clear citation requirements
    - Identify key terms and expected sources
    - Ensure the optimized query will produce evidence-based responses with proper citations

    SCIENTIFIC STANDARDS:
    - Prioritize peer-reviewed sources and systematic reviews
    - Include methodological rigor appropriate to the domain
    - Ensure clinical applicability for medical queries
    - Reference authoritative organizations (WHO, NIH, FAA, etc.)
    - Include recent research findings when available

    Your optimization ensures that downstream agents receive queries that will produce scientifically sound, well-cited responses with real data from reputable sources.
    """
    
    return Agent(
        name="Query Optimizer Agent",
        instructions=instructions,
        tools=[
            analyze_query_for_research_alignment,
            gather_research_context_and_sources,
            optimize_query_for_scientific_research
        ],
        output_type=OptimizedQuery,
        model=OpenAIModelsConfig.O3_DEEP_RESEARCH.model_name
    )


def create_query_optimization_system() -> Dict[str, Agent]:
    """
    Create the complete query optimization system.
    
    Returns:
        Dictionary mapping agent names to agent instances
    """
    optimizer_agent = create_query_optimizer_agent()
    
    return {
        "optimizer": optimizer_agent
    }


# Testing and validation functions
async def test_query_optimization(test_query: str) -> OptimizedQuery:
    """Test the query optimization system with a sample query."""
    from agents import Runner
    
    optimizer_agent = create_query_optimizer_agent()
    
    try:
        response = await Runner.run(optimizer_agent, test_query)
        return response.final_output if response else None
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return None


if __name__ == "__main__":
    import asyncio
    
    # Set up logging for testing
    logging.basicConfig(level=logging.INFO)
    
    # Test the system
    test_query = "What are the cardiovascular risks for commercial pilots?"
    
    async def main():
        result = await test_query_optimization(test_query)
        if result:
            print(f"Optimized Query: {result.optimized_query[:200]}...")
            print(f"Key Terms: {result.key_terms}")
            print(f"Expected Sources: {result.expected_sources}")
        else:
            print("Test failed")
    
    asyncio.run(main()) 