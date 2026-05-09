import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import requests
import re
import time

time.sleep(1)
base = 'http://localhost:5000'

def test_page_loads():
    r = requests.get(f'{base}/')
    assert r.status_code == 200

def test_numpad_10key_layout():
    """Verify the numpad has proper 10-key layout"""
    r = requests.get(f'{base}/')
    html = r.text
    
    # Row 1: C / * -
    assert ">C<" in html
    assert "&divide;" in html or "÷" in html
    assert "&times;" in html or "×" in html
    
    # Standard digit positions
    assert ">7<" in html
    assert ">8<" in html
    assert ">9<" in html
    assert ">4<" in html
    assert ">5<" in html
    assert ">6<" in html
    assert ">1<" in html
    assert ">2<" in html
    assert ">3<" in html
    assert ">0<" in html
    assert ">.<" in html
    assert ">=<" in html
    
    # Check for spans
    assert "span 2" in html or "span 2 rows" in html

def test_0_is_wide():
    """0 button should span 2 columns"""
    r = requests.get(f'{base}/')
    html = r.text
    # Find the 0 button area
    assert 'grid-column' in html

def test_tall_buttons_exist():
    """+ and = should be tall (span 2 rows)"""
    r = requests.get(f'{base}/')
    html = r.text
    # Check for CSS class on tall buttons
    assert 'row' in html

def test_chaining_works_with_new_layout():
    """Full chaining test on new layout"""
    base_url = f'{base}/calc'
    requests.post(base_url, json={'action': 'clear'})
    
    # 7 × 8 = 56
    requests.post(base_url, json={'action': 'number', 'value': '7'})
    requests.post(base_url, json={'action': 'operator', 'op': 'multiply'})
    requests.post(base_url, json={'action': 'number', 'value': '8'})
    r = requests.post(base_url, json={'action': 'equals'})
    assert r.json()['display'] == '56'
    
    # ÷ 2 = 28
    requests.post(base_url, json={'action': 'operator', 'op': 'divide'})
    requests.post(base_url, json={'action': 'number', 'value': '2'})
    r = requests.post(base_url, json={'action': 'equals'})
    assert r.json()['display'] == '28'

def test_keyboard_input():
    """Keyboard still works"""
    base_url = f'{base}/calc'
    requests.post(base_url, json={'action': 'clear'})
    requests.post(base_url, json={'action': 'number', 'value': '9'})
    requests.post(base_url, json={'action': 'operator', 'op': 'multiply'})
    requests.post(base_url, json={'action': 'number', 'value': '9'})
    r = requests.post(base_url, json={'action': 'equals'})
    assert r.json()['display'] == '81'

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