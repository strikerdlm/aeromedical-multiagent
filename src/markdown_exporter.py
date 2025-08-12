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

    def export_citation_list(self, citations: List[str], title: str = "Verified Citation List", filename: str = None) -> str:
        """Export a list of APA formatted citations to a standalone Markdown file.

        Args:
            citations: A list of citation strings already formatted in APA style.
            title: Optional markdown title to use at the top of the document.
            filename: Optional filename (without path). If omitted a timestamped
                filename is generated automatically.

        Returns:
            The absolute filesystem path to the newly created markdown file.
        """
        if not citations:
            raise ValueError("The citation list is empty; nothing to export.")

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"citations_{timestamp}.md"

        content = f"# {title}\n\n"
        content += self._generate_metadata_section(mode="citations", agent_name="Citation Review Agent", total_messages=len(citations))
        content += "## References (APA 7th ed.)\n\n"

        for i, citation in enumerate(citations, 1):
            # Ensure each citation is on its own line with a numerical list marker
            if citation.lstrip().startswith(str(i)):
                content += f"{citation}\n"
            else:
                content += f"{i}. {citation}\n"

        # Footer
        content += f"\n---\n\n*Exported by Aeromedical Evidence Review Framework on {self._format_timestamp()}*\n"

        file_path = self.output_dir / filename
        file_path.write_text(content, encoding="utf-8")

        return str(file_path)

    # ---------------------------------------------------------------------
    # Convenience writer used by UI download flows
    # ---------------------------------------------------------------------
    def export_to_markdown(self, content: str, filename: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Write raw markdown content to a specific filename inside exports.

        Args:
            content: Markdown content to write
            filename: Target filename (relative name or path under exports)
            metadata: Optional dictionary to append as a metadata section

        Returns:
            Absolute path to the written file
        """
        file_path = Path(filename)
        if not file_path.is_absolute():
            file_path = self.output_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        final_content = content
        if metadata:
            # Append a simple metadata section at the end to avoid corrupting provided content
            meta_lines = ["\n---\n", "## Export Metadata (Appended)\n"]
            for k, v in metadata.items():
                meta_lines.append(f"- **{k}:** {v}\n")
            meta_lines.append(f"\n*Exported on {self._format_timestamp()}*\n")
            final_content = f"{content}\n{''.join(meta_lines)}"

        file_path.write_text(final_content, encoding="utf-8")
        return str(file_path.absolute())

    # ---------------------------------------------------------------------
    # Journal-style manuscript export (IMRaD)
    # ---------------------------------------------------------------------
    def _extract_sections_from_markdown(self, text: str) -> Dict[str, str]:
        """Best-effort extraction of common scientific sections from markdown.

        Scans for second-level headings (## Section) and collects their content.
        Returns a mapping from normalised section name to text.
        """
        sections: Dict[str, str] = {}
        if not text:
            return sections

        # Normalise newlines and ensure a trailing newline for parsing
        text = text.replace("\r\n", "\n").replace("\r", "\n") + "\n"
        pattern = re.compile(r"^##\s+(.+?)\n", re.MULTILINE)
        matches = list(pattern.finditer(text))

        # If no second-level headings, try first-level
        if not matches:
            pattern = re.compile(r"^#\s+(.+?)\n", re.MULTILINE)
            matches = list(pattern.finditer(text))

        if not matches:
            # No headings found; treat entire text as Discussion-like narrative
            sections["discussion"] = text.strip()
            return sections

        def norm(name: str) -> str:
            return re.sub(r"[^a-z]", "", name.lower())

        # Collect content between headings
        for i, m in enumerate(matches):
            title = m.group(1).strip()
            start = m.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            content = text[start:end].strip()
            sections[norm(title)] = content

        return sections

    def export_scientific_publication(self,
                                      messages: List[Dict[str, Any]],
                                      mode: str,
                                      manuscript_meta: Optional[Dict[str, Any]] = None,
                                      filename: Optional[str] = None,
                                      verify_citations: bool = False) -> str:
        """Export a journal-style IMRaD manuscript in Markdown.

        Args:
            messages: Conversation including assistant output with substantive content
            mode: Current processing mode used to annotate metadata
            manuscript_meta: Optional dict with keys such as title, authors, affiliations,
                corresponding, keywords, acknowledgments, funding, conflicts, data_availability,
                ethics.
            filename: Optional custom filename
            verify_citations: If True, runs citation verification and replaces the References section

        Returns:
            Absolute path to the exported manuscript file.
        """
        if not messages:
            raise ValueError("No messages available to export")

        # Get last assistant response as the source material
        assistant_msg = next((m for m in reversed(messages) if m.get("role") == "assistant"), None)
        if not assistant_msg:
            raise ValueError("No assistant response found to export")
        body_text = str(assistant_msg.get("content", "")).strip()

        # Prepare metadata
        manuscript_meta = manuscript_meta or {}
        title = manuscript_meta.get("title") or "Untitled Scientific Manuscript"
        authors = manuscript_meta.get("authors")  # string like "A. Author^1, B. Author^2*"
        affiliations = manuscript_meta.get("affiliations")  # multi-line string with ^1 labels
        corresponding = manuscript_meta.get("corresponding")
        keywords = manuscript_meta.get("keywords")  # comma-separated string
        acknowledgments = manuscript_meta.get("acknowledgments")
        funding = manuscript_meta.get("funding")
        conflicts = manuscript_meta.get("conflicts")
        data_availability = manuscript_meta.get("data_availability")
        ethics = manuscript_meta.get("ethics")

        # Attempt to extract sections from the assistant body
        sec_map = self._extract_sections_from_markdown(body_text)

        def pick(*aliases: str) -> Optional[str]:
            for a in aliases:
                key = re.sub(r"[^a-z]", "", a.lower())
                if key in sec_map and sec_map[key]:
                    return sec_map[key]
            return None

        abstract = pick("Abstract")
        introduction = pick("Introduction", "Background")
        methods = pick("Methods", "Methodology", "Materials and Methods")
        results = pick("Results", "Findings")
        discussion = pick("Discussion", "Discussion & Critical Appraisal")
        limitations = pick("Limitations")
        conclusion = pick("Conclusion", "Conclusions")
        references_raw = pick("References", "Bibliography")

        # Compose manuscript
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if not filename:
            filename = f"manuscript_{self._sanitize_filename(title)}_{timestamp}.md"

        lines: List[str] = []
        lines.append(f"# {title}\n")

        if authors:
            lines.append(f"{authors}\n")
        if affiliations:
            lines.append(f"\n{affiliations.strip()}\n")
        if corresponding:
            lines.append(f"\n**Correspondence:** {corresponding}\n")
        if keywords:
            lines.append(f"**Keywords:** {keywords}\n")

        # Manuscript metadata block from app
        lines.append("\n---\n")
        lines.append(self._generate_metadata_section(mode=mode, agent_name="Journal Exporter", total_messages=len(messages)))

        # Core sections
        lines.append("## Abstract\n\n")
        lines.append((abstract or "[Add a concise 200–300 word abstract summarizing background, objectives, methods, results, and conclusions.]") + "\n\n")

        lines.append("## Introduction\n\n")
        if introduction:
            lines.append(introduction + "\n\n")
        else:
            lines.append("[Provide background, rationale, and clearly state objectives / hypotheses.]\n\n")

        lines.append("## Methods\n\n")
        if methods:
            lines.append(methods + "\n\n")
        else:
            lines.append("[Describe study design, data sources, eligibility criteria, search strategy, outcomes, and analysis.]\n\n")

        lines.append("## Results\n\n")
        if results:
            lines.append(results + "\n\n")
        else:
            lines.append("[Report key findings with appropriate tables/figures references and effect estimates.]\n\n")

        lines.append("## Discussion\n\n")
        if discussion:
            lines.append(discussion + "\n\n")
        else:
            lines.append("[Interpret findings in context of prior literature, clinical relevance, mechanisms, and implications.]\n\n")

        lines.append("## Limitations\n\n")
        lines.append((limitations or "[State methodological and practical limitations, risks of bias, and generalizability.]") + "\n\n")

        lines.append("## Conclusion\n\n")
        lines.append((conclusion or "[Provide a clear, concise conclusion aligned to objectives with potential future work.]") + "\n\n")

        if acknowledgments:
            lines.append("## Acknowledgments\n\n")
            lines.append(acknowledgments.strip() + "\n\n")

        if funding:
            lines.append("## Funding\n\n")
            lines.append(funding.strip() + "\n\n")

        if conflicts:
            lines.append("## Conflicts of Interest\n\n")
            lines.append(conflicts.strip() + "\n\n")

        if data_availability:
            lines.append("## Data Availability\n\n")
            lines.append(data_availability.strip() + "\n\n")

        if ethics:
            lines.append("## Ethics Statement\n\n")
            lines.append(ethics.strip() + "\n\n")

        # References handling
        verified_references: List[str] = []
        if verify_citations:
            try:
                # Lazy import to avoid hard dependency at module import time
                from .core_agents.citation_orchestrator import run_citation_review  # type: ignore
                # Run citation verification against the assembled manuscript so far
                assembled_so_far = "".join(lines) + ("\n\n## References\n\n" + (references_raw or ""))
                # Use asyncio.run to execute the async coroutine in this sync context
                import asyncio as _asyncio
                verified_references = _asyncio.run(run_citation_review(assembled_so_far))  # type: ignore[arg-type]
            except Exception:
                # Fall back silently to raw references if verification fails
                verified_references = []

        lines.append("## References\n\n")
        if verified_references:
            for i, ref in enumerate(verified_references, 1):
                if ref.lstrip().startswith(str(i)):
                    lines.append(ref + "\n")
                else:
                    lines.append(f"{i}. {ref}\n")
        elif references_raw:
            lines.append(references_raw.strip() + "\n")
        else:
            lines.append("[Add APA-formatted reference list. Ensure all in-text citations are present here.]\n")

        # Footer
        lines.append(f"\n---\n\n*Manuscript exported by Aeromedical Evidence Review Framework on {self._format_timestamp()}*\n")

        # Write file
        file_path = self.output_dir / filename
        file_path.write_text("".join(lines), encoding="utf-8")
        return str(file_path.absolute())
