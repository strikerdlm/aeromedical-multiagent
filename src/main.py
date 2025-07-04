"""
Multi-Agent Prompt Enhancement Application.

This is the main application file that provides a text-based interface
for the multi-agent prompt enhancement system with separate O3 and Flowise flows.
"""

from __future__ import annotations

import logging
import sys
import os
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown

from .config import AppConfig
from .agents import AgentOrchestrator
from .o3_agents import create_o3_enhancement_system
from .flowise_agents import create_flowise_enhancement_system
from .flowise_client import FlowiseAPIError
from .multiline_input import MultilineInputHandler, detect_paste_input, format_large_text_preview


# Set up logging with proper Unicode support
def setup_logging():
    """Set up logging with UTF-8 encoding support for Windows compatibility."""
    # Windows-specific console encoding fix
    if sys.platform.startswith('win'):
        try:
            # Try to set console to UTF-8 on Windows
            os.system('chcp 65001 >nul 2>&1')
        except Exception:
            pass  # Ignore if this fails
    
    # Clear any existing handlers
    logging.getLogger().handlers.clear()
    
    # Create formatters
    formatter = logging.Formatter(AppConfig.LOG_FORMAT)
    
    # Console handler with UTF-8 support
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # File handler with explicit UTF-8 encoding
    file_handler = logging.FileHandler('prompt_enhancer.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, AppConfig.LOG_LEVEL))
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

setup_logging()

logger = logging.getLogger(__name__)


class PromptEnhancerApp:
    """
    Main application class for the Multi-Agent Prompt Enhancement system.
    
    This class provides a text-based interface for users to choose between
    O3 Deep Research and Flowise API processing flows with multiline input support.
    """
    
    def __init__(self):
        """Initialize the prompt enhancer application."""
        self.console = Console()
        self.multiline_handler = MultilineInputHandler(self.console)
        self.orchestrator = AgentOrchestrator()
        
        # Create both agent systems
        self.o3_agents = create_o3_enhancement_system()
        self.flowise_agents = create_flowise_enhancement_system()
        
        self.messages: List[Dict[str, Any]] = []
        
        # Current processing mode and agent
        self.current_mode: str = "menu"  # "menu", "o3", "flowise"
        self.current_agent = None
        
        logger.info("Prompt Enhancer App initialized successfully")
    
    def display_welcome_message(self) -> None:
        """Display the welcome message and system overview."""
        welcome_text = """
        # 🚀 Advanced Multi-Agent Prompt Enhancement System
        
        Welcome to the next-generation prompt enhancement system with **two specialized processing flows**:
        
        ## 🔬 **O3 Deep Research Flow**
        - **o3-deep-research-2025-06-26**: Optimized for in-depth synthesis and research
        - **o3 with Web Search**: Enhanced with real-time information and high reasoning
        - **Intelligent Classification**: Automatically selects the best O3 model
        - **Perfect for**: Scientific research, technology analysis, complex reasoning
        
        ## 🌐 **Flowise API Flow**  
        - **Specialized Knowledge Bases**: Medical, NASA, PubMed, Clinical resources
        - **RAG-Enhanced Processing**: Retrieval-Augmented Generation with domain expertise
        - **Multiple Chatflows**: physiology_rag, nasa_hrp, deep_research, agentic_rag, pubmed
        - **Perfect for**: Medical questions, research literature, specialized domain knowledge
        
        ## 📝 **Multiline Input Support**
        - **Paste Large Text Blocks**: Perfect for research papers, articles, and context
        - **Smart Input Detection**: Automatically handles single-line or multiline input
        - **Multiple Input Modes**: Type '>>>' for multiline mode or paste directly
        - **Progress Tracking**: Visual feedback for large inputs
        
        ## How to Use:
        1. **Choose Your Processing Flow** from the main menu
        2. **Enter Your Question** - single line or multiline with large context blocks
        3. **Get Comprehensive Results** from the most appropriate AI system
        
        **You now have granular control over which AI system processes your requests!**
        """
        
        self.console.print(Panel(Markdown(welcome_text), title="🤖 Advanced AI Prompt Enhancer", border_style="bright_blue"))
    
    def display_main_menu(self) -> None:
        """Display the main processing flow selection menu."""
        menu_text = """
        # 🎯 Choose Your Processing Flow
        
        Select which AI system you want to use for processing your request:
        """
        
        self.console.print(Panel(Markdown(menu_text), title="Main Menu", border_style="cyan"))
        
        table = Table(title="Available Processing Flows")
        table.add_column("Option", style="cyan", width=8)
        table.add_column("Flow Name", style="green", width=20)
        table.add_column("Best For", style="yellow", width=40)
        table.add_column("AI Models", style="magenta", width=25)
        
        table.add_row(
            "1", 
            "O3 Deep Research", 
            "Scientific research, complex analysis, reasoning tasks", 
            "o3-deep-research, o3+web"
        )
        table.add_row(
            "2", 
            "Flowise API", 
            "Medical questions, domain expertise, literature search", 
            "Specialized RAG chatflows"
        )
        table.add_row(
            "3", 
            "DeepResearch Flowise", 
            "Comprehensive research with Flowise deep knowledge", 
            "deep_research chatflow"
        )
        table.add_row(
                    "4", 
        "Aeromedical Risk", 
        "Aerospace medicine risk assessment and analysis", 
        "aeromedical_risk chatflow (requires CHATFLOW_AEROMEDICAL_RISK env var)"
        )
        table.add_row(
            "5", 
            "Help & Info", 
            "Learn more about each processing flow", 
            "Information only"
        )
        table.add_row(
            "6", 
            "Exit", 
            "Quit the application", 
            "N/A"
        )
        
        self.console.print(table)
    
    def display_flow_help(self) -> None:
        """Display detailed help about each processing flow."""
        help_text = """
        # 📖 Processing Flow Details
        
        ## 🔬 O3 Deep Research Flow
        
        **When to use:**
        - Complex scientific or technical questions
        - Multi-step reasoning and analysis
        - Current events (uses web search)
        - General knowledge with deep analysis
        - Technology comparisons and explanations
        
        **How it works:**
        1. **O3 Prompt Enhancer** - Analyzes and enhances your prompt for O3 models
        2. **O3 Processor** - Routes to either:
           - `o3-deep-research-2025-06-26` for complex analysis
           - `o3 with web search` for current information
        
        **Example questions:**
        - "Explain quantum computing and its applications in cryptography"
        - "What are the latest developments in artificial intelligence?"
        - "How does photosynthesis work at the molecular level?"
        
        ---
        
        ## 🌐 Flowise API Flow
        
        **When to use:**
        - Medical and physiology questions
        - NASA and space medicine research
        - PubMed literature searches
        - Clinical reference needs
        - Aviation medicine questions
        
        **How it works:**
        1. **Flowise Prompt Enhancer** - Optimizes your prompt for RAG systems
        2. **Flowise Processor** - Routes to specialized chatflows:
           - `physiology_rag` - Human physiology and medical questions
           - `nasa_hrp` - NASA Human Research Program
           - `pubmed` - Medical literature search
           - `deep_research` - Comprehensive research analysis
           - `agentic_rag` - Multi-agent RAG processing
        
        **Example questions:**
        - "What are the cardiovascular effects of microgravity?"
        - "Find recent research on diabetes treatment protocols"
        - "Explain the physiological changes during space flight"
        
        ---
        
        ## 🎯 DeepResearch Flowise Flow
        
        **When to use:**
        - Comprehensive research requiring deep knowledge synthesis
        - Academic and scientific research questions
        - Multi-source analysis and compilation
        - Complex research topics requiring RAG expertise
        - When you want direct access to Flowise's most powerful research capabilities
        
        **How it works:**
        - **Direct DeepResearch Agent** - Bypasses routing and directly queries the 
          `deep_research` chatflow (ID: 43677137-d307-4ff4-96c9-5019b6e10879)
        - **Specialized Knowledge Bases** - Accesses comprehensive research databases
        - **Advanced RAG Processing** - Uses multi-source retrieval and synthesis
        - **Streaming Responses** - Provides real-time response generation
        
        **Perfect for:**
        - Literature reviews and research compilation
        - Scientific and technical analysis
        - Cross-disciplinary research questions
        - Advanced domain expertise queries
        - Research synthesis from multiple sources
        
        **Example questions:**
        - "Provide a comprehensive analysis of CRISPR gene editing applications"
        - "Research the latest advances in renewable energy storage technologies"
        - "Analyze the intersection of AI and climate change research"
        
        ---
        
        ## 🚁 Aeromedical Risk Flow
        
        **When to use:**
        - Aviation medical risk assessment and analysis
        - Aerospace physiology questions
        - Flight safety medical considerations
        - Pilot medical certification guidance
        - Aviation medicine risk factors
        - Aerospace health and safety analysis
        
        **How it works:**
        - **Direct Aeromedical Risk Agent** - Bypasses routing and directly queries the 
          `aeromedical_risk` chatflow (requires CHATFLOW_AEROMEDICAL_RISK environment variable)
        - **Specialized Aerospace Medicine Knowledge** - Accesses aviation medical databases
        - **Conservative Risk Assessment** - Safety-first approach to risk evaluation
        - **Flight Safety Focus** - Prioritizes aviation safety and medical standards
        
        **Perfect for:**
        - Aviation medical risk assessments
        - Aerospace physiology analysis
        - Flight safety medical guidance
        - Pilot health and fitness evaluations
        - Aviation medicine risk factor analysis
        - Aerospace health and safety consultations
        
        **Example questions:**
        - "What are the cardiovascular risk factors for commercial pilots?"
        - "Assess the medical risks of high-altitude flight operations"
        - "What are the physiological effects of long-duration space flight?"
        - "Evaluate the medical fitness requirements for drone pilots"
        
        ---
        
        ## 📝 Multiline Input Features
        
        **How to use multiline input:**
        - Type `>>>` to enter multiline mode
        - Paste large text blocks directly
        - Type `/send` on a new line to finish
        - Press Ctrl+D (Linux/Mac) or Ctrl+Z (Windows) to finish
        
        **Perfect for:**
        - Research papers and articles as context
        - Large data blocks
        - Multi-paragraph questions
        - Code snippets and technical documentation
        
        **Press any key to return to the main menu...**
        """
        
        self.console.print(Panel(Markdown(help_text), title="📖 Flow Help", border_style="yellow"))
        input()  # Wait for user to press a key
    
    def get_menu_choice(self) -> str:
        """Get the user's menu choice."""
        while True:
            choice = Prompt.ask(
                "\n[bold cyan]Select your processing flow[/bold cyan] (1-6)",
                choices=["1", "2", "3", "4", "5", "6"],
                default="1"
            )
            
            if choice == "1":
                return "o3"
            elif choice == "2":
                return "flowise"
            elif choice == "3":
                return "deepresearch_flowise"
            elif choice == "4":
                return "aeromedical_risk"
            elif choice == "5":
                self.display_flow_help()
                self.display_main_menu()
                continue
            elif choice == "6":
                return "exit"
    
    def display_agent_status(self) -> None:
        """Display current agent status and available options."""
        if not self.current_agent:
            self.console.print("No active agent - you're in the main menu")
            return
            
        table = Table(title=f"Current Agent: {self.current_agent.name}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Processing Mode", self.current_mode.upper())
        table.add_row("Agent Name", self.current_agent.name)
        table.add_row("Available Tools", str(len(self.current_agent.tools)))
        table.add_row("Model", self.current_agent.model)
        table.add_row("Messages in History", str(len(self.messages)))
        table.add_row("Multiline Support", "✅ Enabled")
        
        self.console.print(table)
    
    def display_help(self) -> None:
        """Display help information."""
        help_text = f"""
        ## Available Commands:
        
        - **Your prompt/question** - Enter any request for enhancement and processing
        - **>>>** - Enter multiline mode for large text blocks
        - **/menu** - Return to the main processing flow selection menu
        - **/help** - Show this help message
        - **/status** - Show current agent status
        - **/history** - Show conversation history
        - **/clear** - Clear conversation history
        - **/quit** or **/exit** - Exit the application
        
        ## Current Mode: {self.current_mode.upper()}
        
        {"### O3 Deep Research Mode" if self.current_mode == "o3" else "### Flowise API Mode" if self.current_mode == "flowise" else "### DeepResearch Flowise Mode" if self.current_mode == "deepresearch_flowise" else "### Aeromedical Risk Mode" if self.current_mode == "aeromedical_risk" else "### Main Menu"}
        
        {"- Optimized for scientific research and complex analysis" if self.current_mode == "o3" else "- Optimized for medical questions and domain expertise" if self.current_mode == "flowise" else "- Direct access to Flowise deep_research chatflow" if self.current_mode == "deepresearch_flowise" else "- Direct access to Flowise aeromedical_risk chatflow" if self.current_mode == "aeromedical_risk" else "- Select a processing flow to begin"}
        {"- Uses o3-deep-research and o3+web models" if self.current_mode == "o3" else "- Uses specialized Flowise chatflows" if self.current_mode == "flowise" else "- Uses deep_research RAG with comprehensive knowledge synthesis" if self.current_mode == "deepresearch_flowise" else "- Uses aeromedical_risk RAG with aviation medicine expertise" if self.current_mode == "aeromedical_risk" else ""}
        
        ## Multiline Input Options:
        
        - **Type `>>>`** - Enter dedicated multiline mode with instructions
        - **Paste directly** - Large text blocks are automatically detected
        - **Type `MULTILINE`** - Alternative way to enter multiline mode
        - **Type `/send`** - Finish multiline input (or use Ctrl+D)
        
        ## Example Questions:
        
        {"- 'Explain quantum computing applications'" if self.current_mode == "o3" else "- 'What are the cardiovascular effects of microgravity?'" if self.current_mode == "flowise" else "- 'Comprehensive analysis of CRISPR applications'" if self.current_mode == "deepresearch_flowise" else "- 'What are the cardiovascular risk factors for pilots?'" if self.current_mode == "aeromedical_risk" else "- First select a processing flow from the menu"}
        {"- 'Latest developments in AI research'" if self.current_mode == "o3" else "- 'Find recent diabetes treatment research'" if self.current_mode == "flowise" else "- 'Research renewable energy storage advances'" if self.current_mode == "deepresearch_flowise" else "- 'Assess medical risks of high-altitude flight'" if self.current_mode == "aeromedical_risk" else ""}
        {"- 'How does photosynthesis work?'" if self.current_mode == "o3" else "- 'Physiological changes during space flight'" if self.current_mode == "flowise" else "- 'AI and climate change research synthesis'" if self.current_mode == "deepresearch_flowise" else "- 'Evaluate pilot medical fitness requirements'" if self.current_mode == "aeromedical_risk" else ""}
        """
        
        self.console.print(Panel(Markdown(help_text), title="📖 Help", border_style="yellow"))
    
    def display_conversation_history(self) -> None:
        """Display the conversation history."""
        if not self.messages:
            self.console.print("💭 No conversation history yet.")
            return
        
        self.console.print(Panel(f"📜 Conversation History - {self.current_mode.upper()} Mode", border_style="magenta"))
        
        for i, message in enumerate(self.messages):
            role = message.get("role", "unknown")
            content = message.get("content", "")
            
            if role == "user":
                # Show preview for long content
                if len(content) > 200:
                    preview = format_large_text_preview(content, max_lines=3, max_chars=200)
                    self.console.print(f"[bold blue]You:[/bold blue] {preview}")
                else:
                    self.console.print(f"[bold blue]You:[/bold blue] {content}")
            elif role == "assistant":
                if len(content) > 200:
                    preview = format_large_text_preview(content, max_lines=3, max_chars=200)
                    self.console.print(f"[bold green]Assistant:[/bold green] {preview}")
                else:
                    self.console.print(f"[bold green]Assistant:[/bold green] {content}")
            elif role == "tool":
                self.console.print(f"[bold yellow]Tool Result:[/bold yellow] {content[:100]}...")
            
            if i < len(self.messages) - 1:
                self.console.print("---")
    
    def get_user_input(self) -> str:
        """
        Get user input with multiline support.
        
        Returns:
            The user's input string
        """
        mode_emoji = "🔬" if self.current_mode == "o3" else "🌐" if self.current_mode in ["flowise", "deepresearch_flowise"] else "🚁"
        prompt_text = f"{self.current_mode.upper()} Mode - Enter your prompt"
        
        # Use the multiline input handler
        user_input = self.multiline_handler.get_single_or_multiline_input(
            prompt_text=prompt_text,
            mode_emoji=mode_emoji
        )
        
        return user_input.strip()
    
    def handle_user_input(self, user_input: str) -> bool:
        """
        Handle user input and commands.
        
        Args:
            user_input: The user's input string
            
        Returns:
            True to continue, False to exit
        """
        user_input = user_input.strip()
        
        # Handle commands
        if user_input.startswith('/'):
            command = user_input[1:].lower()
            
            if command in ['quit', 'exit']:
                return False
            elif command == 'menu':
                self.current_mode = "menu"
                self.current_agent = None
                self.console.print("🔄 Returned to main menu.")
                return True
            elif command == 'help':
                self.display_help()
                return True
            elif command == 'status':
                self.display_agent_status()
                return True
            elif command == 'history':
                self.display_conversation_history()
                return True
            elif command == 'clear':
                self.messages = []
                self.console.print("🧹 Conversation history cleared.")
                return True
            else:
                self.console.print(f"❌ Unknown command: {command}. Type /help for available commands.")
                return True
        
        # Handle regular user input
        if not user_input:
            self.console.print("💬 Please enter a prompt or command.")
            return True
        
        # If we're in menu mode, we shouldn't process requests
        if self.current_mode == "menu":
            self.console.print("⚠️  Please select a processing flow first from the main menu.")
            return True
        
        # Check if this looks like pasted content and show detection
        if detect_paste_input(user_input):
            self.console.print("[dim]📋 Large text block detected - processing with enhanced context handling...[/dim]")
        
        return self.process_user_request(user_input)
    
    def process_user_request(self, user_input: str) -> bool:
        """
        Process a user request through the selected agent system.
        
        Args:
            user_input: The user's request
            
        Returns:
            True to continue, False to exit
        """
        try:
            # Add user message to conversation
            self.messages.append({"role": "user", "content": user_input})
            
            # Show processing message with input summary for large text
            if len(user_input) > 500:
                lines = len(user_input.split('\n'))
                words = len(user_input.split())
                self.console.print(f"\n🤔 Processing your request ({lines} lines, {words} words) with [bold]{self.current_agent.name}[/bold] ({self.current_mode.upper()} mode)...")
            else:
                self.console.print(f"\n🤔 Processing your request with [bold]{self.current_agent.name}[/bold] ({self.current_mode.upper()} mode)...")
            
            # Execute the current agent
            with self.console.status("[bold green]Thinking..."):
                response = self.orchestrator.run_full_turn(self.current_agent, self.messages)
            
            # Update current agent and messages
            if response.agent:
                self.current_agent = response.agent
            self.messages.extend(response.messages)
            
            # Display the response
            if response.messages:
                last_message = response.messages[-1]
                if last_message.get("role") == "assistant" and last_message.get("content"):
                    self.console.print(Panel(
                        last_message["content"],
                        title=f"🤖 {self.current_agent.name} ({self.current_mode.upper()})",
                        border_style="green"
                    ))
            
            self.console.print(f"\n✅ Request processed. Current agent: [bold]{self.current_agent.name}[/bold]")
            
        except FlowiseAPIError as e:
            logger.error(f"Flowise API error: {e}")
            self.console.print(f"❌ Flowise API Error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing request: {e}")
            self.console.print(f"❌ Error processing request: {e}")
        
        return True
    
    def run(self) -> None:
        """Run the main application loop."""
        try:
            self.display_welcome_message()
            
            while True:
                # Show menu if we're in menu mode
                if self.current_mode == "menu":
                    self.display_main_menu()
                    choice = self.get_menu_choice()
                    
                    if choice == "exit":
                        break
                    elif choice == "o3":
                        self.current_mode = "o3"
                        self.current_agent = self.o3_agents["o3_enhancer"]
                        self.console.print(f"\n🔬 [bold green]O3 Deep Research Mode Activated[/bold green]")
                        self.console.print("You can now enter your questions for O3 model processing.")
                        self.console.print("Type [bold]/menu[/bold] to return to the main menu anytime.")
                        self.console.print("Type [bold]>>>[/bold] for multiline input mode (use '/send' to finish).\n")
                    elif choice == "flowise":
                        self.current_mode = "flowise"
                        self.current_agent = self.flowise_agents["flowise_enhancer"]
                        self.console.print(f"\n🌐 [bold green]Flowise API Mode Activated[/bold green]")
                        self.console.print("You can now enter your questions for Flowise chatflow processing.")
                        self.console.print("Type [bold]/menu[/bold] to return to the main menu anytime.")
                        self.console.print("Type [bold]>>>[/bold] for multiline input mode (use '/send' to finish).\n")
                    elif choice == "deepresearch_flowise":
                        self.current_mode = "deepresearch_flowise"
                        self.current_agent = self.flowise_agents["deep_research"]
                        self.console.print(f"\n🌐 [bold green]DeepResearch Flowise Mode Activated[/bold green]")
                        self.console.print("You can now enter your questions for DeepResearch Flowise processing.")
                        self.console.print("Type [bold]/menu[/bold] to return to the main menu anytime.")
                        self.console.print("Type [bold]>>>[/bold] for multiline input mode (use '/send' to finish).\n")
                    elif choice == "aeromedical_risk":
                        self.current_mode = "aeromedical_risk"
                        self.current_agent = self.flowise_agents["aeromedical_risk"]
                        self.console.print(f"\n🚁 [bold green]Aeromedical Risk Mode Activated[/bold green]")
                        self.console.print("You can now enter your questions for aeromedical risk assessment.")
                        self.console.print("Type [bold]/menu[/bold] to return to the main menu anytime.")
                        self.console.print("Type [bold]>>>[/bold] for multiline input mode (use '/send' to finish).\n")
                    
                    continue
                
                # Get user input for processing
                try:
                    user_input = self.get_user_input()
                except (KeyboardInterrupt, EOFError):
                    self.console.print("\n👋 Goodbye!")
                    break
                
                # Handle the input
                should_continue = self.handle_user_input(user_input)
                if not should_continue:
                    break
            
        except Exception as e:
            logger.error(f"Fatal error in main loop: {e}")
            self.console.print(f"❌ Fatal error: {e}")
        finally:
            self.console.print("\n✨ Thank you for using the Multi-Agent Prompt Enhancement System!")


def main() -> None:
    """Main entry point for the application."""
    try:
        # Validate environment variables
        if not AppConfig.validate_environment():
            sys.exit(1)
        
        # Check chatflow availability
        chatflow_status = AppConfig.validate_chatflow_ids()
        available_chatflows = [name for name, available in chatflow_status.items() if available]
        
        if not available_chatflows:
            print("⚠️  Warning: No Flowise chatflow IDs configured.")
            print("   Some features may not be available.")
            print("   Configure CHATFLOW_* environment variables for full functionality.")
        
        # Create and run the application
        app = PromptEnhancerApp()
        app.run()
        
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user.")
    except Exception as e:
        logger.error(f"Fatal application error: {e}")
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 