"""
System-level tests for the Multi-Agent Prompt Enhancement Application.
"""
import pytest
from unittest.mock import MagicMock, patch
import requests

from src.main import EnhancedPromptEnhancerApp
from src.flowise_client import FlowiseClient, FlowiseAPIError
from src.config import AppConfig

@pytest.fixture
def app():
    """Fixture to initialize the main application."""
    # Mock environment validation to prevent system exit
    with patch.object(AppConfig, 'validate_environment', return_value=True), \
         patch.object(AppConfig, 'validate_chatflow_ids', return_value={'aeromedical_risk': True}):
        # Mock setup_logging to avoid file IO
        with patch('src.main.setup_logging'):
            application = EnhancedPromptEnhancerApp()
            return application

def test_app_initialization(app):
    """Test that the main application initializes without errors."""
    assert app is not None
    assert app.console is not None
    assert app.mode_manager is not None
    assert app.current_mode == "smart"

def test_command_handling(app):
    """Test that basic commands are handled correctly."""
    assert not app.handle_enhanced_user_input("/quit") # Should exit
    assert app.handle_enhanced_user_input("/modes") # Should continue
    
    # Check that mode switching works
    app.handle_enhanced_user_input("/prompt")
    assert app.current_mode == "prompt"

@patch('requests.post')
def test_flowise_api_failure_handling(mock_post, app):
    """Test how the system handles a Flowise API failure."""
    
    # Simulate a 500 server error from Flowise
    mock_post.return_value = MagicMock(status_code=500)
    
    client = FlowiseClient()
    
    # The retry decorator should raise the final exception
    with pytest.raises(requests.exceptions.HTTPError):
        client.query_chatflow("some_id", "some_question")

@patch('requests.post')
def test_flowise_authentication_error(mock_post, app):
    """Test handling of a 401 authentication error."""
    
    # Simulate a 401 Unauthorized error
    mock_post.return_value = MagicMock(status_code=401)
    
    client = FlowiseClient()
    
    with pytest.raises(FlowiseAPIError, match="Authentication failed"):
        client.query_chatflow("some_id", "some_question")

@patch('requests.post')
def test_flowise_chatflow_not_found(mock_post, app):
    """Test handling of a 404 not found error."""
    
    # Simulate a 404 Not Found error
    mock_post.return_value = MagicMock(status_code=404)
    
    client = FlowiseClient()
    
    with pytest.raises(FlowiseAPIError, match="Chatflow not found"):
        client.query_chatflow("non_existent_id", "some_question")

@patch('asyncio.run')
@patch('agents.Runner.run')
def test_fallback_mechanism(mock_runner_run, mock_asyncio_run, app):
    """Test the fallback mechanism when Flowise fails and fallback is enabled."""
    
    # Configure app for the test
    app.mode_manager.switch_mode("aeromedical_risk")
    app.user_preferences["auto_fallback"] = True
    
    # First call to runner (Flowise) raises an error
    mock_runner_run.side_effect = [
        Exception("Flowise API is down"),
        MagicMock(final_output="This is the fallback response.") # Second call (Prompt)
    ]

    # The main loop's call to asyncio.run will trigger our mock
    def mock_run(coro):
        # We manually await the coroutine to simulate the event loop
        # This is a simplified way to handle this for the test
        try:
            coro.send(None)
        except StopIteration as e:
            return e.value
    
    mock_asyncio_run.side_effect = mock_run

    # Simulate processing a user request
    app.handle_enhanced_user_input("what are the risks?")
    
    # Assertions
    # 1. Runner was called twice (initial attempt + fallback)
    assert mock_runner_run.call_count == 2
    
    # 2. The mode was switched to 'prompt' for fallback
    assert app.current_mode == "prompt"
    
    # 3. The fallback response was added to messages
    assert len(app.messages) == 2 # user query + fallback response
    assert app.messages[-1]["content"] == "This is the fallback response." 