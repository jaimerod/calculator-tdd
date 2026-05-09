import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import requests, time

time.sleep(1)
base_url = 'http://localhost:5000'

def test_backspace_maps_to_clear():
    """Backspace key should clear/reset like C button"""
    # Do a calculation first
    requests.post(f'{base_url}/calc', json={'action': 'clear'})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '5'})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'add'})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '3'})
    r = requests.post(f'{base_url}/calc', json={'action': 'equals'})
    assert r.json()['display'] == '8'
    
    # Now clear - should behave exactly like C
    r = requests.post(f'{base_url}/calc', json={'action': 'clear'})
    assert r.json()['display'] == '0'

def test_del_key_maps_to_clear():
    """Del key should clear/reset like C button"""
    requests.post(f'{base_url}/calc', json={'action': 'clear'})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '9'})
    r = requests.post(f'{base_url}/calc', json={'action': 'clear'})
    assert r.json()['display'] == '0'

def test_html_has_backspace_keybinding():
    """The HTML should map Backspace key to sendAction('clear')"""
    r = requests.get(f'{base_url}/')
    html = r.text
    assert 'Backspace' in html

def test_html_has_delete_keybinding():
    """The HTML should map Delete key to sendAction('clear')"""
    r = requests.get(f'{base_url}/')
    html = r.text
    assert 'Delete' in html

def test_backspace_fresh_start():
    """After backspace/clear, typing a number starts fresh"""
    requests.post(f'{base_url}/calc', json={'action': 'clear'})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '5'})
    requests.post(f'{base_url}/calc', json={'action': 'clear'})
    r = requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '3'})
    assert r.json()['display'] == '3', "Should start fresh, not '53'"

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