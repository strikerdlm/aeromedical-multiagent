"""
This module contains the main UserInterface class for the application.
"""
from __future__ import annotations
from typing import TYPE_CHECKING
import random

from ..custom_rich.stubs import Panel, Table, Text, Markdown, Prompt
from ..multiline_input import format_large_text_preview
from .exporter import ExportHandler
from .prisma_display import PrismaDisplay

if TYPE_CHECKING:
    from ..main import EnhancedPromptEnhancerApp


class UserInterface:
    """Handles all user interaction, including console output and input."""

    def __init__(self, app: "EnhancedPromptEnhancerApp"):
        """
        Initialize the UserInterface.

        Args:
            app: The main application instance.
        """
        self.app = app
        self.console = app.console
        self.exporter = ExportHandler(app)
        self.prisma_display = PrismaDisplay(app)

    def display_enhanced_welcome(self) -> None:
        """Display an enhanced welcome message with better onboarding."""
        
        title_panel = Panel(
            Text("Advanced Aeromedical Evidence Review System", justify="center", style="bold blue"),
            title="🚀 Welcome",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(title_panel)

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
        
        self.console.print("📖 [bold]Help & Commands[/bold]")
        self.console.print()
        
        self.console.print("[bold yellow]Commands:[/bold yellow]")
        for cmd, desc in base_commands:
            self.console.print(f"  [bold]{cmd}[/bold] - {desc}")
        
        if self.app.current_mode in mode_specific:
            self.console.print()
            self.console.print(f"[bold yellow]Current Mode ({self.app.current_mode.title()}):[/bold yellow]")
            for cmd, desc in mode_specific[self.app.current_mode]:
                self.console.print(f"  [bold]{cmd}[/bold] - {desc}")
        
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
        mode_prompts = {
            "smart": "🎯 Ask your question (auto-detection enabled)",
            "prompt": "🔬 Enter your research question",
            "deep_research": "🔬 Enter your research query",
            "aeromedical_risk": "🚁 Enter your aeromedical question",
            "aerospace_medicine_rag": "🚀 Enter your aerospace medicine question",
            "prisma": "📊 Enter your systematic review research question"
        }
        
        prompt_text = mode_prompts.get(self.app.current_mode, "💬 Enter your question")
        
        if self.app.current_mode == "smart" and self.app.user_preferences["show_tips"]:
            self.console.print("[dim]💡 Tip: The system will analyze your question and select the optimal AI model[/dim]")
        
        user_input = self.app.multiline_handler.get_single_or_multiline_input(
            prompt_text=prompt_text,
            mode_emoji=""
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

    def show_export_options(self) -> None:
        """Show export options after a response is generated."""
        self.console.print()
        self.console.print("💾 [bold]Export Options[/bold]")
        self.console.print("📄 /export - Save this response to markdown")
        self.console.print("📚 /save - Save full conversation to markdown")
        self.console.print("📊 /report - Create structured research report")
        self.console.print()

    # Delegate to handlers
    def export_latest_response(self) -> None:
        self.exporter.export_latest_response()

    def export_full_conversation(self) -> None:
        self.exporter.export_full_conversation()

    def export_structured_report(self) -> None:
        self.exporter.export_structured_report()

    def list_exported_files(self) -> None:
        self.exporter.list_exported_files()

    def display_prisma_status(self) -> None:
        self.prisma_display.display_prisma_status()

    def display_prisma_reviews(self) -> None:
        self.prisma_display.display_prisma_reviews() 