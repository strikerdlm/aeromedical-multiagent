"""
AGENTS.md integration utilities.

This module provides a lightweight, optional mechanism to load and apply
project-level guidelines from an `AGENTS.md`-style document and prepend them to
agent instruction prompts at runtime.

The feature can be toggled via environment (see AppConfig) or at runtime by the
application. The integration is deliberately simple and safe: if the guidelines
file is missing or disabled, original instructions are returned unchanged.
"""
from __future__ import annotations

import os
from typing import Optional

from .config import AppConfig


# ---------------------------------------------------------------------------
# Internal state
# ---------------------------------------------------------------------------
_CACHED_AGENTS_MD_CONTENT: Optional[str] = None
_IS_ENABLED: bool = getattr(AppConfig, "ENABLE_AGENTS_MD", False)


def set_enabled(enabled: bool) -> None:
    """Globally enable/disable AGENTS.md guidelines application."""
    global _IS_ENABLED
    _IS_ENABLED = bool(enabled)


def is_enabled() -> bool:
    """Return whether AGENTS.md guidelines are currently enabled."""
    return _IS_ENABLED


def _try_read_file(path: str) -> Optional[str]:
    try:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception:
        # Fail silent – feature is optional
        return None
    return None


def load_agents_md_content(path: Optional[str] = None) -> str:
    """Load AGENTS.md content from the given path or common defaults.

    Search order:
    1) explicit `path` argument
    2) AppConfig.AGENTS_MD_PATH
    3) Docs/AGENTS.md
    4) AGENTS.md (repo root)
    """
    candidate_paths = []  # type: list[str]
    if path:
        candidate_paths.append(path)

    # From configuration
    cfg_path = getattr(AppConfig, "AGENTS_MD_PATH", "")
    if cfg_path:
        candidate_paths.append(cfg_path)

    # Common fallbacks
    candidate_paths.extend([
        os.path.join("Docs", "AGENTS.md"),
        "AGENTS.md",
    ])

    for p in candidate_paths:
        content = _try_read_file(p)
        if content:
            return content
    return ""


def get_agents_md_content() -> str:
    """Return cached AGENTS.md content, loading it on first access."""
    global _CACHED_AGENTS_MD_CONTENT
    if _CACHED_AGENTS_MD_CONTENT is None:
        _CACHED_AGENTS_MD_CONTENT = load_agents_md_content()
    return _CACHED_AGENTS_MD_CONTENT or ""


def apply_guidelines_to_instructions(original_instructions: str, role_label: str = "Agent") -> str:
    """Prepend AGENTS.md guidelines to `original_instructions` when enabled.

    If the feature is disabled or content is unavailable, the original string is
    returned unchanged.
    """
    if not _IS_ENABLED:
        return original_instructions

    content = get_agents_md_content()
    if not content:
        return original_instructions

    header = f"Project Guidelines (AGENTS.md) for {role_label}:"
    note = (
        "Follow these repository guidelines implicitly when reasoning and generating "
        "responses for this project. Do not restate them; apply them to your process."
    )

    combined = (
        f"{header}\n\n{note}\n\n---\n"  # separator for clarity
        f"{content}\n\n---\n\n"
        f"{original_instructions}"
    )
    return combined


