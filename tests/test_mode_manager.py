"""
Tests for the ModeManager class.
"""
import pytest
from unittest.mock import Mock, MagicMock

from src.mode_manager import ModeManager
from src.config import AppConfig

@pytest.fixture
def mock_app():
    """Fixture for a mocked application object."""
    app = Mock()
    app.console = MagicMock()
    app.prompt_agents = "prompt_agent"
    app.flowise_agents = {
        "deep_research": "deep_research_agent",
        "aeromedical_risk": "aeromedical_risk_agent",
        "aerospace_medicine_rag": "aerospace_medicine_rag_agent",
    }
    app.prisma_system = "prisma_agent"
    app.user_preferences = {
        "auto_suggest": True,
        "confirm_mode_switch": False,
    }
    return app


class TestModeManager:
    """Tests for the ModeManager class."""

    def test_initialization(self, mock_app):
        """Test that the ModeManager initializes correctly."""
        manager = ModeManager(mock_app)
        assert manager.app is not None
        assert manager.console is not None
        assert manager.current_mode == "smart"
        assert manager.current_agent is None

    def test_switch_mode(self, mock_app):
        """Test switching modes."""
        manager = ModeManager(mock_app)
        
        manager.switch_mode("prompt")
        assert manager.current_mode == "prompt"
        assert manager.current_agent == "prompt_agent"
        assert mock_app.current_mode == "prompt"
        assert mock_app.current_agent == "prompt_agent"

        manager.switch_mode("deep_research")
        assert manager.current_mode == "deep_research"
        assert manager.current_agent == "deep_research_agent"

    def test_switch_mode_invalid(self, mock_app):
        """Test switching to an invalid mode."""
        manager = ModeManager(mock_app)
        assert not manager.switch_mode("invalid_mode")
        assert manager.current_mode == "smart" # Should not change

    @pytest.mark.parametrize("query, expected_mode", [
        ("explain in detail how quantum computing works", "prompt"),
        ("I need a comprehensive literature review on pilot fatigue", "deep_research"),
        ("what is the risk assessment for a pilot with diabetes", "aeromedical_risk"),
        ("give me a scientific article about aerospace medicine", "aerospace_medicine_rag"),
        ("start a prisma systematic review of telemedicine", "prisma"),
        ("what is the weather like today?", "prompt"), # default
        ("a study of pilots and artificial intelligence", "prompt"), # mixed
    ])
    def test_detect_optimal_mode(self, mock_app, query, expected_mode):
        """Test the mode detection with various queries."""
        manager = ModeManager(mock_app)
        detected_mode, confidence = manager.detect_optimal_mode(query)
        assert detected_mode == expected_mode

    def test_handle_smart_mode_detection_no_switch(self, mock_app):
        """Test that mode is not switched when not in smart mode."""
        manager = ModeManager(mock_app)
        manager.switch_mode("prompt")
        assert not manager.handle_smart_mode_detection("a query")

    def test_handle_smart_mode_detection_with_auto_switch(self, mock_app):
        """Test automatic mode switching in smart mode."""
        manager = ModeManager(mock_app)
        mock_app.user_preferences["confirm_mode_switch"] = False
        
        query = "I need a comprehensive literature review on pilot fatigue"
        manager.handle_smart_mode_detection(query)
        
        assert manager.current_mode == "deep_research"
        mock_app.console.print.assert_any_call("[green]🎯 Auto-detected optimal mode: 🔬 Deep Research (confidence: 100.0%)[/green]") 