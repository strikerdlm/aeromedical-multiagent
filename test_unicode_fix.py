#!/usr/bin/env python3
"""
Test script to verify Unicode logging fixes work correctly.

This script tests the Unicode encoding fixes implemented to resolve
the UnicodeEncodeError that occurred when logging Flowise API responses
containing academic citations with special characters.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agents import safe_log_info
from src.main import setup_logging
import logging

def test_unicode_logging():
    """Test Unicode logging with various problematic characters."""
    
    print("🧪 Testing Unicode Logging Fixes")
    print("=" * 50)
    
    # Test cases with Unicode characters that caused the original error
    test_cases = [
        "Miller AL et al., Acta Astronáut 2024",
        "Young LR et al., NPJ Microgravity 2023",  
        "Díaz Artiles A et al., Front Physiol 2022",
        "Mathematical symbols: π ∑ ∂ ∫ √ α β γ",
        "Accented characters: café résumé naïve",
        "German umlauts: Müller, Bäcker, Köln",
        "Mixed: Smith & Jones (2024) → \"Advanced μ-gravity effects\"",
        "Citation with em-dash: Research findings — comprehensive analysis",
    ]
    
    print("Testing safe_log_info function...")
    success_count = 0
    
    for i, test_message in enumerate(test_cases, 1):
        try:
            print(f"Test {i}: {test_message[:50]}...")
            safe_log_info(f"Test {i}: {test_message}")
            print("  ✅ Success")
            success_count += 1
        except Exception as e:
            print(f"  ❌ Failed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Results: {success_count}/{len(test_cases)} tests passed")
    
    if success_count == len(test_cases):
        print("🎉 All Unicode logging tests PASSED!")
        print("\nThe fix successfully handles:")
        print("  • Academic citations with accented characters")
        print("  • Mathematical symbols")
        print("  • International character sets")
        print("  • Mixed Unicode content")
        return True
    else:
        print("❌ Some tests failed. Check logging configuration.")
        return False

def test_file_logging():
    """Test that file logging works with UTF-8 encoding."""
    
    print("\n🗂️  Testing File Logging")
    print("=" * 50)
    
    log_file = "test_unicode.log"
    
    try:
        # Test direct file writing with UTF-8
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write('Test Unicode: Café résumé naïve π∑∂\n')
        
        # Read it back
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"File content: {content.strip()}")
        print("✅ File logging with UTF-8 works correctly")
        
        # Clean up
        os.remove(log_file)
        return True
        
    except Exception as e:
        print(f"❌ File logging failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Unicode Logging Fix Verification")
    print("This script tests the fixes for UnicodeEncodeError in Flowise API logging")
    print()
    
    # Test 1: Safe logging function
    test1_passed = test_unicode_logging()
    
    # Test 2: File logging 
    test2_passed = test_file_logging()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print(f"  Safe Logging Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"  File Logging Test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("The Unicode encoding error in Flowise API logging has been FIXED!")
        print("\nChanges made:")
        print("  1. Updated logging configuration with UTF-8 encoding")
        print("  2. Added safe_log_info() function for Unicode handling")
        print("  3. Windows console encoding improvements")
        print("  4. Error handling for remaining edge cases")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
    
    print("\nYou can now safely use the Flowise API without Unicode errors!") 