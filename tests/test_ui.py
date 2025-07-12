"""
Tests for the UI components of the application.
"""
import pytest
from unittest.mock import Mock, MagicMock

from src.ui import UserInterface

@pytest.fixture
def mock_app():
    """Fixture for a mocked application object."""
    app = Mock()
    app.console = MagicMock()
    app.current_mode = "smart"
    app.messages = []
    app.user_preferences = {
        "auto_suggest": True,
        "show_tips": True,
        "confirm_mode_switch": False,
        "auto_fallback": True
    }
    app.multiline_handler = MagicMock()
    app.markdown_exporter = MagicMock()
    app.prisma_system = MagicMock()
    return app


class TestUserInterface:
    """Tests for the UserInterface class."""

    def test_initialization(self, mock_app):
        """Test that the UserInterface initializes correctly."""
        ui = UserInterface(mock_app)
        assert ui.app is not None
        assert ui.console is not None
        assert ui.exporter is not None
        assert ui.prisma_display is not None

    def test_display_enhanced_welcome(self, mock_app, capsys):
        """Test the welcome message display."""
        ui = UserInterface(mock_app)
        ui.display_enhanced_welcome()
        assert mock_app.console.print.call_count > 0

    def test_display_current_status(self, mock_app, capsys):
        """Test the status display."""
        ui = UserInterface(mock_app)
        ui.display_current_status()
        mock_app.console.print.assert_any_call("📊 [bold]Current Status[/bold]")
        mock_app.console.print.assert_any_call("Current Mode: 🎯 Smart Auto-Detection")

    def test_display_mode_selection(self, mock_app, capsys):
        """Test the mode selection display."""
        ui = UserInterface(mock_app)
        ui.display_mode_selection()
        mock_app.console.print.assert_any_call("🛠️ [bold]Available Processing Modes[/bold]")
        mock_app.console.print.assert_any_call("[cyan]🎯 Smart Auto-Detection[/cyan]")

    def test_provide_contextual_tip(self, mock_app):
        """Test that a tip is provided."""
        ui = UserInterface(mock_app)
        ui.provide_contextual_tip()
        assert mock_app.console.print.call_count == 1
        
    def test_toggle_fallback(self, mock_app):
        """Test toggling the fallback preference."""
        ui = UserInterface(mock_app)
        initial_fallback = mock_app.user_preferences["auto_fallback"]
        
        ui.toggle_fallback()
        
        # Check that the preference was flipped
        assert mock_app.user_preferences["auto_fallback"] is not initial_fallback
        
        # Check that a message was printed
        assert mock_app.console.print.call_count > 0 