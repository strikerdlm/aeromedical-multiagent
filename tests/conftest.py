import sys
import os
import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Provide dummy fixtures expected by test_live_apis.py so that the file can be
# collected by *pytest* without raising a *FixtureLookupError* even when the
# environment is not configured for live API tests.

@pytest.fixture(name="chatflow_name")
def _fixture_chatflow_name():
    return "Dummy Chatflow"


@pytest.fixture(name="chatflow_id")
def _fixture_chatflow_id():
    return "dummy-id" 