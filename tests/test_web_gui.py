import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import requests

def test_flask_server_is_running():
    """Test that the Flask server serves the calculator page"""
    try:
        response = requests.get('http://localhost:5000')
        assert response.status_code == 200
        assert 'Calculator' in response.text
    except requests.exceptions.ConnectionError:
        assert False, "Flask server is not running on port 5000"

def test_calculator_api_add():
    """Test the calculator API endpoint for addition"""
    try:
        response = requests.post('http://localhost:5000/calculate', json={'a': 2, 'b': 3, 'op': 'add'})
        assert response.status_code == 200
        data = response.json()
        assert data['result'] == 5
    except requests.exceptions.ConnectionError:
        assert False, "Flask server is not running on port 5000"

def test_calculator_api_divide_by_zero():
    """Test that dividing by zero returns an error"""
    try:
        response = requests.post('http://localhost:5000/calculate', json={'a': 10, 'b': 0, 'op': 'divide'})
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
    except requests.exceptions.ConnectionError:
        assert False, "Flask server is not running on port 5000"

if __name__ == '__main__':
    import time
    time.sleep(2)  # Give server time to start
    
    tests = [
        test_flask_server_is_running,
        test_calculator_api_add,
        test_calculator_api_divide_by_zero
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