"""
Tests for the PRISMA Systematic Review feature.
"""
import pytest
from unittest.mock import patch, MagicMock

# Mock expensive imports
from src.config import AppConfig, PRISMAConfig

# Since this is a test file, we will mock the clients to avoid real API calls
@pytest.fixture
def mock_clients():
    """Fixture to mock all external API clients."""
    with patch('src.prisma_agents.PerplexityClient') as mock_pplx, \
         patch('src.prisma_agents.GrokClient') as mock_grok, \
         patch('src.prisma_agents.FlowiseClient') as mock_flowise, \
         patch('src.prisma_agents.OpenAI') as mock_openai:
        yield {
            "perplexity": mock_pplx,
            "grok": mock_grok,
            "flowise": mock_flowise,
            "openai": mock_openai
        }

def test_prisma_configuration():
    """Tests that PRISMA configuration is loaded correctly."""
    assert PRISMAConfig.O3_HIGH_REASONING.model_name is not None
    assert PRISMAConfig.PERPLEXITY_MODEL is not None
    assert PRISMAConfig.GROK_MODEL is not None
    assert PRISMAConfig.TARGET_WORD_COUNT > 0
    assert PRISMAConfig.MIN_CITATIONS > 0
    assert len(PRISMAConfig.PRISMA_CHATFLOWS) > 0

def test_prisma_agent_system_creation(mock_clients):
    """Tests that the PRISMA agent system and its agents can be created."""
    from src.prisma_agents import create_prisma_agent_system
    
    # We need to ensure that the environment is "valid" for the test
    with patch.object(AppConfig, 'validate_prisma_environment', return_value=True):
        agents = create_prisma_agent_system()

    assert "orchestrator" in agents
    assert "searcher" in agents
    assert "reviewer" in agents
    assert "writer" in agents
    assert "validator" in agents
    
    # Check that one of the agents has tools
    assert len(agents["searcher"].tools) > 0

def test_prisma_tools_initialization(mock_clients):
    """Tests initialization of PRISMAAgentTools."""
    from src.prisma_agents import PRISMAAgentTools

    with patch.object(AppConfig, 'validate_prisma_environment', return_value=True):
        tools = PRISMAAgentTools()

    assert tools.perplexity_client is not None
    assert tools.grok_client is not None
    assert tools.flowise_client is not None
    assert tools.openai_client is not None

@patch('src.prisma_agents.PRISMAWorkflow')
def test_initialize_workflow_tool(mock_workflow, mock_clients):
    """Test the initialize_workflow tool."""
    from src.prisma_agents import PRISMAAgentTools, SearchStrategy

    tools = PRISMAAgentTools()
    strategy = SearchStrategy(keywords=["test"], databases=["test"], date_range="2024", language="en")
    
    result = tools.initialize_workflow(
        research_question="test question",
        search_strategy=strategy,
        inclusion_criteria=[],
        exclusion_criteria=[]
    )
    
    assert "✅ PRISMA workflow initialized" in result
    mock_workflow.assert_called_once() 