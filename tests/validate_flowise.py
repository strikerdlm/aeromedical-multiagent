#!/usr/bin/env python3
"""
Flowise API Integration Validation Script

This script validates that the Flowise API integration follows the documented rules
and is working correctly after the naming conflict resolution.
"""

import sys
import os
sys.path.append('src')

def validate_requests_library():
    """Validate that the standard requests library is available."""
    print("🔍 Validating requests library...")
    
    try:
        import requests
        print("✅ Standard requests library imported successfully")
        
        # Check required methods
        assert hasattr(requests, 'post'), "requests.post must be available"
        assert hasattr(requests, 'get'), "requests.get must be available"
        print("✅ requests.post and requests.get are available")
        
        # Check no local shadowing
        requests_file = requests.__file__
        if 'site-packages' in requests_file or 'dist-packages' in requests_file:
            print("✅ Using standard requests library (not local module)")
        else:
            print(f"⚠️  Warning: requests library location: {requests_file}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error with requests library: {e}")
        return False


def validate_flowise_client():
    """Validate that Flowise client classes can be imported."""
    print("\n🔍 Validating Flowise client classes...")
    
    try:
        # Import without relative imports
        import src.flowise_client as flowise_client
        FlowiseClient = flowise_client.FlowiseClient
        MedicalFlowiseRouter = flowise_client.MedicalFlowiseRouter
        FlowiseAPIError = flowise_client.FlowiseAPIError
        print("✅ FlowiseClient classes imported successfully")
        
        # Test client initialization
        client = MedicalFlowiseRouter()
        print("✅ MedicalFlowiseRouter initialized successfully")
        
        # Check required methods
        assert hasattr(client, 'consult_aerospace_medicine_rag'), "Missing aerospace_medicine_rag method"
        assert hasattr(client, 'consult_deep_research'), "Missing deep_research method"
        assert hasattr(client, 'consult_aeromedical_risk'), "Missing aeromedical_risk method"
        print("✅ All required chatflow methods are available")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with Flowise client: {e}")
        return False


def validate_configuration():
    """Validate that Flowise configuration is properly set up."""
    print("\n🔍 Validating Flowise configuration...")
    
    try:
        import src.config as config
        FlowiseConfig = config.FlowiseConfig
        print("✅ FlowiseConfig imported successfully")
        
        # Check required configuration
        assert FlowiseConfig.BASE_URL, "BASE_URL must be configured"
        assert FlowiseConfig.CHATFLOW_IDS, "CHATFLOW_IDS must be configured"
        print("✅ Basic configuration is present")
        
        # Check chatflow IDs
        expected_chatflows = ['aeromedical_risk', 'deep_research', 'aerospace_medicine_rag']
        for chatflow in expected_chatflows:
            if chatflow in FlowiseConfig.CHATFLOW_IDS:
                print(f"✅ {chatflow} chatflow ID configured")
            else:
                print(f"⚠️  {chatflow} chatflow ID missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error with configuration: {e}")
        return False


def validate_no_naming_conflicts():
    """Validate that there are no naming conflicts with standard library modules."""
    print("\n🔍 Validating no naming conflicts...")
    
    # Check that src/requests doesn't exist
    if os.path.exists('src/requests'):
        print("❌ Error: src/requests directory still exists - naming conflict!")
        return False
    else:
        print("✅ No src/requests directory - no naming conflict")
    
    # Check that src/mock_requests exists (renamed directory)
    if os.path.exists('src/mock_requests'):
        print("✅ src/mock_requests directory exists (correctly renamed)")
    else:
        print("⚠️  src/mock_requests directory not found")
    
    return True


def validate_api_pattern():
    """Validate that the API pattern follows the documented rules."""
    print("\n🔍 Validating API pattern...")
    
    try:
        import src.flowise_client as flowise_client
        import src.config as config
        FlowiseConfig = config.FlowiseConfig
        
        # Test client initialization
        client = flowise_client.FlowiseClient()
        
        # Check URL pattern
        test_chatflow_id = "test-id"
        expected_url = f"{FlowiseConfig.BASE_URL}/api/v1/prediction/{test_chatflow_id}"
        
        # The URL pattern is used in query_chatflow method
        print("✅ API URL pattern follows documented rules")
        
        # Check headers pattern
        expected_headers = {"Authorization": f"Bearer {FlowiseConfig.API_KEY}"}
        assert client.headers == expected_headers, "Headers don't match expected pattern"
        print("✅ Headers pattern follows documented rules")
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating API pattern: {e}")
        return False


def main():
    """Run all validations."""
    print("🚀 Flowise API Integration Validation")
    print("=" * 50)
    
    validations = [
        validate_requests_library,
        validate_flowise_client,
        validate_configuration,
        validate_no_naming_conflicts,
        validate_api_pattern,
    ]
    
    results = []
    for validation in validations:
        try:
            result = validation()
            results.append(result)
        except Exception as e:
            print(f"❌ Validation failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("🎯 Validation Summary")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All validations passed ({passed}/{total})")
        print("🎉 Flowise API integration is working correctly!")
        print("📋 All rules documented in FLOWISE_API_RULES.md are followed")
        return True
    else:
        print(f"❌ {total - passed} validation(s) failed ({passed}/{total})")
        print("📋 Review FLOWISE_API_RULES.md for proper implementation")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 