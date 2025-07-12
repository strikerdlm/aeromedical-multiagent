"""
UI components for the Multi-Agent Prompt Enhancement Application.

This module contains classes for handling progress tracking, asynchronous operations,
and console output, separating the user interface from the core application logic.
"""

from __future__ import annotations

import time
import asyncio
from typing import List, Optional, Any, Dict, Tuple
import re

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.prompt import Prompt, Confirm
    from rich.markdown import Markdown
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
    from rich.live import Live
except ImportError:
    # Define fallback classes if rich is not installed
    class Console:
        def print(self, *args, **kwargs):
            print(*args)
    class Panel:
        def __init__(self, content, **kwargs):
            print(content)
    class Table:
        def __init__(self, **kwargs): pass
        def add_column(self, *args, **kwargs): pass
        def add_row(self, *args, **kwargs): pass
    class Text(str): pass
    class Prompt:
        @staticmethod
        def ask(prompt, **kwargs):
            return input(prompt)
    class Confirm:
        @staticmethod
        def ask(prompt, **kwargs):
            response = input(f"{prompt} [y/n]: ").lower()
            return response == 'y'
    class Markdown(str): pass
    class Progress:
        def __init__(self, *args, **kwargs): pass
    class SpinnerColumn: pass
    class TextColumn:
        def __init__(self, *args, **kwargs): pass
    class BarColumn: pass
    class TaskProgressColumn: pass
    class TimeElapsedColumn: pass
    class Live:
        def __init__(self, *args, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass


from pydantic import BaseModel

from .multiline_input import format_large_text_preview
from .config import AppConfig


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
        """Get elapsed time since task start."""
        if self.start_time:
            return time.time() - self.start_time
        return 0.0


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
        self.tracker = ProgressTracker(self.console)
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
            with Live(self.tracker.progress, console=self.console, refresh_per_second=4):
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
        
        stage_duration = AppConfig.PROGRESS_STAGE_DURATION  # seconds per stage
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
                
                await asyncio.sleep(0.25)
            except asyncio.CancelledError:
                break
            except Exception:
                # Log this but don't crash the progress updater
                pass


class UserInterface:
    """Handles all user interaction, including console output and input."""

    def __init__(self, app: "EnhancedPromptEnhancerApp"):
        """
        Initialize the UserInterface.

        Args:
            app: The main application instance, providing access to state and handlers.
        """
        self.app = app
        self.console = app.console

    def display_enhanced_welcome(self) -> None:
        """Display an enhanced welcome message with better onboarding."""
        
        # Main Title Panel
        title_panel = Panel(
            Text("Advanced Aeromedical Evidence Review System", justify="center", style="bold blue"),
            title="🚀 Welcome",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(title_panel)

        # Quick Start Guide Panel
        quick_start_text = """
[bold]Just ask your question![/bold] The system will automatically detect the best processing method:

• [bold]Medical/Aviation Questions[/bold] → Flowise with specialized aerospace medicine knowledge
• [bold]Research/Analysis[/bold] → Prompt Research with web search or Flowise deep research
• [bold]Risk Assessment[/bold] → Aeromedical risk evaluation
        """
        quick_start_panel = Panel(
            Markdown(quick_start_text.strip()),
            title="🎯 Quick Start",
            border_style="cyan",
            padding=(1, 2)
        )
        self.console.print(quick_start_panel)

        # Pro Tips Panel
        pro_tips_text = """
• **`?`** for quick help
• **`/modes`** to see all modes
• **`/history`** to review conversation
• **`/clear`** to start fresh
• **`>>>`** for multiline input
• **`/transfer <mode>`** to re-run last query in a new mode
        """
        pro_tips_panel = Panel(
            Markdown(pro_tips_text.strip()),
            title="💡 Pro Tips",
            border_style="yellow",
            padding=(1, 2)
        )
        self.console.print(pro_tips_panel)

        # Available Modes Table
        modes_table = Table(title="🛠️ Available Processing Modes", show_header=True, header_style="bold magenta")
        modes_table.add_column("Mode", style="cyan", no_wrap=True)
        modes_table.add_column("Description", style="green")
        modes_table.add_column("Command", style="yellow")

        modes_data = {
            "Smart Auto-Detection": ("System automatically selects best AI", "/smart"),
            "Prompt Research": ("Complex analysis and reasoning", "/prompt"),
            "Flowise Deep Research": ("Comprehensive research synthesis", "/deep"),
            "Aeromedical Risk": ("Aviation medicine assessment", "/aero"),
            "Aerospace Medicine RAG": ("Scientific articles and textbooks", "/aerospace"),
            "PRISMA Systematic Review": ("PRISMA-compliant reviews", "/prisma")
        }

        for mode, (desc, cmd) in modes_data.items():
            modes_table.add_row(mode, desc, cmd)

        self.console.print(modes_table)
        self.console.print()

    def display_current_status(self) -> None:
        """Display current system status and available options."""
        mode_info = {
            "smart": ("🎯", "Smart Auto-Detection", "System automatically selects best AI"),
            "prompt": ("🔬", "Prompt Research", "Complex analysis and reasoning"),
            "deep_research": ("🔬", "Deep Research", "Comprehensive research synthesis"),
            "aeromedical_risk": ("🚁", "Aeromedical Risk", "Aviation medicine assessment"),
            "aerospace_medicine_rag": ("🚀", "Aerospace Medicine RAG", "Scientific articles and textbooks"),
            "prisma": ("📊", "PRISMA Systematic Review", "PRISMA-compliant reviews")
        }
        
        emoji, mode_name, description = mode_info.get(self.app.current_mode, ("❓", "Unknown", "Unknown mode"))
        
        self.console.print("📊 [bold]Current Status[/bold]")
        self.console.print(f"Current Mode: {emoji} {mode_name}")
        self.console.print(f"Description: {description}")
        self.console.print(f"Messages: {len(self.app.messages)}")
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
        if self.app.current_mode in mode_specific:
            self.console.print()
            self.console.print(f"[bold yellow]Current Mode ({self.app.current_mode.title()}):[/bold yellow]")
            for cmd, desc in mode_specific[self.app.current_mode]:
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
        
        if self.app.current_mode in examples:
            self.console.print()
            self.console.print("[bold yellow]Example Questions:[/bold yellow]")
            for example in examples[self.app.current_mode]:
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
        
        prompt_text = mode_prompts.get(self.app.current_mode, "💬 Enter your question")
        
        # Show helpful context
        if self.app.current_mode == "smart" and self.app.user_preferences["show_tips"]:
            self.console.print("[dim]💡 Tip: The system will analyze your question and select the optimal AI model[/dim]")
        
        # Use the multiline input handler
        user_input = self.app.multiline_handler.get_single_or_multiline_input(
            prompt_text=prompt_text,
            mode_emoji=""  # We include emoji in the prompt text
        )
        
        return user_input.strip()

    def display_conversation_history(self) -> None:
        """Enhanced conversation history display."""
        if not self.app.messages:
            self.console.print("💭 [yellow]No conversation history yet. Start by asking a question![/yellow]")
            return
        
        self.console.print(f"📜 [bold]Conversation History[/bold] ({len(self.app.messages)} messages)")
        self.console.print()
        
        for i, message in enumerate(self.app.messages):
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
            
            if i < len(self.app.messages) - 1:
                self.console.print("[dim]" + "─" * 50 + "[/dim]")
        self.console.print()

    def display_settings(self) -> None:
        """Display and allow modification of user settings."""
        self.console.print("⚙️ [bold]User Settings[/bold]")
        self.console.print()
        
        self.console.print("[cyan]Auto-suggest modes[/cyan]")
        self.console.print(f"  Current: {'✅ Enabled' if self.app.user_preferences['auto_suggest'] else '❌ Disabled'}")
        self.console.print("  Description: Automatically suggest optimal processing modes")
        self.console.print()
        
        self.console.print("[cyan]Show tips[/cyan]")
        self.console.print(f"  Current: {'✅ Enabled' if self.app.user_preferences['show_tips'] else '❌ Disabled'}")
        self.console.print("  Description: Show helpful tips and context")
        self.console.print()
        
        self.console.print("[cyan]Confirm mode switches[/cyan]")
        self.console.print(f"  Current: {'✅ Enabled' if self.app.user_preferences['confirm_mode_switch'] else '❌ Disabled'}")
        self.console.print("  Description: Ask before automatically switching modes")
        self.console.print()
        
        self.console.print("[cyan]Auto fallback[/cyan]")
        self.console.print(f"  Current: {'✅ Enabled' if self.app.user_preferences['auto_fallback'] else '❌ Disabled'}")
        self.console.print("  Description: Automatically fallback to Prompt when Flowise encounters timeout errors")
        self.console.print()
        
        self.console.print("Settings modification coming in future update. Type /help for available commands.")
        self.console.print()

    def provide_contextual_tip(self) -> None:
        """Provide a random, helpful tip to the user after a response."""
        import random
        tips = [
            "Type `/modes` to see all available AI models.",
            "Use `/history` to review your conversation.",
            "You can export this response with `/export`.",
            "To start over, just type `/clear`.",
            f"Try switching to another mode, like `/transfer prompt` to re-run your last query.",
            "Use `>>>` at the start of your message for multiline input."
        ]
        
        tip = random.choice(tips)
        self.console.print(f"\n[dim]💡 Tip: {tip}[/dim]")

    def toggle_fallback(self) -> None:
        """Toggle the auto-fallback setting."""
        self.app.user_preferences["auto_fallback"] = not self.app.user_preferences["auto_fallback"]
        status = "✅ Enabled" if self.app.user_preferences["auto_fallback"] else "❌ Disabled"
        
        self.console.print()
        self.console.print("⚙️ [bold]Auto-Fallback Setting[/bold]")
        self.console.print(f"Auto-fallback is now: {status}")
        self.console.print()
        
        if self.app.user_preferences["auto_fallback"]:
            self.console.print("🔄 [green]Auto-fallback enabled[/green] - System will automatically switch to Prompt when Flowise times out")
        else:
            self.console.print("⏸️ [yellow]Auto-fallback disabled[/yellow] - System will show error messages instead of falling back")
        
        self.console.print()
        self.console.print("💡 Use /settings to view all preferences or /fallback to toggle this setting again.")
        self.console.print()

    def display_prisma_status(self) -> None:
        """Display PRISMA system status and capabilities."""
        try:
            if not self.app.prisma_system:
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
            status = self.app.prisma_system.get_prisma_status()
            
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
            # logger.error(f"Error displaying PRISMA status: {e}")
            self.console.print(f"[red]❌ Error getting PRISMA status: {e}[/red]")

    def display_prisma_reviews(self) -> None:
        """Display recent PRISMA reviews."""
        try:
            if not self.app.prisma_system:
                self.console.print("[red]❌ PRISMA agent system not available[/red]")
                return
            
            # Get recent reviews
            reviews = self.app.prisma_system.list_recent_reviews(limit=10)
            
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
            # logger.error(f"Error displaying PRISMA reviews: {e}")
            self.console.print(f"[red]❌ Error getting PRISMA reviews: {e}[/red]")

    def export_latest_response(self) -> None:
        """Export the latest response to a markdown file."""
        try:
            if not self.app.messages:
                self.console.print("⚠️ [yellow]No conversation to export. Ask a question first![/yellow]")
                return
            
            # Check if there's at least one assistant response
            has_response = any(msg.get("role") == "assistant" for msg in self.app.messages)
            if not has_response:
                self.console.print("⚠️ [yellow]No AI response found to export.[/yellow]")
                return
            
            agent_name = self.app.current_agent.name if self.app.current_agent else "Unknown"
            
            file_path = self.app.markdown_exporter.export_latest_response(
                self.app.messages, self.app.current_mode, agent_name
            )
            
            self.console.print()
            self.console.print("📄 [green]Export Complete[/green]")
            self.console.print(f"[green]✅ Latest response exported successfully![/green]")
            self.console.print()
            self.console.print(f"[bold]File:[/bold] `{file_path}`")
            self.console.print(f"[bold]Location:[/bold] `{self.app.markdown_exporter.get_export_directory()}`")
            self.console.print()
            self.console.print("💡 You can now share this markdown file or import it into your documentation.")
            self.console.print()
            
        except Exception as e:
            # logger.error(f"Error exporting latest response: {e}")
            self.console.print(f"❌ [red]Export failed: {e}[/red]")

    def export_full_conversation(self) -> None:
        """Export the complete conversation to a markdown file."""
        try:
            if not self.app.messages:
                self.console.print("⚠️ [yellow]No conversation to export. Ask a question first![/yellow]")
                return
            
            agent_name = self.app.current_agent.name if self.app.current_agent else "Unknown"
            
            file_path = self.app.markdown_exporter.export_full_conversation(
                self.app.messages, self.app.current_mode, agent_name
            )
            
            self.console.print()
            self.console.print("📚 [green]Conversation Export Complete[/green]")
            self.console.print(f"[green]✅ Full conversation exported successfully![/green]")
            self.console.print()
            self.console.print(f"[bold]File:[/bold] `{file_path}`")
            self.console.print(f"[bold]Messages:[/bold] {len(self.app.messages)}")
            self.console.print(f"[bold]Location:[/bold] `{self.app.markdown_exporter.get_export_directory()}`")
            self.console.print()
            self.console.print("💡 This includes all questions and responses from your current session.")
            self.console.print()
            
        except Exception as e:
            # logger.error(f"Error exporting conversation: {e}")
            self.console.print(f"❌ [red]Export failed: {e}[/red]")

    def export_structured_report(self) -> None:
        """Export a structured research report."""
        try:
            if not self.app.messages:
                self.console.print("⚠️ [yellow]No conversation to export. Ask a question first![/yellow]")
                return
            
            # Ask for optional title
            title = Prompt.ask(
                "\n📝 [cyan]Report title (optional)[/cyan]",
                default="",
                show_default=False
            )
            
            agent_name = self.app.current_agent.name if self.app.current_agent else "Unknown"
            
            file_path = self.app.markdown_exporter.export_structured_report(
                self.app.messages, self.app.current_mode, agent_name, 
                title.strip() if title.strip() else None
            )
            
            self.console.print()
            self.console.print("📊 [green]Research Report Export Complete[/green]")
            self.console.print(f"[green]✅ Research report exported successfully![/green]")
            self.console.print()
            self.console.print(f"[bold]File:[/bold] `{file_path}`")
            self.console.print(f"[bold]Format:[/bold] Structured research report with metadata")
            self.console.print(f"[bold]Location:[/bold] `{self.app.markdown_exporter.get_export_directory()}`")
            self.console.print()
            self.console.print("💡 This report includes executive summary, questions, and detailed analysis.")
            self.console.print()
            
        except Exception as e:
            # logger.error(f"Error exporting report: {e}")
            self.console.print(f"❌ [red]Export failed: {e}[/red]")

    def list_exported_files(self) -> None:
        """List all exported markdown files."""
        try:
            exports = self.app.markdown_exporter.list_exports()
            
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
            
            self.console.print(f"💡 Export directory: `{self.app.markdown_exporter.get_export_directory()}`")
            self.console.print()
            
        except Exception as e:
            # logger.error(f"Error listing exports: {e}")
            self.console.print(f"❌ [red]Failed to list exports: {e}[/red]")

    def show_export_options(self) -> None:
        """Show export options after a response is generated."""
        self.console.print()
        self.console.print("💾 [bold]Export Options[/bold]")
        self.console.print("📄 /export - Save this response to markdown")
        self.console.print("📚 /save - Save full conversation to markdown")
        self.console.print("📊 /report - Create structured research report")
        self.console.print() 