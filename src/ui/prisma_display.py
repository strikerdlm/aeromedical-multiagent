"""
This module contains the UI-related logic for displaying PRISMA-related
information.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..main import EnhancedPromptEnhancerApp


class PrismaDisplay:
    """Handles all user interaction for displaying PRISMA information."""

    def __init__(self, app: "EnhancedPromptEnhancerApp"):
        """
        Initialize the PrismaDisplay.

        Args:
            app: The main application instance.
        """
        self.app = app
        self.console = app.console

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

            status = self.app.prisma_system.get_prisma_status()

            self.console.print("📊 [bold]PRISMA System Status[/bold]")
            self.console.print()

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

            capabilities = status.get("capabilities", {})
            models = capabilities.get("models_available", {})
            self.console.print("[bold]Available Models:[/bold]")
            for model_type, model_name in models.items():
                self.console.print(f"  • {model_type.replace('_', ' ').title()}: {model_name}")
            self.console.print()

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

                workflow_phases = models_in_use.get("workflow_phases", {})
                if workflow_phases:
                    self.console.print("[bold]Workflow Model Assignment:[/bold]")
                    for phase, model_info in workflow_phases.items():
                        phase_name = phase.replace('_', ' ').title()
                        self.console.print(f"  • {phase_name}: {model_info}")
                    self.console.print()

            specs = capabilities.get("target_specifications", {})
            self.console.print("[bold]PRISMA Specifications:[/bold]")
            for spec_name, spec_value in specs.items():
                self.console.print(f"  • {spec_name.replace('_', ' ').title()}: {spec_value}")
            self.console.print()

            phases = capabilities.get("workflow_phases", [])
            self.console.print("[bold]Workflow Phases:[/bold]")
            for phase in phases:
                self.console.print(f"  • {phase}")
            self.console.print()

            session_count = status.get("session_history_count", 0)
            self.console.print(f"[bold]Session Information:[/bold]")
            self.console.print(f"  • Reviews completed: {session_count}")
            self.console.print(f"  • Current workflow: {'Active' if status.get('current_workflow_active') else 'None'}")
            self.console.print()

        except Exception as e:
            self.console.print(f"[red]❌ Error getting PRISMA status: {e}[/red]")

    def display_prisma_reviews(self) -> None:
        """Display recent PRISMA reviews."""
        try:
            if not self.app.prisma_system:
                self.console.print("[red]❌ PRISMA agent system not available[/red]")
                return

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

                self.console.print(f"[cyan]{i}. {question[:80]}{'...' if len(question) > 80 else ''}[/cyan]")
                self.console.print(f"   Session: {session_id}")
                self.console.print(f"   Status: {status_val} | Words: {word_count} | Citations: {citations}")

                validation = review.get("validation_status", {})
                if validation.get("meets_minimum_requirements"):
                    self.console.print("   [green]✅ Meets PRISMA requirements[/green]")
                else:
                    self.console.print("   [yellow]⚠️ May need improvements[/yellow]")

                self.console.print()

            self.console.print("💡 Use `/export` to save reviews or `/prisma-status` for system information.")
            self.console.print()

        except Exception as e:
            self.console.print(f"[red]❌ Error getting PRISMA reviews: {e}[/red]")
