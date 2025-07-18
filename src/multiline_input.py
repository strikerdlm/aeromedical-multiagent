"""
Multiline Input Handler for Prompt Enhancement System.

This module provides utilities for handling multiline text input,
including support for pasting large blocks of text as context.
"""

from __future__ import annotations

import sys
from typing import Optional, List
import re

from .custom_rich.stubs import Console, Panel, Text, Prompt

class MultilineInputHandler:
    """
    Handler for multiline text input with support for large text blocks.
    
    This class provides methods for collecting multiline input from users,
    including special handling for pasted content and large context blocks.
    """
    
    def __init__(self, console: Optional[Console] = None):
        """
        Initialize the multiline input handler.
        
        Args:
            console: Rich console instance (creates default if None)
        """
        self.console = console or Console()
        self.MAX_INPUT_CHARS = 50000 # Max characters for multiline input
    
    def get_multiline_input(
        self, 
        prompt_text: str = "Enter your prompt",
        mode_emoji: str = "💬",
        show_instructions: bool = True
    ) -> str:
        """
        Get multiline input from the user with support for large text blocks.
        
        Args:
            prompt_text: The prompt text to display
            mode_emoji: Emoji to show in the prompt
            show_instructions: Whether to show multiline input instructions
            
        Returns:
            The complete user input as a string
        """
        if show_instructions:
            self._display_multiline_instructions()
        
        # Display the prompt
        self.console.print(f"\n[bold cyan]{mode_emoji} {prompt_text}[/bold cyan]")
        self.console.print("[dim]Enter your text. Type '/send' on a new line to finish:[/dim]")
        
        lines = []
        line_count = 0
        char_count = 0
        
        try:
            while True:
                try:
                    # Get input line by line
                    if line_count == 0:
                        line = input(">>> ")
                    else:
                        line = input("... ")
                    
                    # Check for end markers
                    if line.strip() == '/send':
                        break
                    elif line.strip().upper() in ['END', 'DONE', 'FINISH', '/END', '/DONE']:
                        self.console.print("[yellow]Note: Use '/send' to finish multiline input[/yellow]")
                        break
                    
                    lines.append(line)
                    line_count += 1
                    char_count += len(line)

                    if char_count > self.MAX_INPUT_CHARS:
                        self.console.print(f"[bold yellow]Warning: Input limit of {self.MAX_INPUT_CHARS} characters reached. Input has been truncated.[/bold yellow]")
                        break
                    
                    # Show progress for large inputs
                    if line_count > 0 and line_count % 10 == 0:
                        self.console.print(f"[dim]({line_count} lines entered...)[/dim]")
                
                except EOFError:
                    # Ctrl+D pressed - treat as end
                    break
                except KeyboardInterrupt:
                    # Ctrl+C pressed
                    self.console.print("\n[yellow]Input cancelled.[/yellow]")
                    return ""
        
        except Exception as e:
            self.console.print(f"[red]Error reading input: {e}[/red]")
            return ""
        
        # Join all lines
        full_input = '\n'.join(lines).strip()
        
        # Display summary of what was entered
        if full_input:
            self._display_input_summary(full_input)
        
        return self._sanitize_input(full_input)
    
    def get_single_or_multiline_input(
        self, 
        prompt_text: str = "Enter your prompt",
        mode_emoji: str = "💬"
    ) -> str:
        """
        Get input that can be either single line or multiline.
        
        This method first tries single-line input, but if the user types
        a multiline indicator, it switches to multiline mode.
        
        Args:
            prompt_text: The prompt text to display
            mode_emoji: Emoji to show in the prompt
            
        Returns:
            The complete user input as a string
        """
        # Show options
        self.console.print(f"\n[bold cyan]{mode_emoji} {prompt_text}[/bold cyan]")
        self.console.print("[dim]Type your prompt, or use '>>>' for multiline mode:[/dim]")
        
        try:
            initial_input = input(">>> ").strip()
            
            # Check if user wants multiline mode
            if initial_input == ">>>":
                return self.get_multiline_input(prompt_text, mode_emoji, show_instructions=False)
            elif initial_input.upper() in ['MULTILINE', 'MULTI', 'ML']:
                return self.get_multiline_input(prompt_text, mode_emoji, show_instructions=True)
            elif not initial_input:
                # Empty input, ask what they want to do
                choice = Prompt.ask(
                    "[yellow]Empty input. Do you want to[/yellow]",
                    choices=["single", "multi", "cancel"],
                    default="single"
                )
                if choice == "multi":
                    return self.get_multiline_input(prompt_text, mode_emoji, show_instructions=True)
                elif choice == "cancel":
                    return ""
                else:
                    return self._sanitize_input(input(">>> ").strip())
            else:
                # Regular single-line input
                return self._sanitize_input(initial_input)
                
        except (KeyboardInterrupt, EOFError):
            self.console.print("\n[yellow]Input cancelled.[/yellow]")
            return ""

    def _sanitize_input(self, text: str) -> str:
        """
        Sanitizes input text to remove potentially malicious content like script tags.
        
        Args:
            text: The input text to sanitize.
            
        Returns:
            The sanitized text.
        """
        # A simple regex to remove <script>...</script> blocks, case-insensitive.
        sanitized_text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        if len(sanitized_text) < len(text):
            self.console.print("[yellow]⚠️ Potential script content was removed from the input.[/yellow]")
        return sanitized_text

    def _display_multiline_instructions(self) -> None:
        """Display instructions for multiline input."""
        self.console.print()
        self.console.print("📝 [bold]Multiline Input Mode[/bold]")
        self.console.print()
        self.console.print("[bold]How to enter multiline text:[/bold]")
        self.console.print("- Type or paste your text across multiple lines")
        self.console.print("- Press [bold]Enter[/bold] after each line to continue")
        self.console.print("- Type [bold]'/send'[/bold] on a new line to finish and send your input")
        self.console.print("- Or press [bold]Ctrl+D[/bold] (Linux/Mac) or [bold]Ctrl+Z[/bold] (Windows) to finish")
        self.console.print()
        self.console.print("[bold]Perfect for:[/bold]")
        self.console.print("- Large context blocks")
        self.console.print("- Pasted research papers or articles")
        self.console.print("- Multi-paragraph questions")
        self.console.print("- Code snippets or data")
        self.console.print()
        self.console.print("[bold]Tips:[/bold]")
        self.console.print("- You can paste large blocks of text directly")
        self.console.print("- The system will handle formatting automatically")
        self.console.print("- Line counts will be shown for large inputs")
        self.console.print("- Use '/send' to submit your multiline input")
        self.console.print()
    
    def _display_input_summary(self, text: str) -> None:
        """
        Display a summary of the entered text.
        
        Args:
            text: The input text to summarize
        """
        lines = text.split('\n')
        char_count = len(text)
        word_count = len(text.split())
        
        # Show preview of first few lines
        preview_lines = lines[:3]
        if len(lines) > 3:
            preview_lines.append("...")
        
        preview = '\n'.join(preview_lines)
        
        self.console.print()
        self.console.print("✅ [green]Input Received[/green]")
        self.console.print()
        self.console.print("[bold]Input Summary:[/bold]")
        self.console.print(f"- Lines: {len(lines)}")
        self.console.print(f"- Characters: {char_count:,}")
        self.console.print(f"- Words: {word_count:,}")
        self.console.print()
        self.console.print("[bold]Preview:[/bold]")
        self.console.print(preview)
        self.console.print()


def get_multiline_input_simple() -> str:
    """
    Simple function to get multiline input without Rich formatting.
    
    Returns:
        The complete user input as a string
    """
    print("Enter your text (press Ctrl+D or type '/send' on a new line to finish):")
    
    lines = []
    try:
        while True:
            try:
                line = input(">>> " if not lines else "... ")
                if line.strip() == '/send':
                    break
                elif line.strip().upper() in ['END', 'DONE', 'FINISH']:
                    print("Note: Use '/send' to finish multiline input")
                    break
                lines.append(line)
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\nInput cancelled.")
                return ""
    except Exception as e:
        print(f"Error reading input: {e}")
        return ""
    
    return '\n'.join(lines).strip()


def detect_paste_input(text: str) -> bool:
    """
    Detect if the input appears to be pasted content.
    
    Args:
        text: The input text to analyze
        
    Returns:
        True if the text appears to be pasted content
    """
    # Heuristics for detecting pasted content
    lines = text.split('\n')
    
    # Check for multiple lines
    if len(lines) > 5:
        return True
    
    # Check for very long single line
    if len(text) > 500:
        return True
    
    # Check for academic/formal text patterns
    formal_indicators = [
        'abstract:', 'introduction:', 'methodology:', 'results:', 'conclusion:',
        'doi:', 'arxiv:', 'pubmed:', 'pmid:', 'issn:', 'isbn:',
        'university', 'journal', 'proceedings', 'conference',
        'et al.', 'fig.', 'table', 'equation'
    ]
    
    text_lower = text.lower()
    formal_count = sum(1 for indicator in formal_indicators if indicator in text_lower)
    
    if formal_count >= 2:
        return True
    
    return False


def format_large_text_preview(text: str, max_lines: int = 10, max_chars: int = 500) -> str:
    """
    Format a preview of large text for display.
    
    Args:
        text: The text to preview
        max_lines: Maximum number of lines to show
        max_chars: Maximum number of characters to show
        
    Returns:
        Formatted preview string
    """
    lines = text.split('\n')
    
    # Truncate by lines
    if len(lines) > max_lines:
        preview_lines = lines[:max_lines]
        preview_lines.append(f"... ({len(lines) - max_lines} more lines)")
        preview_text = '\n'.join(preview_lines)
    else:
        preview_text = text
    
    # Truncate by characters
    if len(preview_text) > max_chars:
        preview_text = preview_text[:max_chars] + "..."
    
    return preview_text
