import sys, os, time, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import requests

time.sleep(1)
base_url = 'http://localhost:5000'

def session():
    return str(uuid.uuid4())

def test_history_tracks_calculations():
    tid = session()
    requests.post(f'{base_url}/calc', json={'action': 'clear', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '5', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'add', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '3', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'equals', 'client_id': tid})
    
    r = requests.get(f'{base_url}/history', params={'client_id': tid})
    assert r.status_code == 200
    history = r.json().get('history', [])
    assert len(history) >= 1
    entry = history[-1]
    assert entry['expression'] == '5 + 3', f"Got {entry['expression']}"
    assert entry['result'] == '8', f"Got {entry['result']}"

def test_history_shows_multiple_entries():
    tid = session()
    
    requests.post(f'{base_url}/calc', json={'action': 'clear', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '10', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'multiply', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '2', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'equals', 'client_id': tid})
    
    requests.post(f'{base_url}/calc', json={'action': 'clear', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '50', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'divide', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '5', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'equals', 'client_id': tid})
    
    r = requests.get(f'{base_url}/history', params={'client_id': tid})
    history = r.json().get('history', [])
    assert len(history) >= 2, f"Expected at least 2, got {len(history)}"

def test_history_slideout_html_exists():
    r = requests.get(f'{base_url}/')
    html = r.text
    assert 'history-panel' in html

def test_history_has_toggle_button():
    r = requests.get(f'{base_url}/')
    html = r.text
    assert 'historyToggle' in html or 'toggleHistory' in html

def test_history_clear_button():
    r = requests.get(f'{base_url}/')
    html = r.text
    assert 'clearHistory' in html or 'clear-history' in html

def test_history_panel_slides_in_out():
    r = requests.get(f'{base_url}/')
    html = r.text
    assert 'translateX' in html or 'transform' in html

def test_op_symbols_in_history():
    tid = session()
    requests.post(f'{base_url}/calc', json={'action': 'clear', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '3', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'subtract', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '1', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'equals', 'client_id': tid})
    
    r = requests.get(f'{base_url}/history', params={'client_id': tid})
    history = r.json().get('history', [])
    latest = history[-1] if history else {'expression': ''}
    # Use the \u2212 minus
    assert '\u2212' in latest['expression'], f"Expected minus in {latest['expression']}"

def test_history_persists_in_duckdb():
    tid = session()
    requests.post(f'{base_url}/calc', json={'action': 'clear', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '5', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'multiply', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '6', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'equals', 'client_id': tid})
    
    r = requests.get(f'{base_url}/history', params={'client_id': tid})
    history = r.json().get('history', [])
    assert any('5' in e['expression'] and '6' in e['expression'] for e in history)

def test_history_clear_works():
    tid = session()
    requests.post(f'{base_url}/calc', json={'action': 'clear', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '5', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'add', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '5', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'equals', 'client_id': tid})
    
    requests.post(f'{base_url}/history/clear', json={'client_id': tid})
    
    r = requests.get(f'{base_url}/history', params={'client_id': tid})
    assert r.json()['history'] == [], f"History not cleared: {r.json()}"

if __name__ == '__main__':
    tests = [name for name in dir() if name.startswith('test_')]
    passed = failed = 0
    for name in tests:
        try:
            globals()[name]()
            sys.stdout.write(f"PASS: {name}\n")
            passed += 1
        except Exception as e:
            sys.stdout.write(f"FAIL: {name} - {e}\n")
            failed += 1
    sys.stdout.write(f"\n{passed} passed, {failed} failed\n")
    if failed > 0:
        sys.exit(1)