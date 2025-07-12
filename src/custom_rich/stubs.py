"""
Centralized fallback stubs for the `rich` library.

This module provides mock objects for `rich` components that are used when
the `rich` library is not installed. This avoids code duplication and ensures
consistent behavior in environments without `rich`.
"""

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.prompt import Prompt, Confirm
    from rich.markdown import Markdown
    from rich.live import Live
    from rich.progress import (
        Progress,
        SpinnerColumn,
        TextColumn,
        BarColumn,
        TaskProgressColumn,
        TimeElapsedColumn,
    )
except ImportError:
    class Console:
        """A fallback Console that prints to stdout."""
        def print(self, *args, **kwargs):
            """Prints arguments to the console."""
            print(*args)

    class Panel:
        """A fallback Panel that prints its content."""
        def __init__(self, content, **kwargs):
            """Initializes the fallback Panel."""
            print(content)

    class Table:
        """A fallback Table that does nothing."""
        def __init__(self, **kwargs):
            """Initializes the fallback Table."""
            pass
        def add_column(self, *args, **kwargs):
            """Adds a column (no-op)."""
            pass
        def add_row(self, *args, **kwargs):
            """Adds a row (no-op)."""
            pass

    class Text(str):
        """A fallback Text object that behaves like a string."""
        pass

    class Prompt:
        """A fallback Prompt that uses standard input."""
        @staticmethod
        def ask(prompt, **kwargs):
            """Asks for input using the built-in input() function."""
            return input(prompt)

    class Confirm:
        """A fallback Confirm prompt."""
        @staticmethod
        def ask(prompt, **kwargs):
            """Asks for a yes/no confirmation."""
            response = input(f"{prompt} [y/n]: ").lower()
            return response == 'y'

    class Markdown(str):
        """A fallback Markdown object that behaves like a string."""
        pass

    class Live:
        """A fallback Live display that does nothing."""
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def update(self, *args, **kwargs):
            """Updates the live display (no-op)."""
            pass
        def start(self, *args, **kwargs):
            """Starts the live display (no-op)."""
            pass
        def stop(self):
            """Stops the live display (no-op)."""
            pass

    # Add fallback for Progress and related components
    class Progress:
        """A fallback Progress bar that does nothing."""
        def __init__(self, *args, **kwargs):
            pass
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
        def add_task(self, description, **kwargs):
            """Adds a task (no-op). Returns a dummy task ID."""
            print(f"Starting: {description}")
            return 1
        def update(self, task_id, **kwargs):
            """Updates a task (no-op)."""
            pass
        def stop(self):
            """Stops the progress display (no-op)."""
            pass

    class SpinnerColumn:
        def __init__(self, *args, **kwargs): pass
    class TextColumn:
        def __init__(self, *args, **kwargs): pass
    class BarColumn:
        def __init__(self, *args, **kwargs): pass
    class TaskProgressColumn:
        def __init__(self, *args, **kwargs): pass
    class TimeElapsedColumn:
        def __init__(self, *args, **kwargs): pass 