import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import requests

time.sleep(2)
base = 'http://localhost:5000'

def session():
    s = requests.Session()
    s.get(f'{base}/')  # get session cookie
    return s

def test_calc_endpoint_exists():
    s = session()
    r = s.post(f'{base}/calc', json={'action': 'clear'})
    assert r.status_code == 200
    assert 'display' in r.json()

def test_stateful_chain_addition():
    s = session()
    s.post(f'{base}/calc', json={'action': 'clear'})
    
    r = s.post(f'{base}/calc', json={'action': 'number', 'value': '2'})
    assert r.json()['display'] == '2'
    s.post(f'{base}/calc', json={'action': 'operator', 'op': 'add'})
    
    r = s.post(f'{base}/calc', json={'action': 'number', 'value': '2'})
    assert r.json()['display'] == '2'
    
    r = s.post(f'{base}/calc', json={'action': 'operator', 'op': 'add'})
    assert r.json()['display'] == '4'
    
    r = s.post(f'{base}/calc', json={'action': 'number', 'value': '2'})
    assert r.json()['display'] == '2'
    
    r = s.post(f'{base}/calc', json={'action': 'equals'})
    assert r.json()['display'] == '6'

def test_chain_mixed_operations():
    s = session()
    s.post(f'{base}/calc', json={'action': 'clear'})
    
    s.post(f'{base}/calc', json={'action': 'number', 'value': '2'})
    s.post(f'{base}/calc', json={'action': 'operator', 'op': 'add'})
    s.post(f'{base}/calc', json={'action': 'number', 'value': '2'})
    r = s.post(f'{base}/calc', json={'action': 'operator', 'op': 'subtract'})
    assert r.json()['display'] == '4'
    
    s.post(f'{base}/calc', json={'action': 'number', 'value': '6'})
    r = s.post(f'{base}/calc', json={'action': 'equals'})
    assert r.json()['display'] == '-2'

if __name__ == '__main__':
    tests = [test_calc_endpoint_exists, test_stateful_chain_addition, test_chain_mixed_operations]
    passed = failed = 0
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