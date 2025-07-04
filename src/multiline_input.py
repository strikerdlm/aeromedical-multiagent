"""
Multiline Input Handler for Prompt Enhancement System.

This module provides utilities for handling multiline text input,
including support for pasting large blocks of text as context.
"""

from __future__ import annotations

import sys
from typing import Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt


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
        
        return full_input
    
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
                    return input(">>> ").strip()
            else:
                # Regular single-line input
                return initial_input
                
        except (KeyboardInterrupt, EOFError):
            self.console.print("\n[yellow]Input cancelled.[/yellow]")
            return ""
    
    def _display_multiline_instructions(self) -> None:
        """Display instructions for multiline input."""
        instructions = """
        ## 📝 Multiline Input Mode
        
        **How to enter multiline text:**
        - Type or paste your text across multiple lines
        - Press **Enter** after each line to continue
        - Type **'/send'** on a new line to finish and send your input
        - Or press **Ctrl+D** (Linux/Mac) or **Ctrl+Z** (Windows) to finish
        
        **Perfect for:**
        - Large context blocks
        - Pasted research papers or articles
        - Multi-paragraph questions
        - Code snippets or data
        
        **Tips:**
        - You can paste large blocks of text directly
        - The system will handle formatting automatically
        - Line counts will be shown for large inputs
        - Use '/send' to submit your multiline input
        """
        
        self.console.print(Panel(instructions, title="📖 Multiline Input Help", border_style="blue"))
    
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
        
        summary_text = f"""
        **Input Summary:**
        - Lines: {len(lines)}
        - Characters: {char_count:,}
        - Words: {word_count:,}
        
        **Preview:**
        {preview}
        """
        
        self.console.print(Panel(summary_text, title="✅ Input Received", border_style="green"))


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
