import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import requests
import time

# Give server time to start
time.sleep(2)

def test_calc_endpoint_exists():
    """Test that /calc endpoint responds"""
    response = requests.post('http://localhost:5000/calc', json={'action': 'clear'})
    assert response.status_code == 200
    data = response.json()
    assert 'display' in data
    print(f"Response: {data}")

def test_stateful_chain_addition():
    """Test chained addition: 2 + 2 + 2 = 6"""
    # Clear first
    requests.post('http://localhost:5000/calc', json={'action': 'clear'})
    
    # Enter 2
    response = requests.post('http://localhost:5000/calc', json={'action': 'number', 'value': '2'})
    data = response.json()
    assert data['display'] == '2', f"Expected '2', got '{data['display']}'"
    
    # Press +
    requests.post('http://localhost:5000/calc', json={'action': 'operator', 'op': 'add'})
    
    # Enter 2
    response = requests.post('http://localhost:5000/calc', json={'action': 'number', 'value': '2'})
    data = response.json()
    assert data['display'] == '2', f"Expected '2', got '{data['display']}'"
    
    # Press + again (should show intermediate result 4)
    response = requests.post('http://localhost:5000/calc', json={'action': 'operator', 'op': 'add'})
    data = response.json()
    assert data['display'] == '4', f"Expected '4', got '{data['display']}'"
    
    # Enter 2
    response = requests.post('http://localhost:5000/calc', json={'action': 'number', 'value': '2'})
    data = response.json()
    assert data['display'] == '2', f"Expected '2', got '{data['display']}'"
    
    # Press = (should show 6)
    response = requests.post('http://localhost:5000/calc', json={'action': 'equals'})
    data = response.json()
    assert data['display'] == '6', f"Expected '6', got '{data['display']}'"

def test_chain_mixed_operations():
    """Test: 2 + 2 - 6 = -2"""
    # Clear first
    requests.post('http://localhost:5000/calc', json={'action': 'clear'})
    
    # 2
    requests.post('http://localhost:5000/calc', json={'action': 'number', 'value': '2'})
    # +
    requests.post('http://localhost:5000/calc', json={'action': 'operator', 'op': 'add'})
    # 2
    requests.post('http://localhost:5000/calc', json={'action': 'number', 'value': '2'})
    # - (should show 4)
    response = requests.post('http://localhost:5000/calc', json={'action': 'operator', 'op': 'subtract'})
    data = response.json()
    assert data['display'] == '4', f"Expected '4', got {data['display']}"
    
    # 6
    requests.post('http://localhost:5000/calc', json={'action': 'number', 'value': '6'})
    # = (should show -2)
    response = requests.post('http://localhost:5000/calc', json={'action': 'equals'})
    data = response.json()
    assert data['display'] == '-2', f"Expected '-2', got {data['display']}"

if __name__ == '__main__':
    tests = [
        test_calc_endpoint_exists,
        test_stateful_chain_addition,
        test_chain_mixed_operations
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"FAIL: {test.__name__} - {e}")
            failed += 1
    
    print(f"\n{passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)