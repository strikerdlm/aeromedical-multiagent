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
from .markdown_exporter import MarkdownExporter
from .prisma_orchestrator import create_prisma_orchestrator, PRISMAOrchestrator


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
        self.markdown_exporter = MarkdownExporter()
        
        # Create both agent systems
        self.o3_agents = create_o3_enhancement_system()
        self.flowise_agents = create_flowise_enhancement_system()
        
        # Initialize PRISMA orchestrator (optional, depends on API availability)
        self.prisma_orchestrator: Optional[PRISMAOrchestrator] = None
        try:
            if AppConfig.validate_prisma_environment():
                self.prisma_orchestrator = create_prisma_orchestrator()
                logger.info("PRISMA orchestrator initialized successfully")
        except Exception as e:
            logger.warning(f"PRISMA orchestrator initialization failed: {e}")
            self.prisma_orchestrator = None
        
        self.messages: List[Dict[str, Any]] = []
        
        # Current processing mode and agent
        self.current_mode: str = "smart"  # "smart", "o3", "flowise", "deepresearch_flowise", "aeromedical_risk", "prisma"
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
        
        # Title - simple text with emoticon
        self.console.print("\n🚀 [bold blue]Advanced Aeromedical Evidence Review System[/bold blue]\n")
        
        # Quick start guide
        self.console.print("🎯 [bold]How to Get Started[/bold]")
        self.console.print("[bold]Just ask your question![/bold] The system will automatically detect the best processing method:")
        self.console.print()
        self.console.print("• [bold]Medical/Aviation Questions[/bold] → Flowise with specialized medical knowledge")
        self.console.print("• [bold]Research/Analysis[/bold] → O3 deep research with web search")
        self.console.print("• [bold]Risk Assessment[/bold] → Aeromedical risk evaluation")
        self.console.print()
        self.console.print("[bold]Pro Tips:[/bold]")
        self.console.print("• Type [bold]?[/bold] for quick help  • [bold]/modes[/bold] to see all modes  • [bold]>>>[/bold] for multiline input")
        self.console.print("• [bold]/history[/bold] to review conversation  • [bold]/clear[/bold] to start fresh")
        self.console.print()
        
        # Available modes - simple text layout
        self.console.print("🛠️ [bold]Available Processing Modes[/bold]")
        self.console.print()
        self.console.print("[cyan]🔬 O3 Research[/cyan]          [green]🌐 Medical RAG[/green]")
        self.console.print("Complex analysis            Clinical questions")
        self.console.print("Latest research             PubMed searches")  
        self.console.print("Technology reviews          Physiology data")
        self.console.print()
        self.console.print("[yellow]🚁 Aero Risk[/yellow]           [magenta]🎯 Smart Mode[/magenta]")
        self.console.print("Flight safety               Auto-detection")
        self.console.print()
        if self.prisma_orchestrator:
            self.console.print("[bright_blue]📊 PRISMA Review[/bright_blue]")
            self.console.print("Systematic reviews          Meta-analyses")
            self.console.print("Evidence synthesis          Research workflows")
        self.console.print("Pilot fitness               Best AI selection")
        self.console.print("Risk assessment             Seamless routing")
        self.console.print()
        
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
        
        self.console.print("📊 [bold]Current Status[/bold]")
        self.console.print(f"Current Mode: {emoji} {mode_name}")
        self.console.print(f"Description: {description}")
        self.console.print(f"Messages: {len(self.messages)}")
        self.console.print("Quick Help: Type ? for help, /modes for mode selection")
        self.console.print()
    
    def display_mode_selection(self) -> None:
        """Display the mode selection interface."""
        self.console.print("🛠️ [bold]Available Processing Modes[/bold]")
        self.console.print()
        
        self.console.print("[cyan]🎯 Smart Auto-Detection[/cyan]")
        self.console.print("   Let the system choose the best AI (Recommended)")
        self.console.print("   Quick Switch: [green]/smart[/green]")
        self.console.print()
        
        self.console.print("[cyan]🔬 O3 Deep Research[/cyan]")
        self.console.print("   Complex analysis, latest research, technology reviews")
        self.console.print("   Quick Switch: [green]/o3[/green]")
        self.console.print()
        
        self.console.print("[cyan]🌐 Flowise Medical RAG[/cyan]")
        self.console.print("   Medical questions, PubMed, clinical knowledge")
        self.console.print("   Quick Switch: [green]/flowise[/green]")
        self.console.print()
        
        self.console.print("[cyan]🔬 DeepResearch RAG[/cyan]")
        self.console.print("   Comprehensive research with deep knowledge synthesis")
        self.console.print("   Quick Switch: [green]/deep[/green]")
        self.console.print()
        
        self.console.print("[cyan]🚁 Aeromedical Risk[/cyan]")
        self.console.print("   Aviation medicine, flight safety, risk assessment")
        self.console.print("   Quick Switch: [green]/aero[/green]")
        self.console.print()
    
    def display_contextual_help(self) -> None:
        """Display contextual help based on current mode."""
        base_commands = [
            ("Your question", "Ask anything - the system will process it"),
            ("?", "Show this help"),
            (">>>", "Enter multiline mode for large text"),
            ("/modes", "Switch processing modes"),
            ("/status", "Show current system status"),
            ("/history", "View conversation history"),
            ("/export", "Export latest response to markdown"),
            ("/save", "Export full conversation to markdown"),
            ("/report", "Export structured research report"),
            ("/exports", "List all exported files"),
            ("/clear", "Clear conversation history"),
            ("/quit", "Exit the application")
        ]
        
        mode_specific = {
            "smart": [
                ("Auto-detection", "System selects best AI based on your question"),
                ("Override", "Use /o3, /flowise, /aero to force specific mode")
            ],
            "o3": [
                ("Best for", "Scientific research, complex analysis, current events"),
                ("Features", "o3-deep-research model with web search capabilities")
            ],
            "flowise": [
                ("Best for", "Medical questions, clinical knowledge, PubMed searches"),
                ("Features", "Specialized medical RAG with multiple knowledge bases")
            ],
            "aeromedical_risk": [
                ("Best for", "Aviation medicine, pilot fitness, flight safety"),
                ("Features", "Conservative risk assessment with safety-first approach")
            ]
        }
        
        # Display help
        self.console.print("📖 [bold]Help & Commands[/bold]")
        self.console.print()
        
        self.console.print("[bold yellow]Commands:[/bold yellow]")
        for cmd, desc in base_commands:
            self.console.print(f"  [bold]{cmd}[/bold] - {desc}")
        
        # Add mode-specific help
        if self.current_mode in mode_specific:
            self.console.print()
            self.console.print(f"[bold yellow]Current Mode ({self.current_mode.title()}):[/bold yellow]")
            for cmd, desc in mode_specific[self.current_mode]:
                self.console.print(f"  [bold]{cmd}[/bold] - {desc}")
        
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
            self.console.print()
            self.console.print("[bold yellow]Example Questions:[/bold yellow]")
            for example in examples[self.current_mode]:
                self.console.print(f"  • '{example}'")
        self.console.print()
    
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
            "aeromedical_risk": self.flowise_agents["aeromedical_risk"],
            "prisma": None  # Special handling for PRISMA
        }
        
        if new_mode not in mode_agents:
            self.console.print(f"[red]❌ Unknown mode: {new_mode}[/red]")
            return False
        
        # Special handling for PRISMA mode
        if new_mode == "prisma":
            if not self.prisma_orchestrator:
                self.console.print("[red]❌ PRISMA mode unavailable - missing API keys or configuration[/red]")
                self.console.print("[yellow]💡 PRISMA requires: OpenAI, Flowise, Perplexity, and Grok API keys[/yellow]")
                return False
        
        old_mode = self.current_mode
        self.current_mode = new_mode
        self.current_agent = mode_agents[new_mode]
        
        mode_names = {
            "smart": "🎯 Smart Auto-Detection",
            "o3": "🔬 O3 Deep Research",
            "flowise": "🌐 Flowise Medical RAG",
            "deepresearch_flowise": "🔬 DeepResearch RAG",
            "aeromedical_risk": "🚁 Aeromedical Risk Assessment",
            "prisma": "📊 PRISMA Systematic Review"
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
            elif command in ['prisma', 'systematic', 'review', 'p']:
                self.switch_mode("prisma")
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
            
            # Export commands
            elif command in ['export', 'save-response']:
                self.export_latest_response()
                return True
            elif command in ['save', 'save-conversation']:
                self.export_full_conversation()
                return True
            elif command in ['report', 'save-report']:
                self.export_structured_report()
                return True
            elif command in ['exports', 'list-exports']:
                self.list_exported_files()
                return True
            
            # PRISMA-specific commands
            elif command in ['prisma-status', 'prisma-info']:
                self.display_prisma_status()
                return True
            elif command in ['prisma-reviews', 'prisma-history']:
                self.display_prisma_reviews()
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
        
        # Special handling for PRISMA mode
        if self.current_mode == "prisma":
            return self.handle_prisma_request(user_input)
        
        if not self.current_agent:
            self.console.print("❌ [red]No processing agent available. Please select a mode first.[/red]")
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
                    
                    # Simple response display without borders
                    mode_info = {
                        "o3": "🔬 O3 Deep Research",
                        "flowise": "🌐 Flowise Medical RAG",
                        "deepresearch_flowise": "🔬 DeepResearch RAG", 
                        "aeromedical_risk": "🚁 Aeromedical Risk Assessment"
                    }
                    
                    title = mode_info.get(self.current_mode, f"🤖 {agent_name}")
                    
                    self.console.print(f"\n{title}")
                    self.console.print("─" * 60)
                    self.console.print(response_content)
                    self.console.print("─" * 60)
            
            # Show success message with helpful next steps
            self.console.print(f"\n[green]✅ Response generated successfully![/green]")
            
            # Show export options
            self.show_export_options()
            
            if self.current_mode == "smart":
                self.console.print("💡 Ask another question or type /modes to explore different processing options")
            else:
                self.console.print(f"💡 Continue in {self.current_mode} mode or type /smart for auto-detection")
            
        except FlowiseAPIError as e:
            logger.error(f"Flowise API error: {e}")
            self.console.print()
            self.console.print("❌ [red]Flowise API Error[/red]")
            self.console.print(f"[red]{e}[/red]")
            self.console.print()
            self.console.print("[yellow]Suggestions:[/yellow]")
            self.console.print("• Check your Flowise API configuration")
            self.console.print("• Verify your internet connection")
            self.console.print("• Try switching to O3 mode with /o3")
            self.console.print()
        except Exception as e:
            logger.error(f"Unexpected error processing request: {e}")
            self.console.print()
            self.console.print("❌ [red]Processing Error[/red]")
            self.console.print(f"[red]{e}[/red]")
            self.console.print()
            self.console.print("[yellow]Suggestions:[/yellow]")
            self.console.print("• Try rephrasing your question")
            self.console.print("• Check the logs for more details")
            self.console.print("• Try a different processing mode")
            self.console.print()
        
        return True
    
    def handle_prisma_request(self, user_input: str) -> bool:
        """
        Handle PRISMA systematic review requests.
        
        Args:
            user_input: The user's research question or topic
            
        Returns:
            True to continue, False to exit
        """
        try:
            if not self.prisma_orchestrator:
                self.console.print("[red]❌ PRISMA orchestrator not available[/red]")
                return True
            
            # Add user message to conversation
            self.messages.append({"role": "user", "content": user_input})
            
            # Enhanced processing feedback
            self.console.print(f"\n📊 [cyan]Initiating PRISMA systematic review for:[/cyan] {user_input[:100]}...")
            self.console.print("[dim]Using multi-agent framework with O3, Perplexity, Grok, and Flowise...[/dim]")
            
            # Create systematic review using the orchestrator
            with self.console.status("[bold green]Conducting comprehensive systematic review..."):
                review_results = self.prisma_orchestrator.quick_prisma_review(user_input)
            
            # Handle the response
            if "error" in review_results:
                self.console.print(f"[red]❌ PRISMA review failed: {review_results['error']}[/red]")
                return True
            
            # Extract and display the systematic review
            systematic_review = review_results.get("systematic_review", "")
            if systematic_review:
                # Add assistant response to conversation
                self.messages.append({"role": "assistant", "content": systematic_review})
                
                # Display the systematic review
                self.console.print(f"\n📊 PRISMA Systematic Review")
                self.console.print("─" * 60)
                self.console.print(systematic_review)
                self.console.print("─" * 60)
                
                # Display metadata
                metadata = review_results.get("workflow_metadata", {})
                word_count = metadata.get("word_count", 0)
                citations = metadata.get("estimated_citations", 0)
                
                self.console.print(f"\n[green]✅ PRISMA systematic review completed![/green]")
                self.console.print(f"📝 Word count: {word_count}")
                self.console.print(f"📚 Estimated citations: {citations}")
                
                # Validation status
                validation = review_results.get("validation_status", {})
                if validation.get("meets_minimum_requirements", False):
                    self.console.print("[green]✅ Meets PRISMA 2020 requirements[/green]")
                else:
                    self.console.print("[yellow]⚠️ May need additional work to meet all PRISMA requirements[/yellow]")
                
                # Show export options
                self.show_export_options()
                self.console.print("📊 /prisma-status - Check PRISMA system status")
                self.console.print("📋 /prisma-reviews - List recent reviews")
                
            else:
                self.console.print("[red]❌ No systematic review content generated[/red]")
            
        except Exception as e:
            logger.error(f"Error in PRISMA request: {e}")
            self.console.print(f"[red]❌ PRISMA processing error: {e}[/red]")
            self.console.print("[yellow]💡 Try a simpler research question or check API configurations[/yellow]")
        
        return True
    
    def display_prisma_status(self) -> None:
        """Display PRISMA system status and capabilities."""
        try:
            if not self.prisma_orchestrator:
                self.console.print("📊 [bold]PRISMA System Status[/bold]")
                self.console.print("[red]❌ PRISMA orchestrator not initialized[/red]")
                self.console.print()
                self.console.print("PRISMA requires the following API keys:")
                self.console.print("• OpenAI API key (OPENAI_API_KEY)")
                self.console.print("• Flowise API key (FLOWISE_API_KEY)")
                self.console.print("• Perplexity API key (PPLX_API_KEY)")
                self.console.print("• Grok API key (XAI_API)")
                self.console.print()
                return
            
            # Get system status
            status = self.prisma_orchestrator.get_prisma_status()
            
            self.console.print("📊 [bold]PRISMA System Status[/bold]")
            self.console.print()
            
            # API connectivity
            api_status = status.get("api_connectivity", {})
            self.console.print("[bold]API Connectivity:[/bold]")
            for api_name, api_info in api_status.items():
                api_status_text = api_info.get("status", "unknown")
                if api_status_text == "connected":
                    self.console.print(f"  ✅ {api_name.title()}: Connected")
                elif api_status_text == "configured":
                    self.console.print(f"  ⚙️ {api_name.title()}: Configured")
                else:
                    self.console.print(f"  ❌ {api_name.title()}: {api_status_text}")
            self.console.print()
            
            # Capabilities
            capabilities = status.get("capabilities", {})
            models = capabilities.get("models_available", {})
            self.console.print("[bold]Available Models:[/bold]")
            for model_type, model_name in models.items():
                self.console.print(f"  • {model_type.replace('_', ' ').title()}: {model_name}")
            self.console.print()
            
            # Target specifications
            specs = capabilities.get("target_specifications", {})
            self.console.print("[bold]PRISMA Specifications:[/bold]")
            for spec_name, spec_value in specs.items():
                self.console.print(f"  • {spec_name.replace('_', ' ').title()}: {spec_value}")
            self.console.print()
            
            # Workflow phases
            phases = capabilities.get("workflow_phases", [])
            self.console.print("[bold]Workflow Phases:[/bold]")
            for phase in phases:
                self.console.print(f"  • {phase}")
            self.console.print()
            
            # Session information
            session_count = status.get("session_history_count", 0)
            self.console.print(f"[bold]Session Information:[/bold]")
            self.console.print(f"  • Reviews completed: {session_count}")
            self.console.print(f"  • Current workflow: {'Active' if status.get('current_workflow_active') else 'None'}")
            self.console.print()
            
        except Exception as e:
            logger.error(f"Error displaying PRISMA status: {e}")
            self.console.print(f"[red]❌ Error getting PRISMA status: {e}[/red]")
    
    def display_prisma_reviews(self) -> None:
        """Display recent PRISMA reviews."""
        try:
            if not self.prisma_orchestrator:
                self.console.print("[red]❌ PRISMA orchestrator not available[/red]")
                return
            
            # Get recent reviews
            reviews = self.prisma_orchestrator.list_recent_reviews(limit=10)
            
            if not reviews:
                self.console.print("📋 [bold]Recent PRISMA Reviews[/bold]")
                self.console.print("[yellow]No PRISMA reviews found in current session.[/yellow]")
                self.console.print()
                self.console.print("Use `/prisma` mode to create systematic reviews.")
                self.console.print()
                return
            
            self.console.print(f"📋 [bold]Recent PRISMA Reviews[/bold] ({len(reviews)} total)")
            self.console.print()
            
            for i, review in enumerate(reviews, 1):
                session_id = review.get("session_id", "unknown")
                question = review.get("research_question", "No question")
                word_count = review.get("word_count", 0)
                citations = review.get("estimated_citations", 0)
                status_val = review.get("status", "unknown")
                
                # Display review summary
                self.console.print(f"[cyan]{i}. {question[:80]}{'...' if len(question) > 80 else ''}[/cyan]")
                self.console.print(f"   Session: {session_id}")
                self.console.print(f"   Status: {status_val} | Words: {word_count} | Citations: {citations}")
                
                # Validation info
                validation = review.get("validation_status", {})
                if validation.get("meets_minimum_requirements"):
                    self.console.print("   [green]✅ Meets PRISMA requirements[/green]")
                else:
                    self.console.print("   [yellow]⚠️ May need improvements[/yellow]")
                
                self.console.print()
            
            self.console.print("💡 Use `/export` to save reviews or `/prisma-status` for system information.")
            self.console.print()
            
        except Exception as e:
            logger.error(f"Error displaying PRISMA reviews: {e}")
            self.console.print(f"[red]❌ Error getting PRISMA reviews: {e}[/red]")
    
    def display_conversation_history(self) -> None:
        """Enhanced conversation history display."""
        if not self.messages:
            self.console.print("💭 [yellow]No conversation history yet. Start by asking a question![/yellow]")
            return
        
        self.console.print(f"📜 [bold]Conversation History[/bold] ({len(self.messages)} messages)")
        self.console.print()
        
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
        self.console.print()

    def display_settings(self) -> None:
        """Display and allow modification of user settings."""
        self.console.print("⚙️ [bold]User Settings[/bold]")
        self.console.print()
        
        self.console.print("[cyan]Auto-suggest modes[/cyan]")
        self.console.print(f"  Current: {'✅ Enabled' if self.user_preferences['auto_suggest'] else '❌ Disabled'}")
        self.console.print("  Description: Automatically suggest optimal processing modes")
        self.console.print()
        
        self.console.print("[cyan]Show tips[/cyan]")
        self.console.print(f"  Current: {'✅ Enabled' if self.user_preferences['show_tips'] else '❌ Disabled'}")
        self.console.print("  Description: Show helpful tips and context")
        self.console.print()
        
        self.console.print("[cyan]Confirm mode switches[/cyan]")
        self.console.print(f"  Current: {'✅ Enabled' if self.user_preferences['confirm_mode_switch'] else '❌ Disabled'}")
        self.console.print("  Description: Ask before automatically switching modes")
        self.console.print()
        
        self.console.print("Settings modification coming in future update. Type /help for available commands.")
        self.console.print()

    def export_latest_response(self) -> None:
        """Export the latest response to a markdown file."""
        try:
            if not self.messages:
                self.console.print("⚠️ [yellow]No conversation to export. Ask a question first![/yellow]")
                return
            
            # Check if there's at least one assistant response
            has_response = any(msg.get("role") == "assistant" for msg in self.messages)
            if not has_response:
                self.console.print("⚠️ [yellow]No AI response found to export.[/yellow]")
                return
            
            agent_name = self.current_agent.name if self.current_agent else "Unknown"
            
            file_path = self.markdown_exporter.export_latest_response(
                self.messages, self.current_mode, agent_name
            )
            
            self.console.print()
            self.console.print("📄 [green]Export Complete[/green]")
            self.console.print(f"[green]✅ Latest response exported successfully![/green]")
            self.console.print()
            self.console.print(f"[bold]File:[/bold] `{file_path}`")
            self.console.print(f"[bold]Location:[/bold] `{self.markdown_exporter.get_export_directory()}`")
            self.console.print()
            self.console.print("💡 You can now share this markdown file or import it into your documentation.")
            self.console.print()
            
        except Exception as e:
            logger.error(f"Error exporting latest response: {e}")
            self.console.print(f"❌ [red]Export failed: {e}[/red]")

    def export_full_conversation(self) -> None:
        """Export the complete conversation to a markdown file."""
        try:
            if not self.messages:
                self.console.print("⚠️ [yellow]No conversation to export. Ask a question first![/yellow]")
                return
            
            agent_name = self.current_agent.name if self.current_agent else "Unknown"
            
            file_path = self.markdown_exporter.export_full_conversation(
                self.messages, self.current_mode, agent_name
            )
            
            self.console.print()
            self.console.print("📚 [green]Conversation Export Complete[/green]")
            self.console.print(f"[green]✅ Full conversation exported successfully![/green]")
            self.console.print()
            self.console.print(f"[bold]File:[/bold] `{file_path}`")
            self.console.print(f"[bold]Messages:[/bold] {len(self.messages)}")
            self.console.print(f"[bold]Location:[/bold] `{self.markdown_exporter.get_export_directory()}`")
            self.console.print()
            self.console.print("💡 This includes all questions and responses from your current session.")
            self.console.print()
            
        except Exception as e:
            logger.error(f"Error exporting conversation: {e}")
            self.console.print(f"❌ [red]Export failed: {e}[/red]")

    def export_structured_report(self) -> None:
        """Export a structured research report."""
        try:
            if not self.messages:
                self.console.print("⚠️ [yellow]No conversation to export. Ask a question first![/yellow]")
                return
            
            # Ask for optional title
            title = Prompt.ask(
                "\n📝 [cyan]Report title (optional)[/cyan]",
                default="",
                show_default=False
            )
            
            agent_name = self.current_agent.name if self.current_agent else "Unknown"
            
            file_path = self.markdown_exporter.export_structured_report(
                self.messages, self.current_mode, agent_name, 
                title if title.strip() else None
            )
            
            self.console.print()
            self.console.print("📊 [green]Research Report Export Complete[/green]")
            self.console.print(f"[green]✅ Research report exported successfully![/green]")
            self.console.print()
            self.console.print(f"[bold]File:[/bold] `{file_path}`")
            self.console.print(f"[bold]Format:[/bold] Structured research report with metadata")
            self.console.print(f"[bold]Location:[/bold] `{self.markdown_exporter.get_export_directory()}`")
            self.console.print()
            self.console.print("💡 This report includes executive summary, questions, and detailed analysis.")
            self.console.print()
            
        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            self.console.print(f"❌ [red]Export failed: {e}[/red]")

    def list_exported_files(self) -> None:
        """List all exported markdown files."""
        try:
            exports = self.markdown_exporter.list_exports()
            
            if not exports:
                self.console.print()
                self.console.print("📁 [yellow]Exported Files[/yellow]")
                self.console.print("[yellow]No exported files found.[/yellow]")
                self.console.print()
                self.console.print("Use `/export`, `/save`, or `/report` to create markdown exports.")
                self.console.print()
                return
            
            # Display exports as simple text
            self.console.print()
            self.console.print(f"📁 [bold]Exported Files[/bold] ({len(exports)} total)")
            self.console.print()
            
            for filename, filepath, modified_time in exports:
                # Determine type based on filename
                if filename.startswith("response_"):
                    file_type = "📄 Response"
                elif filename.startswith("conversation_"):
                    file_type = "📚 Conversation"
                elif filename.startswith("report_"):
                    file_type = "📊 Report"
                else:
                    file_type = "📎 Export"
                
                modified_str = modified_time.strftime("%Y-%m-%d %H:%M")
                
                self.console.print(f"[cyan]{file_type}[/cyan] - {filename}")
                self.console.print(f"  Modified: {modified_str}")
                self.console.print(f"  Path: {filepath}")
                self.console.print()
            
            self.console.print(f"💡 Export directory: `{self.markdown_exporter.get_export_directory()}`")
            self.console.print()
            
        except Exception as e:
            logger.error(f"Error listing exports: {e}")
            self.console.print(f"❌ [red]Failed to list exports: {e}[/red]")

    def show_export_options(self) -> None:
        """Show export options after a response is generated."""
        self.console.print()
        self.console.print("💾 [bold]Export Options[/bold]")
        self.console.print("📄 /export - Save this response to markdown")
        self.console.print("📚 /save - Save full conversation to markdown")
        self.console.print("📊 /report - Create structured research report")
        self.console.print()

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
                    self.console.print("\n👋 [yellow]Goodbye! Thanks for using the Aeromedical Evidence Review System![/yellow]")
                    break
                
                # Handle the input
                should_continue = self.handle_enhanced_user_input(user_input)
                if not should_continue:
                    break
            
        except Exception as e:
            logger.error(f"Fatal error in enhanced main loop: {e}")
            self.console.print()
            self.console.print("💥 [red]Critical Error[/red]")
            self.console.print(f"[red]Fatal Error:[/red] {e}")
            self.console.print()
            self.console.print("The application encountered an unexpected error and needs to close.")
            self.console.print("Please check the logs for more details.")
            self.console.print()
        finally:
            self.console.print("\n✨ [bold blue]Thank you for using the Enhanced Aeromedical Evidence Review System![/bold blue]")
            self.console.print("Your research makes aviation safer. Keep up the great work!")


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