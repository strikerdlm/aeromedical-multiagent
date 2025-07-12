"""
Mode Manager for the Multi-Agent Prompt Enhancement Application.
"""
from __future__ import annotations
import re
from typing import Tuple, Optional, Any, Dict, List

from .custom_rich.stubs import Confirm, Console
from .config import AppConfig


class ModeManager:
    """Manages the processing modes and agents."""

    def __init__(self, app: "EnhancedPromptEnhancerApp"):
        """
        Initialize the ModeManager.
        
        Args:
            app: The main application instance, providing access to agents and console.
        """
        self.app = app
        self.console = app.console
        self.current_mode = "smart"
        self.current_agent = None

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
            "prompt": self.app.prompt_agents,
            "deep_research": self.app.flowise_agents["deep_research"],
            "aeromedical_risk": self.app.flowise_agents["aeromedical_risk"],
            "aerospace_medicine_rag": self.app.flowise_agents["aerospace_medicine_rag"],
            "prisma": self.app.prisma_system
        }
        
        if new_mode not in mode_agents:
            self.console.print(f"[red]❌ Unknown mode: {new_mode}[/red]")
            return False
        
        # Special handling for PRISMA mode
        if new_mode == "prisma":
            if not self.app.prisma_system:
                self.console.print("[red]❌ PRISMA mode unavailable - missing API keys or configuration[/red]")
                self.console.print("[yellow]💡 PRISMA requires: OpenAI, Flowise, Perplexity, and Grok API keys[/yellow]")
                return False
        
        old_mode = self.current_mode
        self.current_mode = new_mode
        self.current_agent = mode_agents[new_mode]
        self.app.current_mode = self.current_mode
        self.app.current_agent = self.current_agent
        
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
        
        for mode, patterns in AppConfig.MODE_PATTERNS.items():
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
        
        if confidence > 0.6 and self.app.user_preferences["auto_suggest"]:
            # High confidence - suggest mode switch
            mode_names = {
                "prompt": "🔬 Prompt Research",
                "deep_research": "🔬 Deep Research", 
                "aeromedical_risk": "🚁 Aeromedical Risk Assessment",
                "aerospace_medicine_rag": "🚀 Aerospace Medicine RAG",
                "prisma": "📊 PRISMA Systematic Review"
            }
            
            mode_name = mode_names.get(suggested_mode, suggested_mode)
            
            if self.app.user_preferences["confirm_mode_switch"]:
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