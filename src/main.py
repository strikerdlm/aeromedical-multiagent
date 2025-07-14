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
from agents import Runner

from .config import AppConfig
from .prompt_agents import create_prompt_enhancement_system
from .flowise_agents import create_flowise_enhancement_system
from .flowise_client import FlowiseAPIError
from .multiline_input import MultilineInputHandler, detect_paste_input
from .markdown_exporter import MarkdownExporter
from .prisma_agents import PRISMAAgentSystem, create_prisma_agent_system
from .ui import AsyncProgressHandler, UserInterface
from .mode_manager import ModeManager


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
        self.mode_manager = ModeManager(self)
        
        # Create both agent systems
        self.prompt_agents = create_prompt_enhancement_system()
        self.flowise_agents = create_flowise_enhancement_system()
        
        # Initialize PRISMA orchestrator (optional, depends on API availability)
        self.prisma_system: Optional[PRISMAAgentSystem] = None
        try:
            if AppConfig.validate_prisma_environment():
                self.prisma_system = PRISMAAgentSystem()
                logger.info("PRISMA agent system initialized successfully")
        except Exception as e:
            logger.warning(f"PRISMA system initialization failed: {e}")
            self.prisma_system = None
        
        self.messages: List[Dict[str, Any]] = []
        self.last_user_query: Optional[str] = None
        
        # Current processing mode and agent - managed by ModeManager
        self.current_mode: str = "smart"
        self.current_agent = None

        self.user_preferences = {
            "auto_suggest": True,
            "show_tips": True,
            "confirm_mode_switch": False,
            "auto_fallback": True
        }
        
        logger.info("Enhanced Prompt Enhancer App initialized successfully")
    
    def handle_enhanced_user_input(self, user_input: str) -> bool:
        """
        Enhanced input handler with better command processing.
        
        Args:
            user_input: The user's input string
            
        Returns:
            True to continue, False to exit
        """
        user_input = user_input.strip()
        
        # Handle quick help
        if user_input == "?":
            self.ui.display_contextual_help()
            return True
        
        # Handle commands
        if user_input.startswith('/'):
            command = user_input[1:].lower()
            
            # Exit commands
            if command in ['quit', 'exit', 'q']:
                return False
            
            # Mode switching commands
            elif command in ['smart', 's']:
                self.mode_manager.switch_mode("smart")
                return True
            elif command in ['prompt', 'p']:
                self.mode_manager.switch_mode("prompt")
                return True
            elif command in ['deep', 'deepresearch', 'd']:
                self.mode_manager.switch_mode("deep_research")
                return True
            elif command in ['aero', 'aeromedical', 'risk', 'a']:
                self.mode_manager.switch_mode("aeromedical_risk")
                return True
            elif command in ['aerospace', 'aerospace_medicine', 'medicine', 'am']:
                self.mode_manager.switch_mode("aerospace_medicine_rag")
                return True
            elif command in ['prisma', 'systematic', 'review', 'p']:
                self.mode_manager.switch_mode("prisma")
                return True
            elif command.startswith('transfer'):
                parts = command.split()
                if len(parts) > 1:
                    target_mode = parts[1]
                    return self.handle_transfer_request(target_mode)
                else:
                    self.console.print("[red]❌ Usage: /transfer <mode>[/red]")
                    self.ui.display_mode_selection()
                    return True
            
            # Information commands
            elif command in ['modes', 'mode', 'm']:
                self.ui.display_mode_selection()
                return True
            elif command in ['help', 'h']:
                self.ui.display_contextual_help()
                return True
            elif command in ['status', 'stat']:
                self.ui.display_current_status()
                return True
            elif command in ['history', 'hist']:
                self.ui.display_conversation_history()
                return True
            elif command in ['clear', 'reset', 'c']:
                self.messages = []
                self.console.print("🧹 [green]Conversation history cleared.[/green]")
                return True
            
            # Settings commands
            elif command in ['settings', 'config']:
                self.ui.display_settings()
                return True
            elif command in ['fallback', 'toggle-fallback']:
                self.ui.toggle_fallback()
                return True
            
            # Export commands
            elif command in ['export', 'save-response']:
                self.ui.export_latest_response()
                return True
            elif command in ['save', 'save-conversation']:
                self.ui.export_full_conversation()
                return True
            elif command in ['report', 'save-report']:
                self.ui.export_structured_report()
                return True
            elif command in ['exports', 'list-exports']:
                self.ui.list_exported_files()
                return True
            
            # PRISMA-specific commands
            elif command in ['prisma-status', 'prisma-info']:
                self.ui.display_prisma_status()
                return True
            elif command in ['prisma-reviews', 'prisma-history']:
                self.ui.display_prisma_reviews()
                return True
            
            else:
                self.console.print(f"[red]❌ Unknown command: /{command}[/red]")
                self.console.print("[yellow]💡 Type ? for help or /modes to see available modes[/yellow]")
                return True
        
        # Handle empty input
        if not user_input:
            self.console.print("[yellow]💬 Please enter a question or command. Type ? for help.[/yellow]")
            return True
        
        # It's a query, not a command. Store it.
        self.last_user_query = user_input
        
        # Smart mode detection
        mode_changed = self.mode_manager.handle_smart_mode_detection(user_input)
        
        # Check if this looks like pasted content
        if detect_paste_input(user_input):
            self.console.print("[dim]📋 Large content detected - processing with enhanced context handling...[/dim]")
        
        # Since the main loop is now async, we can await this directly
        # The process_user_request_enhanced method will handle all modes, including prisma.
        return asyncio.run(self.process_user_request_enhanced(user_input))
    
    async def process_user_request_enhanced(self, user_input: str) -> bool:
        """
        Enhanced request processing with better feedback and error handling.
        This method is now async to properly use the agents.Runner.
        """
        # If in smart mode and no agent selected, determine agent now
        if self.current_mode == "smart":
            suggested_mode, _ = self.mode_manager.detect_optimal_mode(user_input)
            self.mode_manager.switch_mode(suggested_mode)

        if not self.current_agent:
            self.console.print("❌ [red]No processing agent available for this mode. Please select another mode.[/red]")
            self.ui.display_mode_selection()
            return True

        self.messages.append({"role": "user", "content": user_input})
        
        agent_name = self.current_agent.name
        self.console.print(f"\n🤖 [cyan]Processing your request with[/cyan] [bold]{agent_name}[/bold]...")
        
        try:
            # Use the official agents.Runner.run coroutine
            response = await Runner.run(self.current_agent, user_input)

            final_output = response.final_output if response else "Agent did not produce a final output."
            
            # Add assistant message to conversation history
            assistant_message = {"role": "assistant", "content": final_output}
            self.messages.append(assistant_message)
            
            # Display the response
            self.console.print(f"\n🤖 [bold]{agent_name} Response:[/bold]")
            self.console.print("─" * 60)
            self.console.print(Markdown(final_output))
            self.console.print("─" * 60)
            
            self.console.print(f"\n[green]✅ Response generated successfully![/green]")
            self.ui.show_export_options()
            self.ui.provide_contextual_tip()
            
        except Exception as e:
            logger.error(f"Error processing request with agent {agent_name}: {e}", exc_info=True)
            self.console.print(f"❌ [red]Error during processing: {e}[/red]")
            
            # Attempt fallback for Flowise errors
            if "flowise" in self.current_mode and self.user_preferences["auto_fallback"]:
                logger.warning(f"Flowise error triggered fallback. Original error: {e}")
                self.console.print("⚡ [yellow]Flowise API error detected - switching to Prompt fallback.[/yellow]")
                self.mode_manager.switch_mode("prompt")
                if self.current_agent:
                    try:
                        self.console.print(f"🔄 [cyan]Retrying your request with[/cyan] [bold]{self.current_agent.name}[/bold]...")
                        response = await Runner.run(self.current_agent, user_input)
                        
                        final_output = response.final_output if response else "Agent did not produce a final output."
                        assistant_message = {"role": "assistant", "content": final_output}
                        self.messages.append(assistant_message)

                        self.console.print(f"\n🤖 [bold]{self.current_agent.name} (Fallback) Response:[/bold]")
                        self.console.print("─" * 60)
                        self.console.print(Markdown(final_output))
                        self.console.print("─" * 60)
                        self.console.print(f"\n[green]✅ Fallback successful![/green]")
                        self.ui.show_export_options()

                    except Exception as fallback_e:
                        logger.error(f"Fallback to Prompt failed: {fallback_e}", exc_info=True)
                        self.console.print(f"❌ [red]Fallback to Prompt also failed: {fallback_e}[/red]")

        return True

    def handle_transfer_request(self, target_mode: str) -> bool:
        """Handles the /transfer command."""
        if not self.last_user_query:
            self.console.print("[yellow]⚠️ No previous query to transfer. Please ask a question first.[/yellow]")
            return True

        self.console.print(f"🔄 [cyan]Transferring last query to [bold]{target_mode}[/bold] mode...[/cyan]")
        
        # Switch to the new mode
        if not self.mode_manager.switch_mode(target_mode):
            self.console.print(f"[red]❌ Could not switch to mode '{target_mode}'.[/red]")
            return True

        # Re-process the last query
        self.console.print(f"Reprocessing query: \"{self.last_user_query[:100].replace(os.linesep, ' ')}...\"")
        return asyncio.run(self.process_user_request_enhanced(self.last_user_query))

    async def handle_prisma_request(self, user_input: str) -> bool:
        """
        Handle PRISMA systematic review requests.
        Now async to properly call the agent system.
        """
        try:
            if not self.prisma_system:
                self.console.print("[red]❌ PRISMA agent system not available[/red]")
                return True
            
            # Add user message to conversation
            self.messages.append({"role": "user", "content": user_input})
            
            # Get the entry-point agent for the PRISMA system
            prisma_agent = self.prisma_system.get_initial_agent()
            
            # Create the initial prompt for the orchestrator
            # The agent will ask for more details if needed.
            initial_prompt = f"Start a PRISMA systematic review for the following research question: {user_input}"

            self.console.print(f"\n📊 [cyan]Initiating PRISMA systematic review for:[/cyan] {user_input[:100]}...")
            self.console.print("[dim]Using multi-agent framework...[/dim]")
            
            # Run the PRISMA agent system
            response = await Runner.run(prisma_agent, initial_prompt)
            final_output = response.final_output if response else "PRISMA agent did not produce a final output."

            # Handle the response
            self.messages.append({"role": "assistant", "content": final_output})
            self.console.print(f"\n📊 PRISMA System Response")
            self.console.print("─" * 60)
            self.console.print(Markdown(final_output))
            self.console.print("─" * 60)
            
            self.console.print(f"\n[green]✅ PRISMA process step completed![/green]")
            self.ui.show_export_options()
            self.ui.provide_contextual_tip()
            
        except Exception as e:
            logger.error(f"Error in PRISMA request: {e}", exc_info=True)
            self.console.print(f"[red]❌ PRISMA processing error: {e}[/red]")
        
        return True

    def run_enhanced(self) -> None:
        """Main application loop for the enhanced interface."""
        self.ui.display_enhanced_welcome()
        
        # This loop is now synchronous and will call asyncio.run for each input.
        while True:
            try:
                # Use the multiline handler directly for input
                user_input = self.multiline_handler.get_single_or_multiline_input()
                if not self.handle_enhanced_user_input(user_input):
                    break
            except KeyboardInterrupt:
                self.console.print("\n\n[bold yellow]Exiting application.[/bold yellow]")
                break
            except Exception as e:
                logger.error(f"An unexpected error occurred in the main loop: {e}", exc_info=True)
                self.console.print(f"\n[bold red]An unexpected error occurred: {e}[/bold red]")
                self.console.print("[dim]Please check the logs for more details.[/dim]")


# Keep original class for compatibility
class PromptEnhancerApp(EnhancedPromptEnhancerApp):
    """Legacy compatibility class. Will be removed."""
    pass


def main() -> None:
    """Main entry point for the enhanced application."""
    parser = argparse.ArgumentParser(description="Enhanced Multi-Agent Prompt Enhancement Application.")
    parser.add_argument("--mode", type=str, choices=["smart", "prompt", "deep_research", "aeromedical_risk", "aerospace_medicine_rag", "prisma"], default="smart", help="The mode to start the application in.")
    parser.add_argument("--query", type=str, help="If provided, runs a single query in the specified mode and exits.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging.")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        # Validate environment variables
        if not AppConfig.validate_environment():
            sys.exit(1)
        
        # Check chatflow availability
        chatflow_status = AppConfig.validate_chatflow_ids()
        available_chatflows = [name for name, available in chatflow_status.items() if available]
        
        if not available_chatflows:
            print("⚠️  Warning: No Flowise chatflow IDs configured.")
            print("   Some features may not be available.")
            print("   Configure CHATFLOW_* environment variables for full functionality.")
        
        # Create and run the enhanced application
        app = EnhancedPromptEnhancerApp()
        app.mode_manager.switch_mode(args.mode)

        if args.query:
            print(f"Running single query in '{args.mode}' mode...")
            asyncio.run(app.process_user_request_enhanced(args.query))
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