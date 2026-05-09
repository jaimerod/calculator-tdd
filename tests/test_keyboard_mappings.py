import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import requests

time.sleep(1)
base_url = 'http://localhost:5000'

def session():
    s = requests.Session()
    s.get(f'{base_url}/')
    return s

def test_backspace_maps_to_clear():
    s = session()
    s.post(f'{base_url}/calc', json={'action': 'clear'})
    s.post(f'{base_url}/calc', json={'action': 'number', 'value': '5'})
    s.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'add'})
    s.post(f'{base_url}/calc', json={'action': 'number', 'value': '3'})
    r = s.post(f'{base_url}/calc', json={'action': 'equals'})
    assert r.json()['display'] == '8'
    r = s.post(f'{base_url}/calc', json={'action': 'clear'})
    assert r.json()['display'] == '0'

def test_del_key_maps_to_clear():
    s = session()
    s.post(f'{base_url}/calc', json={'action': 'clear'})
    s.post(f'{base_url}/calc', json={'action': 'number', 'value': '9'})
    r = s.post(f'{base_url}/calc', json={'action': 'clear'})
    assert r.json()['display'] == '0'

def test_html_has_backspace_keybinding():
    r = requests.get(f'{base_url}/')
    assert 'Backspace' in r.text

def test_html_has_delete_keybinding():
    r = requests.get(f'{base_url}/')
    assert 'Delete' in r.text

def test_backspace_fresh_start():
    s = session()
    s.post(f'{base_url}/calc', json={'action': 'clear'})
    s.post(f'{base_url}/calc', json={'action': 'number', 'value': '5'})
    s.post(f'{base_url}/calc', json={'action': 'clear'})
    r = s.post(f'{base_url}/calc', json={'action': 'number', 'value': '3'})
    assert r.json()['display'] == '3'

if __name__ == '__main__':
    tests = [name for name in dir() if name.startswith('test_')]
    passed = failed = 0
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