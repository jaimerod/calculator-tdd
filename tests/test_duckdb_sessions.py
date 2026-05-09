import sys, os, time, uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import requests

time.sleep(1)
base_url = 'http://localhost:5000'

def test_two_tabs_via_duckdb():
    """Two tabs with different UUIDs should be isolated via DuckDB"""
    tid1 = str(uuid.uuid4())
    tid2 = str(uuid.uuid4())
    
    requests.post(f'{base_url}/calc', json={'action': 'clear', 'client_id': tid1})
    requests.post(f'{base_url}/calc', json={'action': 'clear', 'client_id': tid2})
    
    # Tab 1: 3 + 7 = 10
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '3', 'client_id': tid1})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'add', 'client_id': tid1})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '7', 'client_id': tid1})
    r1 = requests.post(f'{base_url}/calc', json={'action': 'equals', 'client_id': tid1})
    
    # Tab 2: 10 * 5 = 50
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '10', 'client_id': tid2})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'multiply', 'client_id': tid2})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '5', 'client_id': tid2})
    r2 = requests.post(f'{base_url}/calc', json={'action': 'equals', 'client_id': tid2})
    
    assert r1.json()['display'] == '10', f"Tab 1 expected 10, got {r1.json()}"
    assert r2.json()['display'] == '50', f"Tab 2 expected 50, got {r2.json()}"

def test_interleaved_tabs_via_duckdb():
    """Interleaved operations with different UUIDs must be isolated"""
    tid1 = str(uuid.uuid4())
    tid2 = str(uuid.uuid4())
    
    requests.post(f'{base_url}/calc', json={'action': 'clear', 'client_id': tid1})
    requests.post(f'{base_url}/calc', json={'action': 'clear', 'client_id': tid2})
    
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '5', 'client_id': tid1})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'add', 'client_id': tid1})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '100', 'client_id': tid2})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'divide', 'client_id': tid2})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '3', 'client_id': tid1})
    r1 = requests.post(f'{base_url}/calc', json={'action': 'equals', 'client_id': tid1})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '4', 'client_id': tid2})
    r2 = requests.post(f'{base_url}/calc', json={'action': 'equals', 'client_id': tid2})
    
    assert r1.json()['display'] == '8', f"Tab 1 expected 8, got {r1.json()}"
    assert r2.json()['display'] == '25', f"Tab 2 expected 25, got {r2.json()}"

def test_chaining_with_duckdb():
    """Chaining should work: 2 + 2 + 2 = 6"""
    tid = str(uuid.uuid4())
    requests.post(f'{base_url}/calc', json={'action': 'clear', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '2', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'add', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '2', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'add', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '2', 'client_id': tid})
    r = requests.post(f'{base_url}/calc', json={'action': 'equals', 'client_id': tid})
    assert r.json()['display'] == '6'

def test_mixed_ops_with_duckdb():
    """2 + 2 - 6 = -2"""
    tid = str(uuid.uuid4())
    requests.post(f'{base_url}/calc', json={'action': 'clear', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '2', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'add', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '2', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'subtract', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '6', 'client_id': tid})
    r = requests.post(f'{base_url}/calc', json={'action': 'equals', 'client_id': tid})
    assert r.json()['display'] == '-2'

def test_fresh_uuid_gets_fresh_state():
    """A new UUID should get a fresh session"""
    fresh_tid = str(uuid.uuid4())
    r = requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '5', 'client_id': fresh_tid})
    assert r.json()['display'] == '5'

def test_duckdb_db_file_exists():
    """The DuckDB file should be created"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'calculator.duckdb')
    assert os.path.exists(db_path), f"DuckDB file not found at {db_path}"

def test_error_with_duckdb():
    """Division by zero should show Error"""
    tid = str(uuid.uuid4())
    requests.post(f'{base_url}/calc', json={'action': 'clear', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '5', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'divide', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '0', 'client_id': tid})
    r = requests.post(f'{base_url}/calc', json={'action': 'equals', 'client_id': tid})
    assert r.json()['display'] == 'Error'

def test_chain_multiply_then_divide():
    """7 * 8 = 56, / 2 = 28"""
    tid = str(uuid.uuid4())
    requests.post(f'{base_url}/calc', json={'action': 'clear', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '7', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'multiply', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '8', 'client_id': tid})
    r = requests.post(f'{base_url}/calc', json={'action': 'equals', 'client_id': tid})
    assert r.json()['display'] == '56'
    
    requests.post(f'{base_url}/calc', json={'action': 'operator', 'op': 'divide', 'client_id': tid})
    requests.post(f'{base_url}/calc', json={'action': 'number', 'value': '2', 'client_id': tid})
    r = requests.post(f'{base_url}/calc', json={'action': 'equals', 'client_id': tid})
    assert r.json()['display'] == '28'

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