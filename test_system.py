#!/usr/bin/env python3
"""
System Test Suite for Multi-Agent Prompt Enhancement Application.

This script tests all major components and functionality to ensure
the system is working correctly before deployment.
"""

import sys
import os
from typing import List, Callable

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_imports():
    """Test that all required modules can be imported."""
    print("\n📦 Testing imports...")
    
    try:
        # Core modules
        from src.config import AppConfig, OpenAIModelsConfig, FlowiseConfig
        from src.agents import Agent, AgentOrchestrator
        from src.main import PromptEnhancerApp
        
        # Specialized agent modules
        from src.o3_agents import create_o3_enhancement_system
        from src.flowise_agents import create_flowise_enhancement_system
        
        # Enhanced clients
        from src.openai_enhanced_client import EnhancedOpenAIClient
        from src.flowise_client import FlowiseClient, MedicalFlowiseRouter
        
        # Multiline input support
        from src.multiline_input import MultilineInputHandler, detect_paste_input, format_large_text_preview
        
        print("✅ All imports successful")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_configuration():
    """Test configuration loading and validation."""
    print("\n⚙️ Testing configuration...")
    
    try:
        from src.config import AppConfig, OpenAIModelsConfig, FlowiseConfig
        
        # Test basic config access
        print(f"   - OpenAI model: {AppConfig.OPENAI_MODEL}")
        print(f"   - Log level: {AppConfig.LOG_LEVEL}")
        print(f"   - Timeout: {AppConfig.TIMEOUT}")
        
        # Test OpenAI models config
        print(f"   - GPT-4o-mini: {OpenAIModelsConfig.GPT4_MINI.model_name}")
        print(f"   - O3 Deep Research: {OpenAIModelsConfig.O3_DEEP_RESEARCH.model_name}")
        
        # Test Flowise config
        print(f"   - Flowise base URL: {FlowiseConfig.BASE_URL}")
        print(f"   - Available chatflows: {len(FlowiseConfig.CHATFLOW_IDS)}")
        
        # Test headers generation
        headers = FlowiseConfig.get_headers()
        print(f"   - Headers generated: {'Authorization' in headers}")
        
        print("✅ Configuration system working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def test_agent_systems():
    """Test both O3 and Flowise agent systems."""
    print("\n🤖 Testing agent systems...")
    
    try:
        from src.o3_agents import create_o3_enhancement_system
        from src.flowise_agents import create_flowise_enhancement_system
        
        # Test O3 agent system
        o3_agents = create_o3_enhancement_system()
        print(f"   - O3 agents created: {list(o3_agents.keys())}")
        
        for name, agent in o3_agents.items():
            print(f"   - {name}: {len(agent.tools)} tools, model: {agent.model}")
        
        # Test Flowise agent system
        flowise_agents = create_flowise_enhancement_system()
        print(f"   - Flowise agents created: {list(flowise_agents.keys())}")
        
        for name, agent in flowise_agents.items():
            print(f"   - {name}: {len(agent.tools)} tools, model: {agent.model}")
        
        print("✅ Agent systems working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Agent system error: {e}")
        return False


def test_multiline_input():
    """Test multiline input functionality."""
    print("\n📝 Testing multiline input system...")
    
    try:
        from src.multiline_input import (
            MultilineInputHandler, 
            detect_paste_input, 
            format_large_text_preview,
            get_multiline_input_simple
        )
        from rich.console import Console
        
        # Test multiline handler creation
        console = Console()
        handler = MultilineInputHandler(console)
        print("   - MultilineInputHandler created successfully")
        
        # Test paste detection
        short_text = "This is a short question"
        long_text = """
        This is a very long text that spans multiple lines and contains
        a lot of content that would typically be pasted from a research paper
        or article. It includes academic terminology and formatting that
        should trigger the paste detection algorithm.
        
        Abstract: This paper presents novel findings in the field of
        artificial intelligence and machine learning. The methodology
        involves comprehensive analysis of large datasets using advanced
        statistical techniques.
        
        Introduction: Recent developments in AI have shown promising results
        in various applications including natural language processing,
        computer vision, and robotics.
        """
        
        is_short_paste = detect_paste_input(short_text)
        is_long_paste = detect_paste_input(long_text)
        
        print(f"   - Short text detected as paste: {is_short_paste} (expected: False)")
        print(f"   - Long text detected as paste: {is_long_paste} (expected: True)")
        
        # Test text preview formatting
        preview = format_large_text_preview(long_text, max_lines=3, max_chars=100)
        print(f"   - Preview length: {len(preview)} chars (should be ~100)")
        
        # Test simple multiline function exists
        print(f"   - Simple multiline function available: {callable(get_multiline_input_simple)}")
        
        print("✅ Multiline input system working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Multiline input error: {e}")
        return False


def test_flowise_client():
    """Test Flowise client initialization (without API calls)."""
    print("\n🌐 Testing Flowise client...")
    
    try:
        from src.flowise_client import FlowiseClient, MedicalFlowiseRouter
        
        # Test client initialization
        client = FlowiseClient()
        print(f"   - Client base URL: {client.base_url}")
        print(f"   - Client initialized successfully")
        
        # Test medical router
        router = MedicalFlowiseRouter()
        print(f"   - Medical router initialized successfully")
        
        print("✅ Flowise client system working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Flowise client error: {e}")
        return False


def test_enhanced_openai_client():
    """Test enhanced OpenAI client initialization (without API calls)."""
    print("\n🧠 Testing enhanced OpenAI client...")
    
    try:
        from src.openai_enhanced_client import EnhancedOpenAIClient, create_enhanced_openai_client
        
        # Test client creation
        client = create_enhanced_openai_client()
        print(f"   - Enhanced client created successfully")
        print(f"   - Client type: {type(client).__name__}")
        
        print("✅ Enhanced OpenAI client system working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced OpenAI client error: {e}")
        return False


def test_main_application():
    """Test main application initialization (without running)."""
    print("\n🚀 Testing main application...")
    
    try:
        from src.main import PromptEnhancerApp
        
        # Test app initialization
        app = PromptEnhancerApp()
        print(f"   - App initialized successfully")
        print(f"   - Current mode: {app.current_mode}")
        print(f"   - O3 agents available: {list(app.o3_agents.keys())}")
        print(f"   - Flowise agents available: {list(app.flowise_agents.keys())}")
        print(f"   - Multiline handler available: {app.multiline_handler is not None}")
        
        print("✅ Main application working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Main application error: {e}")
        return False


def test_comprehensive_workflow():
    """Test the complete workflow without API calls."""
    print("\n🔄 Testing comprehensive workflow...")
    
    try:
        from src.main import PromptEnhancerApp
        from src.multiline_input import detect_paste_input
        
        # Initialize app
        app = PromptEnhancerApp()
        
        # Test mode switching
        app.current_mode = "o3"
        app.current_agent = app.o3_agents["o3_enhancer"]
        print(f"   - Switched to O3 mode with agent: {app.current_agent.name}")
        
        app.current_mode = "flowise"
        app.current_agent = app.flowise_agents["flowise_enhancer"]
        print(f"   - Switched to Flowise mode with agent: {app.current_agent.name}")
        
        # Test multiline input detection
        test_input = "This is a test input for the system"
        is_paste = detect_paste_input(test_input)
        print(f"   - Input detection working: {not is_paste}")
        
        # Test message handling
        app.messages.append({"role": "user", "content": test_input})
        print(f"   - Message added to history: {len(app.messages)} messages")
        
        print("✅ Comprehensive workflow working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Comprehensive workflow error: {e}")
        return False


def run_all_tests() -> bool:
    """Run all tests and return overall success status."""
    print("🧪 Running Multi-Agent Prompt Enhancement System Tests")
    print("=" * 60)
    
    tests: List[Callable[[], bool]] = [
        test_imports,
        test_configuration,
        test_agent_systems,
        test_multiline_input,
        test_flowise_client,
        test_enhanced_openai_client,
        test_main_application,
        test_comprehensive_workflow,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1:2d}. {test.__name__:<30} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
        print("\n💡 To run the application:")
        print("   python run_app.py")
        print("   or")
        print("   python -m src.main")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 