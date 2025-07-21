"""
Enhanced Multi-Agent Prompt Enhancement Application.

This is the main application file that provides an improved text-based interface
for the multi-agent prompt enhancement system with intelligent mode detection
and streamlined user experience.
"""

from __future__ import annotations

import logging
import sys
import os
import re
import asyncio
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import argparse

from .custom_rich.stubs import Console, Panel, Table, Text, Prompt, Confirm, Markdown

from rich.console import Console as RichConsole
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.live import Live
from pydantic import BaseModel

from .config import AppConfig, FlowiseConfig
from .multiline_input import MultilineInputHandler, detect_paste_input
from .markdown_exporter import MarkdownExporter
from .ui import AsyncProgressHandler, UserInterface
from .jobs import JobStore
from .core_agents import run_research_pipeline


# Set up logging with proper Unicode support
def setup_logging():
    """Set up logging with UTF-8 encoding support for Windows compatibility."""
    # Windows-specific console encoding fix
    if sys.platform.startswith('win'):
        try:
            # Try to set console to UTF-8 on Windows
            os.system('chcp 65001 >nul 2>&1')
        except Exception:
            pass  # Ignore if this fails
    
    # Clear any existing handlers
    logging.getLogger().handlers.clear()
    
    # Create formatters
    formatter = logging.Formatter(AppConfig.LOG_FORMAT)
    
    # Console handler with UTF-8 support
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # File handler with explicit UTF-8 encoding
    file_handler = logging.FileHandler('prompt_enhancer.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, AppConfig.LOG_LEVEL))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

setup_logging()

logger = logging.getLogger(__name__)


class EnhancedPromptEnhancerApp:
    """
    Enhanced Multi-Agent Prompt Enhancement system with improved UX.
    
    This class provides an intuitive text-based interface with smart mode detection,
    streamlined navigation, and enhanced user guidance.
    """
    
    def __init__(self):
        """Initialize the enhanced prompt enhancer application."""
        self.console = Console()
        self.multiline_handler = MultilineInputHandler(self.console)
        self.markdown_exporter = MarkdownExporter()
        self.progress_handler = AsyncProgressHandler(self.console)
        self.ui = UserInterface(self)
        self.job_store = JobStore()
        self.messages: List[Dict[str, Any]] = []
        self.last_user_query: Optional[str] = None
        
        logger.info("Enhanced Research App initialized successfully")

    async def process_user_request(self, user_input: str) -> bool:
        """
        Processes the user's research query using the new core agent pipeline.
        """
        self.last_user_query = user_input
        self.messages.append({"role": "user", "content": user_input})

        self.console.print("\n🔬 [cyan]Initiating deep research pipeline...[/cyan]")
        self.console.print("[dim]This may take several minutes. I will stream updates as I get them.[/dim]")
        
        try:
            # The new pipeline handles everything from optimization to final report.
            final_output = await run_research_pipeline(user_input, verbose=True)

            assistant_message = {"role": "assistant", "content": str(final_output)}
            self.messages.append(assistant_message)

            self.console.print(f"\n🤖 [bold]Deep Research Agent Response:[/bold]")
            self.console.print("─" * 60)
            self.console.print(Markdown(str(final_output)))
            self.console.print("─" * 60)

            self.console.print(f"\n[green]✅ Research completed successfully![/green]")
            self.ui.show_export_options()

        except Exception as e:
            logger.error(f"Error in deep research pipeline: {e}", exc_info=True)
            self.console.print(f"❌ [red]An error occurred during research: {e}[/red]")
        
        return True

    def run_enhanced(self) -> None:
        """Main application loop."""
        self.ui.display_enhanced_welcome()
        
        while True:
            try:
                user_input = self.multiline_handler.get_single_or_multiline_input()
                if user_input.strip().lower() in ['/quit', '/exit', '/q']:
                    break
                
                if user_input.strip().startswith('/'):
                    self.console.print("[yellow]Commands are currently disabled during the refactor. Please enter a research query.[/yellow]")
                    continue
                
                if not user_input.strip():
                    continue

                asyncio.run(self.process_user_request(user_input))

            except KeyboardInterrupt:
                self.console.print("\n\n[bold yellow]Exiting application.[/bold yellow]")
                break
            except Exception as e:
                logger.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)
                self.console.print(f"\n[bold red]An unexpected error occurred: {e}[/bold red]")


def main() -> None:
    """Main entry point for the enhanced application."""
    parser = argparse.ArgumentParser(description="Enhanced Multi-Agent Research Application.")
    parser.add_argument("query", nargs='?', default=None, help="If provided, runs a single query and exits.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging.")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        app = EnhancedPromptEnhancerApp()
        if args.query:
            print("Running single query...")
            asyncio.run(app.process_user_request(args.query))
        else:
            app.run_enhanced()
        
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user.")
    except Exception as e:
        logger.error(f"Fatal application error: {e}", exc_info=True)
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 