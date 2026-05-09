import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import requests, time

time.sleep(1)

def run_test(name, steps):
    """steps: list of (action, payload, expected_display)"""
    requests.post('http://localhost:5000/calc', json={'action': 'clear'})
    
    for action, payload, expected in steps:
        payload['action'] = action
        r = requests.post('http://localhost:5000/calc', json=payload)
        data = r.json()
        actual = data.get('display', data.get('result', ''))
        if str(actual) != str(expected):
            print(f"  FAIL at step {action}({payload}): expected {expected}, got {actual}")
            return False
    return True

tests = [
    ("2 + 2 + 2 = 6", [
        ('number', {'value': '2'}, '2'),
        ('operator', {'op': 'add'}, '2'),
        ('number', {'value': '2'}, '2'),
        ('operator', {'op': 'add'}, '4'),
        ('number', {'value': '2'}, '2'),
        ('equals', {}, '6'),
    ]),
    ("2 + 2 - 6 = -2", [
        ('number', {'value': '2'}, '2'),
        ('operator', {'op': 'add'}, '2'),
        ('number', {'value': '2'}, '2'),
        ('operator', {'op': 'subtract'}, '4'),
        ('number', {'value': '6'}, '6'),
        ('equals', {}, '-2'),
    ]),
    ("3 * 3 * 3 = 27", [
        ('number', {'value': '3'}, '3'),
        ('operator', {'op': 'multiply'}, '3'),
        ('number', {'value': '3'}, '3'),
        ('operator', {'op': 'multiply'}, '9'),
        ('number', {'value': '3'}, '3'),
        ('equals', {}, '27'),
    ]),
    ("100 / 2 / 5 = 10", [
        ('number', {'value': '100'}, '100'),
        ('operator', {'op': 'divide'}, '100'),
        ('number', {'value': '2'}, '2'),
        ('operator', {'op': 'divide'}, '50'),
        ('number', {'value': '5'}, '5'),
        ('equals', {}, '10'),
    ]),
    ("10 * 2 + 5 = 25", [
        ('number', {'value': '10'}, '10'),
        ('operator', {'op': 'multiply'}, '10'),
        ('number', {'value': '2'}, '2'),
        ('operator', {'op': 'add'}, '20'),
        ('number', {'value': '5'}, '5'),
        ('equals', {}, '25'),
    ]),
    ("decimal: 1.5 + 2.5 = 4", [
        ('number', {'value': '1'}, '1'),
        ('number', {'value': '.'}, '1.'),
        ('number', {'value': '5'}, '1.5'),
        ('operator', {'op': 'add'}, '1.5'),
        ('number', {'value': '2'}, '2'),
        ('number', {'value': '.'}, '2.'),
        ('number', {'value': '5'}, '2.5'),
        ('equals', {}, '4'),
    ]),
]

passed = 0
failed = 0
for name, steps in tests:
    if run_test(name, steps):
        print(f"PASS: {name}")
        passed += 1
    else:
        print(f"FAIL: {name}")
        failed += 1

print(f"\n{passed} passed, {failed} failed")
if failed > 0:
    sys.exit(1)