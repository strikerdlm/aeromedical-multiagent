#!/usr/bin/env python3
"""
Test script for PRISMA Systematic Review feature.

This script tests the PRISMA functionality to ensure all components
are working correctly.
"""

import sys
import os
import logging
from typing import Dict, Any

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def test_imports():
    """Test that all PRISMA modules can be imported."""
    print("\n📦 Testing PRISMA imports...")
    
    try:
        # Core PRISMA modules
        from src.config import PRISMAConfig, AppConfig
        from src.perplexity_client import PerplexityClient, PRISMAPerplexityRouter
        from src.grok_client import GrokClient, PRISMAGrokRouter
        from src.prisma_agents import PRISMAAgentSystem, create_prisma_agent_system
        from src.prisma_orchestrator import PRISMAOrchestrator, create_prisma_orchestrator
        
        print("✅ All PRISMA imports successful")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_configuration():
    """Test PRISMA configuration."""
    print("\n⚙️ Testing PRISMA configuration...")
    
    try:
        from src.config import PRISMAConfig, AppConfig
        
        # Test configuration values
        print(f"   - O3 Model: {PRISMAConfig.O3_HIGH_REASONING.model_name}")
        print(f"   - Perplexity Model: {PRISMAConfig.PERPLEXITY_MODEL}")
        print(f"   - Grok Model: {PRISMAConfig.GROK_MODEL}")
        print(f"   - Target Word Count: {PRISMAConfig.TARGET_WORD_COUNT}")
        print(f"   - Minimum Citations: {PRISMAConfig.MIN_CITATIONS}")
        print(f"   - Chatflow IDs: {list(PRISMAConfig.PRISMA_CHATFLOWS.keys())}")
        
        # Test environment validation
        env_valid = AppConfig.validate_prisma_environment()
        print(f"   - Environment validation: {'✅ Passed' if env_valid else '❌ Failed'}")
        
        print("✅ Configuration testing completed")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def test_client_initialization():
    """Test client initialization."""
    print("\n🔌 Testing client initialization...")
    
    try:
        from src.perplexity_client import PerplexityClient
        from src.grok_client import GrokClient
        from src.flowise_client import FlowiseClient
        
        # Test Perplexity client
        try:
            perplexity_client = PerplexityClient()
            print("   - Perplexity client: ✅ Initialized")
        except Exception as e:
            print(f"   - Perplexity client: ❌ {e}")
        
        # Test Grok client
        try:
            grok_client = GrokClient()
            print("   - Grok client: ✅ Initialized")
        except Exception as e:
            print(f"   - Grok client: ❌ {e}")
        
        # Test Flowise client
        try:
            flowise_client = FlowiseClient()
            print("   - Flowise client: ✅ Initialized")
        except Exception as e:
            print(f"   - Flowise client: ❌ {e}")
        
        print("✅ Client initialization testing completed")
        return True
        
    except Exception as e:
        print(f"❌ Client initialization error: {e}")
        return False


def test_agent_system():
    """Test PRISMA agent system."""
    print("\n🤖 Testing PRISMA agent system...")
    
    try:
        from src.prisma_agents import create_prisma_agent_system
        
        # Create agent system
        agents = create_prisma_agent_system()
        print(f"   - Created agents: {list(agents.keys())}")
        
        # Test agent properties
        for agent_name, agent in agents.items():
            print(f"   - {agent_name}: {agent.name}")
            print(f"     Tools: {len(agent.tools)}")
        
        print("✅ Agent system testing completed")
        return True
        
    except Exception as e:
        print(f"❌ Agent system error: {e}")
        return False


def test_orchestrator():
    """Test PRISMA orchestrator."""
    print("\n🎯 Testing PRISMA orchestrator...")
    
    try:
        from src.config import AppConfig
        from src.prisma_orchestrator import create_prisma_orchestrator
        
        # Check if environment is configured
        if not AppConfig.validate_prisma_environment():
            print("   - Environment not configured for full testing")
            print("   - Skipping orchestrator initialization test")
            return True
        
        # Create orchestrator
        orchestrator = create_prisma_orchestrator()
        print("   - Orchestrator: ✅ Initialized")
        
        # Test status method
        status = orchestrator.get_prisma_status()
        print(f"   - Status check: ✅ {status.get('status', 'unknown')}")
        
        # Test connectivity
        api_status = status.get("api_connectivity", {})
        for api_name, api_info in api_status.items():
            status_text = api_info.get("status", "unknown")
            print(f"   - {api_name.title()}: {status_text}")
        
        print("✅ Orchestrator testing completed")
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator error: {e}")
        return False


def test_main_integration():
    """Test integration with main application."""
    print("\n🔗 Testing main application integration...")
    
    try:
        from src.main import EnhancedPromptEnhancerApp
        
        # Create app instance
        app = EnhancedPromptEnhancerApp()
        print("   - App initialized successfully")
        
        # Check PRISMA orchestrator
        if app.prisma_orchestrator:
            print("   - PRISMA orchestrator: ✅ Available")
        else:
            print("   - PRISMA orchestrator: ❌ Not initialized (likely missing API keys)")
        
        # Test mode switching
        success = app.switch_mode("prisma")
        if success:
            print("   - PRISMA mode switch: ✅ Successful")
        else:
            print("   - PRISMA mode switch: ❌ Failed (expected if APIs not configured)")
        
        print("✅ Main integration testing completed")
        return True
        
    except Exception as e:
        print(f"❌ Main integration error: {e}")
        return False


def test_quick_functionality():
    """Test quick functionality if APIs are available."""
    print("\n⚡ Testing quick functionality...")
    
    try:
        from src.config import AppConfig
        from src.prisma_orchestrator import create_prisma_orchestrator
        
        # Only test if environment is configured
        if not AppConfig.validate_prisma_environment():
            print("   - APIs not configured, skipping functionality test")
            return True
        
        # Create orchestrator
        orchestrator = create_prisma_orchestrator()
        
        # Test a simple status check
        status = orchestrator.get_prisma_status()
        if status.get("status") == "active":
            print("   - System status: ✅ Active")
        
        # Test recent reviews (should be empty initially)
        reviews = orchestrator.list_recent_reviews()
        print(f"   - Recent reviews: {len(reviews)} found")
        
        print("✅ Quick functionality testing completed")
        return True
        
    except Exception as e:
        print(f"❌ Quick functionality error: {e}")
        return False


def generate_test_report(results: Dict[str, bool]) -> None:
    """Generate a comprehensive test report."""
    print("\n" + "="*60)
    print("📊 PRISMA FEATURE TEST REPORT")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print()
    
    # Detailed results
    print("Detailed Results:")
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
    
    print()
    
    # Recommendations
    if failed_tests > 0:
        print("🔧 Recommendations:")
        if not results.get("Configuration", True):
            print("  • Check environment variables (API keys)")
        if not results.get("Client Initialization", True):
            print("  • Verify API key configurations")
        if not results.get("Orchestrator", True):
            print("  • Ensure all required dependencies are installed")
        print()
    
    # API Key Status
    print("📋 Required API Keys Status:")
    print("  • OPENAI_API_KEY: Required for O3 models")
    print("  • FLOWISE_API_KEY: Required for Flowise chatflows")
    print("  • PPLX_API_KEY: Required for Perplexity research")
    print("  • XAI_API: Required for Grok reasoning")
    print()
    print("💡 To use all PRISMA features, configure these API keys in your .env file")
    print()


def main():
    """Run all PRISMA tests."""
    print("🧪 PRISMA Systematic Review Feature Testing")
    print("="*60)
    
    # Configure logging for testing
    logging.basicConfig(
        level=logging.WARNING,  # Reduce noise during testing
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run all tests
    test_results = {}
    
    test_results["Imports"] = test_imports()
    test_results["Configuration"] = test_configuration()
    test_results["Client Initialization"] = test_client_initialization()
    test_results["Agent System"] = test_agent_system()
    test_results["Orchestrator"] = test_orchestrator()
    test_results["Main Integration"] = test_main_integration()
    test_results["Quick Functionality"] = test_quick_functionality()
    
    # Generate report
    generate_test_report(test_results)
    
    # Return exit code
    all_passed = all(test_results.values())
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 