import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import requests
import uuid

time.sleep(1)
base_url = 'http://localhost:5000'

def test_two_tabs_with_different_ids():
    """Two tabs with different client_ids should not interfere"""
    tab1_id = str(uuid.uuid4())
    tab2_id = str(uuid.uuid4())
    
    # Tab 1: 3 + 7 = 10
    requests.post(f'{base_url}/calc', json={'action': 'clear', 'client_id': tab1_id})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '3', 'client_id': tab1_id})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'add', 'client_id': tab1_id})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '7', 'client_id': tab1_id})
    r1 = requests.post(f'{base_url}/calc', json={'action': 'equals', 'client_id': tab1_id})
    
    # Tab 2: 10 * 5 = 50
    requests.post(f'{base_url}/calc', json={'action': 'clear', 'client_id': tab2_id})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '10', 'client_id': tab2_id})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'multiply', 'client_id': tab2_id})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '5', 'client_id': tab2_id})
    r2 = requests.post(f'{base_url}/calc', json={'action': 'equals', 'client_id': tab2_id})
    
    assert r1.json()['display'] == '10', f"Tab 1 expected 10, got {r1.json()}"
    assert r2.json()['display'] == '50', f"Tab 2 expected 50, got {r2.json()}"

def test_interleaved_tabs_with_ids():
    """Interleaved operations with different client_ids must be isolated"""
    tab1_id = str(uuid.uuid4())
    tab2_id = str(uuid.uuid4())
    
    # Clear both
    requests.post(f'{base_url}/calc', json={'action': 'clear', 'client_id': tab1_id})
    requests.post(f'{base_url}/calc', json={'action': 'clear', 'client_id': tab2_id})
    
    # Tab 1 starts: 5 +
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '5', 'client_id': tab1_id})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'add', 'client_id': tab1_id})
    
    # Tab 2 does their own thing: 100 /
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '100', 'client_id': tab2_id})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'divide', 'client_id': tab2_id})
    
    # Tab 1 continues: 3 =
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '3', 'client_id': tab1_id})
    r1 = requests.post(f'{base_url}/calc', json={'action': 'equals', 'client_id': tab1_id})
    
    # Tab 2 continues: 4 =
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '4', 'client_id': tab2_id})
    r2 = requests.post(f'{base_url}/calc', json={'action': 'equals', 'client_id': tab2_id})
    
    assert r1.json()['display'] == '8', f"Tab 1 expected 8 (5+3), got {r1.json()}"
    assert r2.json()['display'] == '25', f"Tab 2 expected 25 (100/4), got {r2.json()}"

def test_no_client_id_falls_back():
    """Requests without client_id should get their own session (backward compat)"""
    # With no client_id, should still work
    r = requests.post(f'{base_url}/calc', json={'action': 'clear'})
    assert r.status_code == 200

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