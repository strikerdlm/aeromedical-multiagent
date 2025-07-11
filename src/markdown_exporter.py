"""
Markdown Export Utility for the Aeromedical Evidence Review System.

This module provides functionality to export conversation data, responses,
and analysis results to well-formatted markdown files for easy sharing
and documentation.
"""

import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path


class MarkdownExporter:
    """
    Utility class for exporting conversation data to markdown format.
    
    Provides various export options including single responses, full conversations,
    and formatted reports with metadata.
    """
    
    def __init__(self, output_dir: str = "exports"):
        """
        Initialize the markdown exporter.
        
        Args:
            output_dir: Directory to save exported files (default: "exports")
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def _sanitize_filename(self, text: str, max_length: int = 50) -> str:
        """
        Sanitize text for use as a filename.
        
        Args:
            text: Text to sanitize
            max_length: Maximum filename length
            
        Returns:
            Sanitized filename string
        """
        # Remove markdown formatting and special characters
        clean_text = re.sub(r'[*_`#\[\]()]', '', text)
        # Replace spaces and special chars with underscores
        clean_text = re.sub(r'[^\w\s-]', '', clean_text)
        clean_text = re.sub(r'[\s-]+', '_', clean_text)
        # Truncate and clean up
        clean_text = clean_text[:max_length].strip('_')
        return clean_text or "export"
    
    def _format_timestamp(self) -> str:
        """Generate a formatted timestamp for exports."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _format_message_content(self, content: str, role: str) -> str:
        """
        Format message content for markdown export.
        
        Args:
            content: Message content
            role: Message role (user/assistant)
            
        Returns:
            Formatted markdown content
        """
        # Clean up any existing markdown artifacts from rich formatting
        content = re.sub(r'\[/?[^\]]*\]', '', content)  # Remove rich markup
        content = content.strip()
        
        if role == "user":
            return f"**Question/Request:**\n\n{content}\n"
        elif role == "assistant":
            return f"**Response:**\n\n{content}\n"
        else:
            return f"**{role.title()}:**\n\n{content}\n"
    
    def _generate_metadata_section(self, mode: str, agent_name: str = None, 
                                 total_messages: int = 0) -> str:
        """
        Generate metadata section for the export.
        
        Args:
            mode: Processing mode used
            agent_name: Name of the agent that generated the response
            total_messages: Total number of messages in conversation
            
        Returns:
            Formatted metadata section
        """
        mode_descriptions = {
            "smart": "🎯 Smart Auto-Detection - System automatically selected optimal AI",
            "o3": "🔬 O3 Deep Research - Complex analysis and reasoning",
            "flowise": "🌐 Flowise Medical RAG - Medical and scientific knowledge",
            "deepresearch_flowise": "🔬 DeepResearch RAG - Comprehensive research synthesis",
            "aeromedical_risk": "🚁 Aeromedical Risk Assessment - Aviation medicine evaluation"
        }
        
        metadata = f"""---

## Export Metadata

- **Export Date:** {self._format_timestamp()}
- **Processing Mode:** {mode_descriptions.get(mode, mode)}
- **Agent:** {agent_name or 'Unknown'}
- **Total Messages:** {total_messages}
- **System:** Aeromedical Evidence Review Framework

---

"""
        return metadata
    
    def export_latest_response(self, messages: List[Dict[str, Any]], mode: str,
                             agent_name: str = None, filename: str = None) -> str:
        """
        Export the latest response from the conversation.
        
        Args:
            messages: List of conversation messages
            mode: Current processing mode
            agent_name: Name of the processing agent
            filename: Optional custom filename
            
        Returns:
            Path to the exported file
        """
        if not messages:
            raise ValueError("No messages to export")
        
        # Find the latest user question and assistant response
        user_msg = None
        assistant_msg = None
        
        for i in range(len(messages) - 1, -1, -1):
            msg = messages[i]
            if msg.get("role") == "assistant" and not assistant_msg:
                assistant_msg = msg
            elif msg.get("role") == "user" and not user_msg:
                user_msg = msg
                if assistant_msg:  # We have both, stop looking
                    break
        
        if not assistant_msg:
            raise ValueError("No assistant response found to export")
        
        # Generate filename if not provided
        if not filename:
            question_preview = user_msg.get("content", "response")[:40] if user_msg else "response"
            filename = f"response_{self._sanitize_filename(question_preview)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        # Build markdown content
        content = f"# Aeromedical Evidence Review - Response Export\n\n"
        content += self._generate_metadata_section(mode, agent_name, len(messages))
        
        if user_msg:
            content += self._format_message_content(user_msg.get("content", ""), "user")
            content += "\n"
        
        content += self._format_message_content(assistant_msg.get("content", ""), "assistant")
        
        # Add footer
        content += f"\n---\n\n*Exported from Aeromedical Evidence Review Framework on {self._format_timestamp()}*\n"
        
        # Write to file
        file_path = self.output_dir / filename
        file_path.write_text(content, encoding='utf-8')
        
        return str(file_path)
    
    def export_full_conversation(self, messages: List[Dict[str, Any]], mode: str,
                               agent_name: str = None, filename: str = None) -> str:
        """
        Export the complete conversation history.
        
        Args:
            messages: List of conversation messages
            mode: Current processing mode
            agent_name: Name of the processing agent
            filename: Optional custom filename
            
        Returns:
            Path to the exported file
        """
        if not messages:
            raise ValueError("No conversation to export")
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"conversation_{timestamp}.md"
        
        # Build markdown content
        content = f"# Aeromedical Evidence Review - Full Conversation\n\n"
        content += self._generate_metadata_section(mode, agent_name, len(messages))
        
        content += "## Conversation History\n\n"
        
        # Group messages into Q&A pairs
        current_pair = []
        for message in messages:
            role = message.get("role", "")
            if role in ["user", "assistant"]:
                current_pair.append(message)
                
                # If we have a complete pair (user + assistant) or it's the last message
                if (len(current_pair) == 2 and current_pair[1]["role"] == "assistant") or message == messages[-1]:
                    # Export this pair
                    for msg in current_pair:
                        content += self._format_message_content(msg.get("content", ""), msg.get("role", ""))
                    content += "\n---\n\n"
                    current_pair = []
                elif len(current_pair) > 2:
                    # Reset if we have too many messages
                    current_pair = [message]
        
        # Add footer
        content += f"\n*Exported from Aeromedical Evidence Review Framework on {self._format_timestamp()}*\n"
        
        # Write to file
        file_path = self.output_dir / filename
        file_path.write_text(content, encoding='utf-8')
        
        return str(file_path)
    
    def export_structured_report(self, messages: List[Dict[str, Any]], mode: str,
                               agent_name: str = None, title: str = None,
                               filename: str = None) -> str:
        """
        Export a structured research report format.
        
        Args:
            messages: List of conversation messages
            mode: Current processing mode
            agent_name: Name of the processing agent
            title: Custom title for the report
            filename: Optional custom filename
            
        Returns:
            Path to the exported file
        """
        if not messages:
            raise ValueError("No content to export as report")
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"report_{timestamp}.md"
        
        # Extract title from first user message if not provided
        if not title:
            first_user_msg = next((msg for msg in messages if msg.get("role") == "user"), None)
            if first_user_msg:
                title = first_user_msg.get("content", "")[:100] + "..." if len(first_user_msg.get("content", "")) > 100 else first_user_msg.get("content", "Research Report")
            else:
                title = "Aeromedical Research Report"
        
        # Build markdown content
        content = f"# {title}\n\n"
        content += self._generate_metadata_section(mode, agent_name, len(messages))
        
        # Executive Summary (from last assistant response)
        last_assistant_msg = None
        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                last_assistant_msg = msg
                break
        
        if last_assistant_msg:
            summary = last_assistant_msg.get("content", "")[:300] + "..."
            content += f"## Executive Summary\n\n{summary}\n\n"
        
        # Research Questions
        content += "## Research Questions\n\n"
        user_questions = [msg for msg in messages if msg.get("role") == "user"]
        for i, msg in enumerate(user_questions, 1):
            content += f"{i}. {msg.get('content', '')}\n\n"
        
        # Detailed Analysis
        content += "## Detailed Analysis\n\n"
        
        # Group into sections
        section_num = 1
        current_user_msg = None
        
        for message in messages:
            role = message.get("role", "")
            if role == "user":
                current_user_msg = message
            elif role == "assistant" and current_user_msg:
                content += f"### {section_num}. Analysis\n\n"
                content += f"**Research Question:** {current_user_msg.get('content', '')}\n\n"
                content += f"**Analysis Results:**\n\n{message.get('content', '')}\n\n"
                section_num += 1
                current_user_msg = None
        
        # Conclusion
        if last_assistant_msg:
            content += "## Conclusion\n\n"
            content += "This analysis was generated using the Aeromedical Evidence Review Framework, "
            content += f"utilizing {mode} processing mode for optimal results relevant to aerospace medicine and aviation safety.\n\n"
        
        # Footer
        content += f"---\n\n*Report generated by Aeromedical Evidence Review Framework on {self._format_timestamp()}*\n"
        content += f"*Processing Mode: {mode} | Agent: {agent_name or 'Unknown'}*\n"
        
        # Write to file
        file_path = self.output_dir / filename
        file_path.write_text(content, encoding='utf-8')
        
        return str(file_path)
    
    def list_exports(self) -> List[Tuple[str, str, datetime]]:
        """
        List all exported markdown files in the export directory, sorted by modification time.
        
        Returns:
            A list of tuples, each containing (filename, absolute_path, modified_time).
        """
        exports = []
        if self.output_dir.exists():
            for file_path in self.output_dir.glob("*.md"):
                modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                exports.append((file_path.name, str(file_path), modified_time))
        
        # Sort by modification time (newest first)
        exports.sort(key=lambda x: x[2], reverse=True)
        return exports
    
    def get_export_directory(self) -> str:
        """Get the full path to the export directory."""
        return str(self.output_dir.absolute())

    def _generate_prisma_filename(self, research_question: str) -> str:
        """Generates a filename for the PRISMA review."""
        sanitized_title = self._sanitize_filename(research_question)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"PRISMA_review_{sanitized_title}_{timestamp}.md"

    def export_prisma_review(self, review_content: str, research_question: str) -> str:
        """
        Export a full PRISMA systematic review to a markdown file.
        
        Args:
            review_content: The full content of the systematic review.
            research_question: The research question for filename generation.

        Returns:
            The absolute path to the exported file.
        """
        filename = self._generate_prisma_filename(research_question)
        file_path = self.output_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(review_content)
        
        return str(file_path) 