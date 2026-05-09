import sys, os, time, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import requests

time.sleep(1)
base_url = 'http://localhost:5000'

def client(id_str=None):
    """Generate a unique client_id for test isolation"""
    return id_str or str(uuid.uuid4())

def test_no_global_shared_state():
    """Two different client_ids should not interfere"""
    c1, c2 = client(), client()
    
    # Client 1: 3 + 7 = 10
    requests.post(base_url + '/calc', json={'action': 'clear', 'client_id': c1})
    requests.post(base_url + '/calc', json={'action': 'number', 'value': '3', 'client_id': c1})
    requests.post(base_url + '/calc', json={'action': 'operator', 'op': 'add', 'client_id': c1})
    requests.post(base_url + '/calc', json={'action': 'number', 'value': '7', 'client_id': c1})
    r1 = requests.post(base_url + '/calc', json={'action': 'equals', 'client_id': c1})
    
    # Client 2: 10 * 5 = 50
    requests.post(base_url + '/calc', json={'action': 'clear', 'client_id': c2})
    requests.post(base_url + '/calc', json={'action': 'number', 'value': '10', 'client_id': c2})
    requests.post(base_url + '/calc', json={'action': 'operator', 'op': 'multiply', 'client_id': c2})
    requests.post(base_url + '/calc', json={'action': 'number', 'value': '5', 'client_id': c2})
    r2 = requests.post(base_url + '/calc', json={'action': 'equals', 'client_id': c2})
    
    assert r1.json()['display'] == '10', f"Client 1 expected 10, got {r1.json()}"
    assert r2.json()['display'] == '50', f"Client 2 expected 50, got {r2.json()}"

def test_concurrent_sessions_independent():
    """Interleaved operations with different client_ids must not interfere"""
    c1, c2 = client(), client()
    
    # Clear both
    requests.post(base_url + '/calc', json={'action': 'clear', 'client_id': c1})
    requests.post(base_url + '/calc', json={'action': 'clear', 'client_id': c2})
    
    # Client 1 starts: 5 +
    requests.post(base_url + '/calc', json={'action': 'number', 'value': '5', 'client_id': c1})
    requests.post(base_url + '/calc', json={'action': 'operator', 'op': 'add', 'client_id': c1})
    
    # Client 2: 100 /
    requests.post(base_url + '/calc', json={'action': 'number', 'value': '100', 'client_id': c2})
    requests.post(base_url + '/calc', json={'action': 'operator', 'op': 'divide', 'client_id': c2})
    
    # Client 1 continues: 3 =
    requests.post(base_url + '/calc', json={'action': 'number', 'value': '3', 'client_id': c1})
    r1 = requests.post(base_url + '/calc', json={'action': 'equals', 'client_id': c1})
    
    # Client 2 continues: 4 =
    requests.post(base_url + '/calc', json={'action': 'number', 'value': '4', 'client_id': c2})
    r2 = requests.post(base_url + '/calc', json={'action': 'equals', 'client_id': c2})
    
    assert r1.json()['display'] == '8', f"Client 1 expected 8 (5+3), got {r1.json()}"
    assert r2.json()['display'] == '25', f"Client 2 expected 25 (100/4), got {r2.json()}"

def test_default_client_id_works():
    """Requests without client_id should still work (backward compat)"""
    r = requests.post(base_url + '/calc', json={'action': 'clear'})
    assert r.status_code == 200

def test_stateless_endpoint_still_works():
    """The /calculate endpoint should work without client_id"""
    r = requests.post(base_url + '/calculate', json={'a': 10, 'b': 5, 'op': 'divide'})
    assert r.status_code == 200
    assert r.json()['result'] == 2

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