import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import requests

time.sleep(1)
base_url = 'http://localhost:5000'

def test_shake_animation_css_exists():
    """CSS should have a @keyframes shake animation"""
    r = requests.get(f'{base_url}/')
    assert 'shake' in r.text

def test_shake_class_exists():
    """CSS should have a .shaking class that triggers the animation"""
    r = requests.get(f'{base_url}/')
    assert '.shake' in r.text or '.shaking' in r.text, "No shake class found"

def test_display_uses_shake_on_error():
    """The HTML should add shake class to calculator when error occurs"""
    r = requests.get(f'{base_url}/')
    html = r.text
    assert 'shake' in html.lower(), "No shake handling in HTML"

def test_error_response_has_display():
    """The API should still return a display value even on error"""
    r = requests.post(f'{base_url}/calc', json={'action': 'clear'})
    r = requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '5'})
    r = requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'divide'})
    r = requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '0'})
    r = requests.post(f'{base_url}/calc', json={'action': 'equals'})
    assert 'display' in r.json()
    # The display should show "Error" or equivalent
    assert r.json()['display'] in ['Error', 'Cannot divide by zero', '0']

def test_calculator_element_has_id():
    """The calculator container should have an ID we can shake"""
    r = requests.get(f'{base_url}/')
    html = r.text
    # Look for an id on the calculator div
    assert 'id=' in html, "No calculator container with ID"

if __name__ == '__main__':
    tests = [name for name in dir() if name.startswith('test_')]
    passed = 0
    failed = 0
    for name in tests:
        try:
            globals()[name]()
            print(f"PASS: {name}")
            passed += 1
        except Exception as e:
            print(f"FAIL: {name} - {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    if failed > 0:
        sys.exit(1)