"""
Tests for Unicode logging and the logging setup.
"""
import pytest
import logging
import os
import subprocess
from unittest.mock import patch, MagicMock

from src.main import setup_logging

# A diverse set of Unicode strings for testing
UNICODE_STRINGS = [
    "Miller AL et al., Acta Astronáut 2024",
    "Young LR et al., NPJ Microgravity 2023",
    "Díaz Artiles A et al., Front Physiol 2022",
    "Mathematical symbols: π ∑ ∂ ∫ √ α β γ",
    "Accented characters: café résumé naïve",
    "German umlauts: Müller, Bäcker, Köln",
    "Mixed: Smith & Jones (2024) → \"Advanced μ-gravity effects\"",
    "Citation with em-dash: Research findings — comprehensive analysis",
    "Emoji: 🚀🧪📊",
]

@pytest.fixture(scope="function")
def configured_logging(tmp_path):
    """Fixture to set up and tear down logging for a test."""
    log_file = tmp_path / "test.log"
    
    # We patch os.system to avoid actually trying to change the console codepage
    with patch('os.system') as mock_os_system:
        # We need to get a fresh logger for each test
        logging.shutdown()
        reload(logging)
        
        # Save the original FileHandler class
        original_file_handler = logging.FileHandler
        
        # Create a custom FileHandler that uses our temp file
        class TestFileHandler(logging.FileHandler):
            def __init__(self, filename, mode='a', encoding=None, delay=False, errors=None):
                super().__init__(str(log_file), mode, encoding, delay, errors)
        
        # Patch FileHandler with our custom class
        logging.FileHandler = TestFileHandler
        try:
            setup_logging()
        finally:
            # Restore the original FileHandler
            logging.FileHandler = original_file_handler
    
    yield log_file
    
    # Teardown
    logging.getLogger().handlers.clear()

def test_setup_logging_creates_handlers(configured_logging):
    """Test that setup_logging correctly adds handlers to the root logger."""
    logger = logging.getLogger()
    # Find our handlers (ignore pytest's handlers)
    stream_handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)]
    file_handlers = [h for h in logger.handlers if isinstance(h, logging.FileHandler)]
    
    assert len(stream_handlers) >= 1, "Should have at least one StreamHandler"
    assert len(file_handlers) >= 1, "Should have at least one FileHandler"
    assert file_handlers[0].encoding == 'utf-8'

@pytest.mark.parametrize("message", UNICODE_STRINGS)
def test_logging_unicode_to_file(configured_logging, message):
    """Test that Unicode strings are correctly written to the log file."""
    log_file = configured_logging
    
    logger = logging.getLogger("test_unicode_file")
    logger.warning(message)
    
    # Check that the file was written with the correct encoding
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert message in content

def test_logging_dict_with_unicode(configured_logging):
    """Test logging a dictionary containing Unicode characters."""
    log_file = configured_logging
    test_dict = {
        "author": "Díaz Artiles",
        "symbol": "π",
        "year": 2022
    }
    
    logger = logging.getLogger("test_dict")
    logger.info(test_dict)
    
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    assert "Díaz Artiles" in content
    assert "π" in content

def test_logging_exception_with_unicode(configured_logging):
    """Test logging an exception that has a Unicode message."""
    log_file = configured_logging
    error_message = "An error occurred with symbol: α"
    
    logger = logging.getLogger("test_exception")
    try:
        raise ValueError(error_message)
    except ValueError as e:
        logger.exception("Caught an exception with Unicode.")
    
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    assert "ValueError" in content
    assert error_message in content
    assert "Caught an exception with Unicode" in content

@patch('sys.platform', 'win32')
@patch('subprocess.run')
def test_windows_chcp_command_is_called(mock_subprocess_run):
    """Test that the 'chcp' command is called on Windows."""
    # We need to reload logging to clear its internal state
    logging.shutdown()
    reload(logging)
    
    setup_logging()
    mock_subprocess_run.assert_called_once_with(['chcp', '65001'],
                                               stdout=subprocess.DEVNULL,
                                               stderr=subprocess.DEVNULL,
                                               check=False)

@patch('sys.platform', 'linux')
@patch('subprocess.run')
def test_windows_chcp_command_not_called_on_linux(mock_subprocess_run):
    """Test that the 'chcp' command is NOT called on non-Windows systems."""
    logging.shutdown()
    reload(logging)
    
    setup_logging()
    mock_subprocess_run.assert_not_called() 