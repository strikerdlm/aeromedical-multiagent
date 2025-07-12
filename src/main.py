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
from .custom_rich import Console, Panel, Table, Text, Prompt, Confirm, Markdown
from rich.console import Console as RichConsole
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.live import Live
from pydantic import BaseModel
from agents import Runner

from .config import AppConfig
from .prompt_agents import create_prompt_enhancement_system
from .flowise_agents import create_flowise_enhancement_system
from .flowise_client import FlowiseAPIError
from .multiline_input import MultilineInputHandler, detect_paste_input, format_large_text_preview
from .markdown_exporter import MarkdownExporter
from .prisma_agents import PRISMAAgentSystem, create_prisma_agent_system


class ProgressTracker:
    """
    Progress tracking system following OpenAI Agents patterns.
    
    Provides structured progress reporting with percentage completion,
    async support, and timeout handling.
    """
    
    def __init__(self, console):
        self.console = console
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
            transient=True
        )
        self.current_task_id = None
        self.start_time = None
        self.timeout_threshold = 60  # 60 seconds timeout warning
        
    def start_task(self, description: str, total: int = 100) -> int:
        """Start a new progress task."""
        self.start_time = time.time()
        self.current_task_id = self.progress.add_task(description, total=total)
        return self.current_task_id
    
    def update_progress(self, task_id: int, advance: int = 1, description: str = None) -> None:
        """Update progress for a task."""
        if description:
            self.progress.update(task_id, description=description, advance=advance)
        else:
            self.progress.update(task_id, advance=advance)
    
    def complete_task(self, task_id: int) -> None:
        """Complete a task."""
        self.progress.update(task_id, completed=100)
        elapsed = time.time() - self.start_time if self.start_time else 0
        self.console.print(f"✅ [green]Task completed in {elapsed:.1f}s[/green]")
    
    def check_timeout_warning(self) -> bool:
        """Check if we should show a timeout warning."""
        if self.start_time and time.time() - self.start_time > self.timeout_threshold:
            return True
        return False
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since task started."""
        return time.time() - self.start_time if self.start_time else 0


class ProcessingStatus(BaseModel):
    """Structured status reporting following OpenAI Agents pattern."""
    stage: str
    progress: int
    message: str
    elapsed_time: float
    estimated_remaining: Optional[float] = None
    is_timeout_warning: bool = False


class AsyncProgressHandler:
    """
    Async progress handler for long-running operations.
    
    Follows OpenAI Agents async patterns for better user experience.
    """
    
    def __init__(self, console):
        self.console = console
        # Use rich console for progress tracking
        self.rich_console = RichConsole()
        self.tracker = ProgressTracker(self.rich_console)
        self.status_history: List[ProcessingStatus] = []
    
    async def execute_with_progress(self, 
                                   operation_func,
                                   operation_name: str,
                                   timeout_seconds: int = 120) -> Any:
        """
        Execute an operation with progress tracking and timeout handling.
        
        Args:
            operation_func: The async function to execute
            operation_name: Name of the operation for progress display
            timeout_seconds: Timeout in seconds
            
        Returns:
            Result of the operation or raises timeout
        """
        # Start progress tracking
        task_id = self.tracker.start_task(f"🔄 {operation_name}")
        
        try:
            with Live(self.tracker.progress, console=self.rich_console, refresh_per_second=4):
                # Create progress update task
                progress_task = asyncio.create_task(
                    self._update_progress_periodically(task_id, operation_name)
                )
                
                # Create timeout task
                timeout_task = asyncio.create_task(
                    asyncio.sleep(timeout_seconds)
                )
                
                # Create operation task
                operation_task = asyncio.create_task(operation_func())
                
                # Wait for first completion
                done, pending = await asyncio.wait(
                    [operation_task, timeout_task],
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                # Cancel remaining tasks
                for task in pending:
                    task.cancel()
                progress_task.cancel()
                
                # Check results
                if operation_task in done:
                    result = await operation_task
                    self.tracker.complete_task(task_id)
                    return result
                else:
                    # Timeout occurred
                    self.tracker.progress.update(task_id, description="⏰ Operation timed out")
                    raise asyncio.TimeoutError(f"Operation '{operation_name}' timed out after {timeout_seconds}s")
                    
        except Exception as e:
            self.tracker.progress.update(task_id, description=f"❌ Error: {str(e)[:50]}...")
            raise e
    
    async def _update_progress_periodically(self, task_id: int, operation_name: str):
        """Update progress periodically with time-based estimates."""
        stages = [
            "Initializing connection...",
            "Sending request...",
            "Processing query...",
            "Analyzing content...",
            "Generating response...",
            "Finalizing results..."
        ]
        
        stage_duration = 20  # seconds per stage
        current_stage = 0
        
        while True:
            try:
                elapsed = self.tracker.get_elapsed_time()
                
                # Calculate current stage and progress
                stage_index = min(int(elapsed / stage_duration), len(stages) - 1)
                stage_progress = (elapsed % stage_duration) / stage_duration * 100
                overall_progress = (stage_index * 100 + stage_progress) / len(stages)
                
                # Update progress
                current_description = f"🔄 {operation_name} - {stages[stage_index]}"
                self.tracker.update_progress(task_id, advance=0, description=current_description)
                self.tracker.progress.update(task_id, completed=min(overall_progress, 95))
                
                # Check for timeout warning
                if self.tracker.check_timeout_warning() and not any(s.is_timeout_warning for s in self.status_history):
                    self.console.print("⚠️ [yellow]Operation is taking longer than expected...[/yellow]")
                    self.status_history.append(ProcessingStatus(
                        stage="timeout_warning",
                        progress=int(overall_progress),
                        message="Operation taking longer than expected",
                        elapsed_time=elapsed,
                        is_timeout_warning=True
                    ))
                
                # Record status
                self.status_history.append(ProcessingStatus(
                    stage=stages[stage_index],
                    progress=int(overall_progress),
                    message=f"Processing {operation_name}",
                    elapsed_time=elapsed,
                    estimated_remaining=max(0, 120 - elapsed) if elapsed < 120 else None
                ))
                
                await asyncio.sleep(1)  # Update every second
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                # Log error but continue
                logging.error(f"Error in progress update: {e}")
                await asyncio.sleep(1)


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
        
        # Current processing mode and agent
        self.current_mode: str = "smart"  # "smart", "prompt", "flowise", "prisma"
        self.current_agent = None
        self.user_preferences = {
            "auto_suggest": True,
            "show_tips": True,
            "confirm_mode_switch": False,
            "auto_fallback": True
        }
        
        # Smart mode detection patterns
        self.mode_patterns = {
            "prompt": [
                r"quantum|technology|latest|recent|current|compare|analysis|research|explain.*how",
                r"artificial intelligence|AI|machine learning|deep learning",
                r"what.*latest|recent.*development|current.*state",
                r"explain.*detail|comprehensive.*analysis|in-depth"
            ],
            "deep_research": [
                r"research|study|analysis|comprehensive|literature|review",
                r"scientific|academic|peer.*review|publication|journal",
                r"systematic.*review|meta.*analysis|evidence.*based",
                r"multiple.*sources|research.*synthesis|knowledge.*base"
            ],
            "aeromedical_risk": [
                r"pilot|flight.*safety|aviation.*medicine|aeromedical",
                r"risk.*assessment|medical.*fitness|flight.*physical",
                r"commercial.*pilot|airline|FAA|aviation.*regulation",
                r"altitude.*sickness|hypoxia|G-force|aerospace.*physiology"
            ],
            "aerospace_medicine_rag": [
                r"aerospace.*medicine|space.*medicine|aviation.*medicine",
                r"scientific.*article|textbook|medical.*literature",
                r"physiology|clinical|health|treatment|therapy|diagnosis",
                r"medical.*research|clinical.*guideline|evidence.*based"
            ],
            "prisma": [
                r"prisma|systematic.*review|meta.*analysis"
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
        
        # Default to aerospace_medicine_rag for medical/scientific queries, o3 for general
        if any(term in query_lower for term in ["medical", "health", "physiology", "clinical", "aerospace", "aviation"]):
            return "aerospace_medicine_rag", 0.6
        else:
            return "prompt", 0.5
    
    def display_enhanced_welcome(self) -> None:
        """Display an enhanced welcome message with better onboarding."""
        
        # Title - simple text with emoticon
        self.console.print("\n🚀 [bold blue]Advanced Aeromedical Evidence Review System[/bold blue]\n")
        
        # Quick start guide
        self.console.print("🎯 [bold]How to Get Started[/bold]")
        self.console.print("[bold]Just ask your question![/bold] The system will automatically detect the best processing method:")
        self.console.print()
        self.console.print("• [bold]Medical/Aviation Questions[/bold] → Flowise with specialized aerospace medicine knowledge")
        self.console.print("• [bold]Research/Analysis[/bold] → Prompt with web search or Flowise deep research")
        self.console.print("• [bold]Risk Assessment[/bold] → Aeromedical risk evaluation")
        self.console.print()
        self.console.print("[bold]Pro Tips:[/bold]")
        self.console.print("• Type [bold]?[/bold] for quick help  • [bold]/modes[/bold] to see all modes  • [bold]>>>[/bold] for multiline input")
        self.console.print("• [bold]/history[/bold] to review conversation  • [bold]/clear[/bold] to start fresh")
        self.console.print("• [bold]/fallback[/bold] to toggle auto-fallback to Prompt when Flowise times out")
        self.console.print("• [bold]Progress tracking[/bold] shows completion percentage and time estimates")
        self.console.print()
        
        # Available modes - simple text layout
        self.console.print("🛠️ [bold]Available Processing Modes[/bold]")
        self.console.print()
        self.console.print("[cyan]🔬 Prompt Research[/cyan]          [green]🔬 Deep Research[/green]")
        self.console.print("Complex analysis            Comprehensive analysis")
        self.console.print("Latest research             Multiple sources")  
        self.console.print("Technology reviews          Literature synthesis")
        self.console.print()
        self.console.print("[yellow]🚁 Aero Risk[/yellow]           [blue]🚀 Aerospace Medicine[/blue]")
        self.console.print("Flight safety               Scientific articles")
        self.console.print("Risk assessment             Medical textbooks")
        self.console.print("Aviation medicine           Evidence-based care")
        self.console.print()
        self.console.print("[magenta]🎯 Smart Mode[/magenta]")
        self.console.print("Auto-detection")
        self.console.print("Best AI selection")
        self.console.print("Seamless routing")
        self.console.print()
    
    def display_current_status(self) -> None:
        """Display current system status and available options."""
        mode_info = {
            "smart": ("🎯", "Smart Auto-Detection", "System automatically selects best AI"),
            "prompt": ("🔬", "Prompt Research", "Complex analysis and reasoning"),
            "deep_research": ("🔬", "Deep Research", "Comprehensive research synthesis"),
            "aeromedical_risk": ("🚁", "Aeromedical Risk", "Aviation medicine assessment"),
            "aerospace_medicine_rag": ("🚀", "Aerospace Medicine RAG", "Scientific articles and textbooks"),
            "prisma": ("📊", "PRISMA Systematic Review", "Systematic reviews, meta-analyses, evidence synthesis")
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
        
        self.console.print("[cyan]🔬 Prompt Research[/cyan]")
        self.console.print("   Complex analysis, latest research, technology reviews")
        self.console.print("   Quick Switch: [green]/prompt[/green]")
        self.console.print()
        
        self.console.print("[cyan]🔬 Deep Research[/cyan]")
        self.console.print("   Comprehensive research analysis with multiple sources")
        self.console.print("   Quick Switch: [green]/deep[/green]")
        self.console.print()
        
        self.console.print("[cyan]🚁 Aeromedical Risk[/cyan]")
        self.console.print("   Aviation medicine, flight safety, risk assessment")
        self.console.print("   Quick Switch: [green]/aero[/green]")
        self.console.print()
        
        self.console.print("[cyan]🚀 Aerospace Medicine RAG[/cyan]")
        self.console.print("   Scientific articles and textbooks in aerospace medicine")
        self.console.print("   Quick Switch: [green]/aerospace[/green]")
        self.console.print()
        
        self.console.print("[cyan]📊 PRISMA Systematic Review[/cyan]")
        self.console.print("   Systematic reviews, meta-analyses, evidence synthesis")
        self.console.print("   Quick Switch: [green]/prisma[/green]")
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
            ("/fallback", "Toggle automatic fallback to Prompt when Flowise times out"),
            ("/quit", "Exit the application")
        ]
        
        mode_specific = {
            "smart": [
                ("Auto-detection", "System selects best AI based on your question"),
                ("Progress tracking", "Shows completion percentage and time estimates"),
                ("Auto-fallback", "Automatically switches to Prompt if Flowise times out"),
                ("Override", "Use /prompt, /deep, /aero, /aerospace, /prisma to force specific mode")
            ],
            "prompt": [
                ("Best for", "Scientific research, complex analysis, current events"),
                ("Features", "Prompt model with web search capabilities")
            ],
            "deep_research": [
                ("Best for", "Comprehensive research, literature synthesis, multiple sources"),
                ("Features", "Specialized research RAG with advanced knowledge synthesis")
            ],
            "aeromedical_risk": [
                ("Best for", "Aviation medicine, pilot fitness, flight safety"),
                ("Features", "Conservative risk assessment with safety-first approach")
            ],
            "aerospace_medicine_rag": [
                ("Best for", "Aerospace medicine, scientific articles, medical textbooks"),
                ("Features", "Specialized aerospace medicine knowledge base with evidence-based content")
            ],
            "prisma": [
                ("Best for", "Systematic reviews, meta-analyses, comprehensive research"),
                ("Features", "Multi-agent workflow with Prompt, Flowise, and Perplexity")
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
            "prompt": [
                "Explain quantum computing applications in cryptography",
                "Compare latest renewable energy technologies",
                "Analyze current developments in space exploration"
            ],
            "deep_research": [
                "Comprehensive analysis of pilot fatigue countermeasures",
                "Literature review on cardiovascular effects in aerospace medicine",
                "Research synthesis on telemedicine effectiveness"
            ],
            "aeromedical_risk": [
                "Cardiovascular risk factors for commercial pilots",
                "Medical fitness requirements for high-altitude operations",
                "Assessment of medication effects on flight safety"
            ],
            "aerospace_medicine_rag": [
                "Physiological changes during long-duration spaceflight",
                "Clinical guidelines for aviation medical examinations",
                "Evidence-based treatment protocols for aerospace medicine"
            ],
            "prisma": [
                "Effectiveness of telemedicine interventions in rural healthcare",
                "Systematic review of pilot fatigue countermeasures",
                "Meta-analysis of cardiovascular effects in aerospace medicine"
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
            "prompt": "🔬 Enter your research question",
            "deep_research": "🔬 Enter your research query",
            "aeromedical_risk": "🚁 Enter your aeromedical question",
            "aerospace_medicine_rag": "🚀 Enter your aerospace medicine question",
            "prisma": "📊 Enter your systematic review research question"
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
                "prompt": "🔬 Prompt Research",
                "deep_research": "🔬 Deep Research", 
                "aeromedical_risk": "🚁 Aeromedical Risk Assessment",
                "aerospace_medicine_rag": "🚀 Aerospace Medicine RAG",
                "prisma": "📊 PRISMA Systematic Review"
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
            "prompt": self.prompt_agents,
            "deep_research": self.flowise_agents["deep_research"],
            "aeromedical_risk": self.flowise_agents["aeromedical_risk"],
            "aerospace_medicine_rag": self.flowise_agents["aerospace_medicine_rag"],
            "prisma": self.prisma_system
        }
        
        if new_mode not in mode_agents:
            self.console.print(f"[red]❌ Unknown mode: {new_mode}[/red]")
            return False
        
        # Special handling for PRISMA mode
        if new_mode == "prisma":
            if not self.prisma_system:
                self.console.print("[red]❌ PRISMA mode unavailable - missing API keys or configuration[/red]")
                self.console.print("[yellow]💡 PRISMA requires: OpenAI, Flowise, Perplexity, and Grok API keys[/yellow]")
                return False
        
        old_mode = self.current_mode
        self.current_mode = new_mode
        self.current_agent = mode_agents[new_mode]
        
        mode_names = {
            "smart": "🎯 Smart Auto-Detection",
            "prompt": "🔬 Prompt Research",
            "deep_research": "🔬 Deep Research",
            "aeromedical_risk": "🚁 Aeromedical Risk Assessment",
            "aerospace_medicine_rag": "🚀 Aerospace Medicine RAG",
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
            elif command in ['prompt', 'p']:
                self.switch_mode("prompt")
                return True
            elif command in ['deep', 'deepresearch', 'd']:
                self.switch_mode("deep_research")
                return True
            elif command in ['aero', 'aeromedical', 'risk', 'a']:
                self.switch_mode("aeromedical_risk")
                return True
            elif command in ['aerospace', 'aerospace_medicine', 'medicine', 'am']:
                self.switch_mode("aerospace_medicine_rag")
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
            elif command in ['fallback', 'toggle-fallback']:
                self.toggle_fallback()
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
            suggested_mode, _ = self.detect_optimal_mode(user_input)
            self.switch_mode(suggested_mode)

        if not self.current_agent:
            self.console.print("❌ [red]No processing agent available for this mode. Please select another mode.[/red]")
            self.display_mode_selection()
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
            self.show_export_options()
            
        except Exception as e:
            logger.error(f"Error processing request with agent {agent_name}: {e}", exc_info=True)
            self.console.print(f"❌ [red]Error during processing: {e}[/red]")
            # Attempt fallback for Flowise errors
            if "flowise" in self.current_mode and self.user_preferences["auto_fallback"]:
                await self.attempt_flowise_fallback(user_input)

        return True

    def is_timeout_error(self, error_message: str) -> bool:
        """
        Check if the error is a timeout error that should trigger fallback.
        
        Args:
            error_message: The error message to check
            
        Returns:
            True if this is a timeout error, False otherwise
        """
        timeout_indicators = [
            "504 Gateway Time-out",
            "504 Gateway Timeout",
            "timeout",
            "timed out",
            "connection timeout",
            "gateway timeout",
            "502 Bad Gateway",
            "503 Service Unavailable"
        ]
        
        error_lower = error_message.lower()
        return any(indicator.lower() in error_lower for indicator in timeout_indicators)
    
    async def attempt_flowise_fallback(self, user_input: str) -> bool:
        """
        Attempt to fallback to O3 agents when Flowise fails.
        
        Args:
            user_input: The original user input
            
        Returns:
            True if fallback was successful, False otherwise
        """
        try:
            # Check if O3 agents are available
            if not self.o3_agents or "o3_enhancer" not in self.o3_agents:
                logger.warning("O3 agents not available for fallback")
                return False
            
            # Store the original mode for restoration later
            original_mode = self.current_mode
            original_agent = self.current_agent
            
            # Show fallback notification
            self.console.print()
            self.console.print("⚡ [yellow]Flowise API timeout detected - automatically switching to Prompt fallback[/yellow]")
            self.console.print("🔄 [cyan]Retrying your request with Prompt Research...[/cyan]")
            self.console.print()
            
            # Switch to O3 mode temporarily
            self.switch_mode("prompt")
            
            # Remove the failed user message from history (it was already added)
            if self.messages and self.messages[-1].get("role") == "user":
                self.messages.pop()
            
            # Add user message to conversation
            self.messages.append({"role": "user", "content": user_input})
            
            # Process with O3 agent
            with self.console.status("[bold green]Processing with Prompt fallback..."):
                response = self.orchestrator.run_full_turn(self.current_agent, self.messages)
            
            # Update current agent and messages
            if response.agent:
                self.current_agent = response.agent
            self.messages.extend(response.messages)
            
            # Display the response
            if response.messages:
                last_message = response.messages[-1]
                if last_message.get("role") == "assistant" and last_message.get("content"):
                    response_content = last_message["content"]
                    
                    self.console.print(f"\n🔬 Prompt Research (Fallback)")
                    self.console.print("─" * 60)
                    self.console.print(response_content)
                    self.console.print("─" * 60)
            
            # Show success message
            self.console.print(f"\n[green]✅ Fallback successful! Response generated with Prompt Research.[/green]")
            
            # Offer to stay in O3 mode or return to original mode
            if original_mode != "prompt":
                self.console.print()
                self.console.print(f"[yellow]💡 Note: Switched from {original_mode} to Prompt mode due to Flowise timeout.[/yellow]")
                self.console.print("• Type /prompt to stay in Prompt mode")
                self.console.print(f"• Type /{original_mode} to return to {original_mode} mode")
                self.console.print("• Type /smart for automatic mode selection")
            
            # Show export options
            self.show_export_options()
            
            logger.info(f"Fallback successful: {original_mode} -> Prompt")
            return True
            
        except Exception as fallback_error:
            logger.error(f"Fallback to Prompt failed: {fallback_error}")
            self.console.print(f"[red]❌ Fallback to Prompt also failed: {fallback_error}[/red]")
            
            # Restore original mode and agent
            self.current_mode = original_mode
            self.current_agent = original_agent
            
            return False

    def display_prisma_status(self) -> None:
        """Display PRISMA system status and capabilities."""
        try:
            if not self.prisma_system:
                self.console.print("📊 [bold]PRISMA System Status[/bold]")
                self.console.print("[red]❌ PRISMA agent system not initialized[/red]")
                self.console.print()
                self.console.print("PRISMA requires the following API keys:")
                self.console.print("• OpenAI API key (OPENAI_API_KEY)")
                self.console.print("• Flowise API key (FLOWISE_API_KEY)")
                self.console.print("• Perplexity API key (PPLX_API_KEY)")
                self.console.print("• Grok API key (XAI_API)")
                self.console.print()
                return
            
            # Get system status
            status = self.prisma_system.get_prisma_status()
            
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
            
            # Models in use
            models_in_use = status.get("models_in_use", {})
            if models_in_use:
                self.console.print("[bold]Models Currently in Use:[/bold]")
                primary_model = models_in_use.get("primary_model", "")
                fallback_model = models_in_use.get("fallback_model", "")
                perplexity_model = models_in_use.get("perplexity_model", "")
                grok_model = models_in_use.get("grok_model", "")
                
                self.console.print(f"  🎯 Primary: {primary_model}")
                self.console.print(f"  🔄 Fallback: {fallback_model}")
                self.console.print(f"  🔍 Literature Search: {perplexity_model}")
                self.console.print(f"  🧠 Critical Analysis: {grok_model}")
                self.console.print()
                
                # Workflow phases
                workflow_phases = models_in_use.get("workflow_phases", {})
                if workflow_phases:
                    self.console.print("[bold]Workflow Model Assignment:[/bold]")
                    for phase, model_info in workflow_phases.items():
                        phase_name = phase.replace('_', ' ').title()
                        self.console.print(f"  • {phase_name}: {model_info}")
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
            if not self.prisma_system:
                self.console.print("[red]❌ PRISMA agent system not available[/red]")
                return
            
            # Get recent reviews
            reviews = self.prisma_system.list_recent_reviews(limit=10)
            
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
        
        self.console.print("[cyan]Auto fallback[/cyan]")
        self.console.print(f"  Current: {'✅ Enabled' if self.user_preferences['auto_fallback'] else '❌ Disabled'}")
        self.console.print("  Description: Automatically fallback to Prompt when Flowise encounters timeout errors")
        self.console.print()
        
        self.console.print("Settings modification coming in future update. Type /help for available commands.")
        self.console.print()
    
    def toggle_fallback(self) -> None:
        """Toggle the auto-fallback setting."""
        self.user_preferences["auto_fallback"] = not self.user_preferences["auto_fallback"]
        status = "✅ Enabled" if self.user_preferences["auto_fallback"] else "❌ Disabled"
        
        self.console.print()
        self.console.print("⚙️ [bold]Auto-Fallback Setting[/bold]")
        self.console.print(f"Auto-fallback is now: {status}")
        self.console.print()
        
        if self.user_preferences["auto_fallback"]:
            self.console.print("🔄 [green]Auto-fallback enabled[/green] - System will automatically switch to Prompt when Flowise times out")
        else:
            self.console.print("⏸️ [yellow]Auto-fallback disabled[/yellow] - System will show error messages instead of falling back")
        
        self.console.print()
        self.console.print("💡 Use /settings to view all preferences or /fallback to toggle this setting again.")
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
        """Main application loop for the enhanced interface."""
        self.display_enhanced_welcome()
        
        # This loop is now synchronous and will call asyncio.run for each input.
        while True:
            try:
                user_input = self.get_user_input_enhanced()
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