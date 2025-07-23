import pytest

@pytest.fixture(name="chatflow_name")
def _fixture_chatflow_name():
    return "Dummy Chatflow"


@pytest.fixture(name="chatflow_id")
def _fixture_chatflow_id():
    return "dummy-id"