import pytest
from unittest.mock import patch, MagicMock
import requests

from src.flowise_client import FlowiseClient, FlowiseAPIError, ConfigurationError

# Test data
TEST_CHATFLOW_ID = "test-chatflow"
TEST_QUESTION = "What is the meaning of life?"
TEST_API_KEY = "test-api-key"
TEST_BASE_URL = "http://fake-flowise-url.com"

@pytest.fixture
def flowise_client():
    """Fixture for a configured FlowiseClient."""
    return FlowiseClient(api_key=TEST_API_KEY, base_url=TEST_BASE_URL)

def test_client_initialization_success(flowise_client):
    """Test that the client initializes correctly with an API key."""
    assert flowise_client.api_key == TEST_API_KEY
    assert flowise_client.base_url == TEST_BASE_URL
    assert flowise_client.headers["Authorization"] == f"Bearer {TEST_API_KEY}"

def test_client_initialization_no_api_key():
    """Test that the client raises ConfigurationError if API key is missing."""
    with pytest.raises(ConfigurationError, match="Flowise API key is not configured"):
        FlowiseClient(api_key=None)

@patch('requests.post')
def test_query_chatflow_success(mock_post, flowise_client):
    """Test a successful chatflow query."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "42"}
    mock_post.return_value = mock_response

    response = flowise_client.query_chatflow(TEST_CHATFLOW_ID, TEST_QUESTION)

    assert response == {"result": "42"}
    mock_post.assert_called_once()

@patch('requests.post')
def test_query_chatflow_authentication_error(mock_post, flowise_client):
    """Test a 401 authentication error."""
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_post.return_value = mock_response

    with pytest.raises(FlowiseAPIError, match="Authentication failed"):
        flowise_client.query_chatflow(TEST_CHATFLOW_ID, TEST_QUESTION)

@patch('requests.post')
def test_query_chatflow_not_found_error(mock_post, flowise_client):
    """Test a 404 not found error."""
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_post.return_value = mock_response

    with pytest.raises(FlowiseAPIError, match="Chatflow not found"):
        flowise_client.query_chatflow(TEST_CHATFLOW_ID, TEST_QUESTION)

@patch('requests.post')
def test_query_chatflow_server_error_retry(mock_post, flowise_client):
    """Test that a 500 server error triggers a retry via the decorator."""
    mock_response_500 = MagicMock()
    mock_response_500.status_code = 500
    # Make raise_for_status raise an exception
    mock_response_500.raise_for_status.side_effect = requests.exceptions.HTTPError

    mock_response_200 = MagicMock()
    mock_response_200.status_code = 200
    mock_response_200.json.return_value = {"result": "success after retry"}

    # First call returns 500, second returns 200
    mock_post.side_effect = [mock_response_500, mock_response_200]

    with patch('time.sleep', return_value=None): # Mock sleep to speed up test
        response = flowise_client.query_chatflow(TEST_CHATFLOW_ID, TEST_QUESTION)
    
    assert response == {"result": "success after retry"}
    assert mock_post.call_count == 2

@patch('requests.post')
def test_query_chatflow_request_exception(mock_post, flowise_client):
    """Test that a RequestException is handled and retried."""
    mock_post.side_effect = [requests.exceptions.ConnectionError, MagicMock(status_code=200, json=lambda: {"result": "connected"})]

    with patch('time.sleep', return_value=None):
        response = flowise_client.query_chatflow(TEST_CHATFLOW_ID, TEST_QUESTION)

    assert response == {"result": "connected"}
    assert mock_post.call_count == 2 