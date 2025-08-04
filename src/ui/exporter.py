"""
This module contains the UI-related logic for exporting responses,
conversations, and reports.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

from ..custom_rich.stubs import Prompt

if TYPE_CHECKING:
    from ..main import EnhancedPromptEnhancerApp


class ExportHandler:
    """Handles all user interaction for exporting data."""

    def __init__(self, app: "EnhancedPromptEnhancerApp"):
        """
        Initialize the ExportHandler.

        Args:
            app: The main application instance.
        """
        self.app = app
        self.console = app.console

    def export_latest_response(self) -> None:
        """Export the latest response to a markdown file."""
        try:
            if not self.app.messages:
                self.console.print("⚠️ [yellow]No conversation to export. Ask a question first![/yellow]")
                return

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
            self.console.print(f"❌ [red]Export failed: {e}[/red]")

    def export_structured_report(self) -> None:
        """Export a structured research report."""
        try:
            if not self.app.messages:
                self.console.print("⚠️ [yellow]No conversation to export. Ask a question first![/yellow]")
                return

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

            self.console.print()
            self.console.print(f"📁 [bold]Exported Files[/bold] ({len(exports)} total)")
            self.console.print()

            for filename, filepath, modified_time in exports:
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
            self.console.print(f"❌ [red]Failed to list exports: {e}[/red]")
