"""
This module contains classes for handling progress tracking and asynchronous
operations, separating the user interface from the core application logic.
"""

from __future__ import annotations

import time
import asyncio
from typing import List, Optional, Any

from pydantic import BaseModel

from ..custom_rich.stubs import (
    Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn,
    TimeElapsedColumn, Live
)
from ..config import AppConfig

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
        self.timeout_threshold = AppConfig.UI_TIMEOUT_WARNING_THRESHOLD

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
                                   timeout_seconds: int = AppConfig.UI_OPERATION_TIMEOUT_SECONDS) -> Any:
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
        stages = AppConfig.UI_PROGRESS_STAGES

        stage_duration = AppConfig.PROGRESS_STAGE_DURATION  # seconds per stage

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
