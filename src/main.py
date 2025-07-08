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
from typing import Dict, Any, List, Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
# Remove problematic imports and use simpler Rich components

from .config import AppConfig
from .agents import AgentOrchestrator
from .o3_agents import create_o3_enhancement_system
from .flowise_agents import create_flowise_enhancement_system
from .flowise_client import FlowiseAPIError
from .multiline_input import MultilineInputHandler, detect_paste_input, format_large_text_preview


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
        self.orchestrator = AgentOrchestrator()
        
        # Create both agent systems
        self.o3_agents = create_o3_enhancement_system()
        self.flowise_agents = create_flowise_enhancement_system()
        
        self.messages: List[Dict[str, Any]] = []
        
        # Current processing mode and agent
        self.current_mode: str = "smart"  # "smart", "o3", "flowise", "deepresearch_flowise", "aeromedical_risk"
        self.current_agent = None
        self.user_preferences = {
            "auto_suggest": True,
            "show_tips": True,
            "confirm_mode_switch": False
        }
        
        # Smart mode detection patterns
        self.mode_patterns = {
            "o3": [
                r"quantum|technology|latest|recent|current|compare|analysis|research|explain.*how",
                r"artificial intelligence|AI|machine learning|deep learning",
                r"what.*latest|recent.*development|current.*state",
                r"explain.*detail|comprehensive.*analysis|in-depth"
            ],
            "flowise": [
                r"medical|physiology|clinical|health|treatment|therapy|diagnosis",
                r"NASA|space|microgravity|aerospace|flight|aviation",
                r"cardiovascular|respiratory|neurological|psychological",
                r"pubmed|literature|journal|study|research.*paper"
            ],
            "aeromedical_risk": [
                r"pilot|flight.*safety|aviation.*medicine|aeromedical",
                r"risk.*assessment|medical.*fitness|flight.*physical",
                r"commercial.*pilot|airline|FAA|aviation.*regulation",
                r"altitude.*sickness|hypoxia|G-force|aerospace.*physiology"
            ]
        }
        
        logger.info("Enhanced Prompt Enhancer App initialized successfully")
    
    def detect_optimal_mode(self, query: str) -> Tuple[str, float]:
        """
        Detect the optimal processing mode based on query content.
        
        Args:
            query: User's query text
            
        Returns:
            Tuple of (suggested_mode, confidence_score)
        """
        query_lower = query.lower()
        mode_scores = {}
        
        for mode, patterns in self.mode_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query_lower))
                score += matches * 2  # Weight each match
                
                # Bonus for exact phrase matches
                if pattern in query_lower:
                    score += 1
            
            mode_scores[mode] = score
        
        # Find the best match
        if mode_scores:
            best_mode = max(mode_scores.keys(), key=lambda x: mode_scores[x])
            max_score = mode_scores[best_mode]
            
            # Normalize confidence (rough heuristic)
            confidence = min(max_score / 5.0, 1.0)
            
            if confidence > 0.3:  # Minimum confidence threshold
                return best_mode, confidence
        
        # Default to flowise for medical/scientific queries, o3 for general
        if any(term in query_lower for term in ["medical", "health", "physiology", "clinical"]):
            return "flowise", 0.6
        else:
            return "o3", 0.5
    
    def display_enhanced_welcome(self) -> None:
        """Display an enhanced welcome message with better onboarding."""
        
        # Title panel
        title_text = "🚀 Advanced Aeromedical Evidence Review System"
        title_panel = Panel(
            Text(title_text, style="bold blue", justify="center"),
            border_style="bright_blue",
            padding=(1, 2)
        )
        
        # Quick start guide
        quick_start = """
        ## 🎯 How to Get Started

        **Just ask your question!** The system will automatically detect the best processing method:

        • **Medical/Aviation Questions** → Flowise with specialized medical knowledge
        • **Research/Analysis** → O3 deep research with web search
        • **Risk Assessment** → Aeromedical risk evaluation
        
        **Pro Tips:**
        • Type **`?`** for quick help  • **`/modes`** to see all modes  • **`>>>`** for multiline input
        • **`/history`** to review conversation  • **`/clear`** to start fresh
        """
        
        # Available modes table
        modes_table = Table.grid(padding=1)
        modes_table.add_column(style="cyan")
        modes_table.add_column(style="green")
        modes_table.add_column(style="yellow") 
        modes_table.add_column(style="magenta")
        
        modes_table.add_row(
            "🔬 O3 Research\nComplex analysis\nLatest research\nTechnology reviews",
            "🌐 Medical RAG\nClinical questions\nPubMed searches\nPhysiology data", 
            "🚁 Aero Risk\nFlight safety\nPilot fitness\nRisk assessment",
            "🎯 Smart Mode\nAuto-detection\nBest AI selection\nSeamless routing"
        )
        
        # Display all panels
        self.console.print(title_panel)
        self.console.print(Panel(Markdown(quick_start), title="🚀 Quick Start", border_style="green"))
        self.console.print(Panel(modes_table, title="🛠️ Available Processing Modes", border_style="cyan"))
        
        # Current status
        self.display_current_status()
    
    def display_current_status(self) -> None:
        """Display current system status and available options."""
        mode_info = {
            "smart": ("🎯", "Smart Auto-Detection", "System automatically selects best AI"),
            "o3": ("🔬", "O3 Deep Research", "Complex analysis and reasoning"),
            "flowise": ("🌐", "Flowise Medical RAG", "Medical and scientific knowledge"),
            "deepresearch_flowise": ("🔬", "DeepResearch RAG", "Comprehensive research synthesis"),
            "aeromedical_risk": ("🚁", "Aeromedical Risk", "Aviation medicine assessment")
        }
        
        emoji, mode_name, description = mode_info.get(self.current_mode, ("❓", "Unknown", "Unknown mode"))
        
        status_table = Table.grid(padding=1)
        status_table.add_column(style="cyan", justify="right")
        status_table.add_column(style="white")
        
        status_table.add_row("Current Mode:", f"{emoji} {mode_name}")
        status_table.add_row("Description:", description)
        status_table.add_row("Messages:", str(len(self.messages)))
        status_table.add_row("Quick Help:", "Type ? for help, /modes for mode selection")
        
        self.console.print(Panel(status_table, title="📊 Current Status", border_style="blue", padding=(0, 1)))
    
    def display_mode_selection(self) -> None:
        """Display the mode selection interface."""
        modes_table = Table(title="🛠️ Available Processing Modes")
        modes_table.add_column("Mode", style="cyan", width=20)
        modes_table.add_column("Best For", style="yellow", width=40)
        modes_table.add_column("Quick Switch", style="green", width=15)
        
        modes_table.add_row(
            "🎯 Smart Auto-Detection", 
            "Let the system choose the best AI (Recommended)", 
            "/smart"
        )
        modes_table.add_row(
            "🔬 O3 Deep Research", 
            "Complex analysis, latest research, technology reviews", 
            "/o3"
        )
        modes_table.add_row(
            "🌐 Flowise Medical RAG", 
            "Medical questions, PubMed, clinical knowledge", 
            "/flowise"
        )
        modes_table.add_row(
            "🔬 DeepResearch RAG", 
            "Comprehensive research with deep knowledge synthesis", 
            "/deep"
        )
        modes_table.add_row(
            "🚁 Aeromedical Risk", 
            "Aviation medicine, flight safety, risk assessment", 
            "/aero"
        )
        
        self.console.print(modes_table)
    
    def display_contextual_help(self) -> None:
        """Display contextual help based on current mode."""
        base_commands = [
            ("**Your question**", "Ask anything - the system will process it"),
            ("**`?`**", "Show this help"),
            ("**`>>>`**", "Enter multiline mode for large text"),
            ("**`/modes`**", "Switch processing modes"),
            ("**`/status`**", "Show current system status"),
            ("**`/history`**", "View conversation history"),
            ("**`/clear`**", "Clear conversation history"),
            ("**`/quit`**", "Exit the application")
        ]
        
        mode_specific = {
            "smart": [
                ("**Auto-detection**", "System selects best AI based on your question"),
                ("**Override**", "Use /o3, /flowise, /aero to force specific mode")
            ],
            "o3": [
                ("**Best for**", "Scientific research, complex analysis, current events"),
                ("**Features**", "o3-deep-research model with web search capabilities")
            ],
            "flowise": [
                ("**Best for**", "Medical questions, clinical knowledge, PubMed searches"),
                ("**Features**", "Specialized medical RAG with multiple knowledge bases")
            ],
            "aeromedical_risk": [
                ("**Best for**", "Aviation medicine, pilot fitness, flight safety"),
                ("**Features**", "Conservative risk assessment with safety-first approach")
            ]
        }
        
        # Create help table
        help_table = Table.grid(padding=1)
        help_table.add_column(style="cyan", justify="right")
        help_table.add_column(style="white")
        
        # Add base commands
        help_table.add_row("[bold yellow]Commands:[/bold yellow]", "")
        for cmd, desc in base_commands:
            help_table.add_row(cmd, desc)
        
        # Add mode-specific help
        if self.current_mode in mode_specific:
            help_table.add_row("", "")
            help_table.add_row(f"[bold yellow]Current Mode ({self.current_mode.title()}):[/bold yellow]", "")
            for cmd, desc in mode_specific[self.current_mode]:
                help_table.add_row(cmd, desc)
        
        # Quick examples
        examples = {
            "smart": [
                "What are the cardiovascular effects of microgravity?",
                "Latest developments in AI for medical diagnosis",
                "Risk factors for pilots with diabetes"
            ],
            "o3": [
                "Explain quantum computing applications in cryptography",
                "Compare latest renewable energy technologies",
                "Analyze current developments in space exploration"
            ],
            "flowise": [
                "Physiological changes during long-duration spaceflight",
                "Recent research on pilot fatigue mitigation",
                "Clinical guidelines for aviation medical examinations"
            ],
            "aeromedical_risk": [
                "Cardiovascular risk factors for commercial pilots",
                "Medical fitness requirements for high-altitude operations",
                "Assessment of medication effects on flight safety"
            ]
        }
        
        if self.current_mode in examples:
            help_table.add_row("", "")
            help_table.add_row("[bold yellow]Example Questions:[/bold yellow]", "")
            for example in examples[self.current_mode]:
                help_table.add_row("•", f"'{example}'")
        
        self.console.print(Panel(help_table, title="📖 Help & Commands", border_style="yellow"))
    
    def get_user_input_enhanced(self) -> str:
        """
        Enhanced user input with smart prompting and mode awareness.
        
        Returns:
            The user's input string
        """
        # Dynamic prompt based on mode
        mode_prompts = {
            "smart": "🎯 Ask your question (auto-detection enabled)",
            "o3": "🔬 Enter your research question",
            "flowise": "🌐 Enter your medical/scientific question",
            "deepresearch_flowise": "🔬 Enter your research query",
            "aeromedical_risk": "🚁 Enter your aeromedical question"
        }
        
        prompt_text = mode_prompts.get(self.current_mode, "💬 Enter your question")
        
        # Show helpful context
        if self.current_mode == "smart" and self.user_preferences["show_tips"]:
            self.console.print("[dim]💡 Tip: The system will analyze your question and select the optimal AI model[/dim]")
        
        # Use the multiline input handler
        user_input = self.multiline_handler.get_single_or_multiline_input(
            prompt_text=prompt_text,
            mode_emoji=""  # We include emoji in the prompt text
        )
        
        return user_input.strip()
    
    def handle_smart_mode_detection(self, user_input: str) -> bool:
        """
        Handle smart mode detection and suggestion.
        
        Args:
            user_input: The user's input
            
        Returns:
            True if mode was changed, False otherwise
        """
        if self.current_mode != "smart":
            return False
        
        suggested_mode, confidence = self.detect_optimal_mode(user_input)
        
        if confidence > 0.6 and self.user_preferences["auto_suggest"]:
            # High confidence - suggest mode switch
            mode_names = {
                "o3": "🔬 O3 Deep Research",
                "flowise": "🌐 Flowise Medical RAG", 
                "aeromedical_risk": "🚁 Aeromedical Risk Assessment"
            }
            
            mode_name = mode_names.get(suggested_mode, suggested_mode)
            
            if self.user_preferences["confirm_mode_switch"]:
                # Ask for confirmation
                should_switch = Confirm.ask(
                    f"[yellow]💡 Your question seems perfect for {mode_name} (confidence: {confidence:.1%}). Switch to this mode?[/yellow]",
                    default=True
                )
                
                if should_switch:
                    self.switch_mode(suggested_mode)
                    return True
            else:
                # Auto-switch with notification
                self.console.print(f"[green]🎯 Auto-detected optimal mode: {mode_name} (confidence: {confidence:.1%})[/green]")
                self.switch_mode(suggested_mode)
                return True
        
        return False
    
    def switch_mode(self, new_mode: str) -> bool:
        """
        Switch to a new processing mode.
        
        Args:
            new_mode: The mode to switch to
            
        Returns:
            True if successful, False otherwise
        """
        mode_agents = {
            "smart": None,
            "o3": self.o3_agents["o3_enhancer"],
            "flowise": self.flowise_agents["flowise_enhancer"],
            "deepresearch_flowise": self.flowise_agents["deep_research"],
            "aeromedical_risk": self.flowise_agents["aeromedical_risk"]
        }
        
        if new_mode not in mode_agents:
            self.console.print(f"[red]❌ Unknown mode: {new_mode}[/red]")
            return False
        
        old_mode = self.current_mode
        self.current_mode = new_mode
        self.current_agent = mode_agents[new_mode]
        
        mode_names = {
            "smart": "🎯 Smart Auto-Detection",
            "o3": "🔬 O3 Deep Research",
            "flowise": "🌐 Flowise Medical RAG",
            "deepresearch_flowise": "🔬 DeepResearch RAG",
            "aeromedical_risk": "🚁 Aeromedical Risk Assessment"
        }
        
        if old_mode != new_mode:
            mode_name = mode_names.get(new_mode, new_mode)
            self.console.print(f"[green]✅ Switched to {mode_name}[/green]")
        
        return True
    
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
            self.display_contextual_help()
            return True
        
        # Handle commands
        if user_input.startswith('/'):
            command = user_input[1:].lower()
            
            # Exit commands
            if command in ['quit', 'exit', 'q']:
                return False
            
            # Mode switching commands
            elif command in ['smart', 's']:
                self.switch_mode("smart")
                return True
            elif command in ['o3', 'research']:
                self.switch_mode("o3")
                return True
            elif command in ['flowise', 'medical', 'f']:
                self.switch_mode("flowise")
                return True
            elif command in ['deep', 'deepresearch', 'd']:
                self.switch_mode("deepresearch_flowise")
                return True
            elif command in ['aero', 'aeromedical', 'risk', 'a']:
                self.switch_mode("aeromedical_risk")
                return True
            
            # Information commands
            elif command in ['modes', 'mode', 'm']:
                self.display_mode_selection()
                return True
            elif command in ['help', 'h']:
                self.display_contextual_help()
                return True
            elif command in ['status', 'stat']:
                self.display_current_status()
                return True
            elif command in ['history', 'hist']:
                self.display_conversation_history()
                return True
            elif command in ['clear', 'reset', 'c']:
                self.messages = []
                self.console.print("🧹 [green]Conversation history cleared.[/green]")
                return True
            
            # Settings commands
            elif command in ['settings', 'config']:
                self.display_settings()
                return True
            
            else:
                self.console.print(f"[red]❌ Unknown command: /{command}[/red]")
                self.console.print("[yellow]💡 Type ? for help or /modes to see available modes[/yellow]")
                return True
        
        # Handle empty input
        if not user_input:
            self.console.print("[yellow]💬 Please enter a question or command. Type ? for help.[/yellow]")
            return True
        
        # Smart mode detection
        mode_changed = self.handle_smart_mode_detection(user_input)
        
        # Check if this looks like pasted content
        if detect_paste_input(user_input):
            self.console.print("[dim]📋 Large content detected - processing with enhanced context handling...[/dim]")
        
        return self.process_user_request_enhanced(user_input)
    
    def process_user_request_enhanced(self, user_input: str) -> bool:
        """
        Enhanced request processing with better feedback and error handling.
        
        Args:
            user_input: The user's request
            
        Returns:
            True to continue, False to exit
        """
        # If in smart mode and no agent selected, use default
        if self.current_mode == "smart" and not self.current_agent:
            # Default to flowise for medical content, o3 for general
            suggested_mode, _ = self.detect_optimal_mode(user_input)
            self.switch_mode(suggested_mode)
        
        if not self.current_agent:
            self.console.print("[red]❌ No processing agent available. Please select a mode first.[/red]")
            self.display_mode_selection()
            return True
        
        try:
            # Add user message to conversation
            self.messages.append({"role": "user", "content": user_input})
            
            # Enhanced processing feedback
            agent_name = self.current_agent.name
            mode_emoji = {
                "o3": "🔬",
                "flowise": "🌐", 
                "deepresearch_flowise": "🔬",
                "aeromedical_risk": "🚁"
            }.get(self.current_mode, "🤖")
            
            if len(user_input) > 500:
                lines = len(user_input.split('\n'))
                words = len(user_input.split())
                self.console.print(f"\n{mode_emoji} [cyan]Processing your request[/cyan] ({lines} lines, {words} words) with [bold]{agent_name}[/bold]...")
            else:
                self.console.print(f"\n{mode_emoji} [cyan]Processing your request with[/cyan] [bold]{agent_name}[/bold]...")
            
            # Execute the current agent with progress indication
            with self.console.status("[bold green]Analyzing and generating response..."):
                response = self.orchestrator.run_full_turn(self.current_agent, self.messages)
            
            # Update current agent and messages
            if response.agent:
                self.current_agent = response.agent
            self.messages.extend(response.messages)
            
            # Display the response with enhanced formatting
            if response.messages:
                last_message = response.messages[-1]
                if last_message.get("role") == "assistant" and last_message.get("content"):
                    response_content = last_message["content"]
                    
                    # Create response panel with mode indicator
                    mode_info = {
                        "o3": "🔬 O3 Deep Research",
                        "flowise": "🌐 Flowise Medical RAG",
                        "deepresearch_flowise": "🔬 DeepResearch RAG", 
                        "aeromedical_risk": "🚁 Aeromedical Risk Assessment"
                    }
                    
                    title = mode_info.get(self.current_mode, f"🤖 {agent_name}")
                    
                    self.console.print(Panel(
                        response_content,
                        title=title,
                        border_style="green",
                        padding=(1, 2)
                    ))
            
            # Show success message with helpful next steps
            self.console.print(f"\n[green]✅ Response generated successfully![/green]")
            
            if self.current_mode == "smart":
                self.console.print("[dim]💡 Ask another question or type /modes to explore different processing options[/dim]")
            else:
                self.console.print(f"[dim]💡 Continue in {self.current_mode} mode or type /smart for auto-detection[/dim]")
            
        except FlowiseAPIError as e:
            logger.error(f"Flowise API error: {e}")
            self.console.print(Panel(
                f"[red]Flowise API Error:[/red] {e}\n\n"
                "[yellow]Suggestions:[/yellow]\n"
                "• Check your Flowise API configuration\n"
                "• Verify your internet connection\n"
                "• Try switching to O3 mode with /o3",
                title="❌ API Error",
                border_style="red"
            ))
        except Exception as e:
            logger.error(f"Unexpected error processing request: {e}")
            self.console.print(Panel(
                f"[red]Unexpected Error:[/red] {e}\n\n"
                "[yellow]Suggestions:[/yellow]\n"
                "• Try rephrasing your question\n"
                "• Check the logs for more details\n"
                "• Try a different processing mode",
                title="❌ Processing Error", 
                border_style="red"
            ))
        
        return True
    
    def display_conversation_history(self) -> None:
        """Enhanced conversation history display."""
        if not self.messages:
            self.console.print("💭 [yellow]No conversation history yet. Start by asking a question![/yellow]")
            return
        
        self.console.print(Panel(f"📜 Conversation History ({len(self.messages)} messages)", border_style="magenta"))
        
        for i, message in enumerate(self.messages):
            role = message.get("role", "unknown")
            content = message.get("content", "")
            
            if role == "user":
                # Show preview for long content
                if len(content) > 200:
                    preview = format_large_text_preview(content, max_lines=3, max_chars=200)
                    self.console.print(f"[bold blue]🧑 You:[/bold blue] {preview}")
                else:
                    self.console.print(f"[bold blue]🧑 You:[/bold blue] {content}")
            elif role == "assistant":
                if len(content) > 200:
                    preview = format_large_text_preview(content, max_lines=3, max_chars=200)
                    self.console.print(f"[bold green]🤖 Assistant:[/bold green] {preview}")
                else:
                    self.console.print(f"[bold green]🤖 Assistant:[/bold green] {content}")
            elif role == "tool":
                self.console.print(f"[bold yellow]🔧 Tool:[/bold yellow] {content[:100]}...")
            
            if i < len(self.messages) - 1:
                self.console.print("[dim]" + "─" * 50 + "[/dim]")
    
    def display_settings(self) -> None:
        """Display and allow modification of user settings."""
        settings_table = Table(title="⚙️ User Settings")
        settings_table.add_column("Setting", style="cyan")
        settings_table.add_column("Current Value", style="green")
        settings_table.add_column("Description", style="yellow")
        
        settings_table.add_row(
            "Auto-suggest modes", 
            "✅ Enabled" if self.user_preferences["auto_suggest"] else "❌ Disabled",
            "Automatically suggest optimal processing modes"
        )
        settings_table.add_row(
            "Show tips", 
            "✅ Enabled" if self.user_preferences["show_tips"] else "❌ Disabled",
            "Show helpful tips and context"
        )
        settings_table.add_row(
            "Confirm mode switches", 
            "✅ Enabled" if self.user_preferences["confirm_mode_switch"] else "❌ Disabled",
            "Ask before automatically switching modes"
        )
        
        self.console.print(settings_table)
        self.console.print("\n[dim]Settings modification coming in future update. Type /help for available commands.[/dim]")
    
    def run_enhanced(self) -> None:
        """Run the enhanced application with improved user experience."""
        try:
            # Show enhanced welcome
            self.display_enhanced_welcome()
            
            # Main interaction loop
            while True:
                try:
                    user_input = self.get_user_input_enhanced()
                except (KeyboardInterrupt, EOFError):
                    self.console.print("\n[yellow]👋 Goodbye! Thanks for using the Aeromedical Evidence Review System![/yellow]")
                    break
                
                # Handle the input
                should_continue = self.handle_enhanced_user_input(user_input)
                if not should_continue:
                    break
            
        except Exception as e:
            logger.error(f"Fatal error in enhanced main loop: {e}")
            self.console.print(Panel(
                f"[red]Fatal Error:[/red] {e}\n\n"
                "The application encountered an unexpected error and needs to close.\n"
                "Please check the logs for more details.",
                title="💥 Critical Error",
                border_style="red"
            ))
        finally:
            self.console.print("\n[bold blue]✨ Thank you for using the Enhanced Aeromedical Evidence Review System![/bold blue]")
            self.console.print("[dim]Your research makes aviation safer. Keep up the great work![/dim]")


# Keep original class for compatibility
class PromptEnhancerApp(EnhancedPromptEnhancerApp):
    """Compatibility wrapper for the original class name."""
    pass


def main() -> None:
    """Main entry point for the enhanced application."""
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
        app.run_enhanced()
        
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user.")
    except Exception as e:
        logger.error(f"Fatal application error: {e}")
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 