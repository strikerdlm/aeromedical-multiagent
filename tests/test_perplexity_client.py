import pytest
from unittest.mock import patch, MagicMock
import requests

from src.perplexity_client import PerplexityClient, PerplexityAPIError, ConfigurationError

# Test data
TEST_API_KEY = "test-pplx-api-key"
TEST_QUERY = "test query"

@pytest.fixture
def perplexity_client():
    """Fixture for a configured PerplexityClient."""
    return PerplexityClient(api_key=TEST_API_KEY)

def test_client_initialization_success(perplexity_client):
    """Test that the client initializes correctly with an API key."""
    assert perplexity_client.api_key == TEST_API_KEY
    assert "Authorization" in perplexity_client.headers
    assert perplexity_client.headers["Authorization"] == f"Bearer {TEST_API_KEY}"

def test_client_initialization_no_api_key():
    """Test that the client raises ConfigurationError if API key is missing."""
    with pytest.raises(ConfigurationError, match="Perplexity API key is not configured"):
        PerplexityClient(api_key=None)

@patch('src.perplexity_client.PerplexityClient._make_api_request')
def test_search_literature_success(mock_api_request, perplexity_client):
    """Test a successful literature search."""
    mock_api_request.return_value = {
        "choices": [{"message": {"content": "search results"}}],
        "citations": [],
        "model": "test-model",
        "usage": {}
    }
    
    result = perplexity_client.search_literature(TEST_QUERY)
    
    assert "content" in result
    assert result["content"] == "search results"
    mock_api_request.assert_called_once()

@patch.object(PerplexityClient, '_make_api_request', side_effect=PerplexityAPIError("API Failure"))
def test_search_literature_api_error(mock_api_request, perplexity_client):
    """Test that an API error is propagated."""
    with pytest.raises(PerplexityAPIError, match="Literature search failed: API Failure"):
        perplexity_client.search_literature(TEST_QUERY)

@patch('requests.Session.post')
def test_make_api_request_retry_on_429(mock_post):
    """Test that the client retries on a 429 rate limit error."""
    client = PerplexityClient(api_key=TEST_API_KEY)
    
    mock_response_429 = MagicMock()
    mock_response_429.status_code = 429
    mock_response_429.raise_for_status.side_effect = requests.exceptions.HTTPError

    mock_response_200 = MagicMock()
    mock_response_200.status_code = 200
    mock_response_200.json.return_value = {"status": "ok"}
    
    mock_post.side_effect = [mock_response_429, mock_response_200]
    
    with patch('time.sleep', return_value=None):
        response = client._make_api_request("/test", {})
    
    assert response == {"status": "ok"}
    assert mock_post.call_count == 2

@patch('requests.Session.post')
def test_make_api_request_fails_on_401(mock_post):
    """Test that the client fails immediately on a 401 error."""
    client = PerplexityClient(api_key=TEST_API_KEY)

    mock_response_401 = MagicMock()
    mock_response_401.status_code = 401
    mock_post.return_value = mock_response_401

    with pytest.raises(PerplexityAPIError, match="Authentication failed"):
        client._make_api_request("/test", {})
    
    assert mock_post.call_count == 1 