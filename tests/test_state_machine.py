"""Tests for the DOP state machine module.
These test pure functions operating on CalcState data shapes.

RED phase: these should fail because state.py doesn't exist yet.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from state import (
    CalcState,
    initial_state,
    press_number,
    press_operator,
    press_equals,
    press_clear,
    press_decimal,
)

# ─── initial_state ───

def test_initial_state_shape():
    """initial_state() returns a valid CalcState dict"""
    s = initial_state()
    assert isinstance(s, dict)
    assert s['current_value'] == 0
    assert s['pending_op'] is None
    assert s['current_input'] == ''
    assert s['just_evaluated'] is False

# ─── press_number ───

def test_press_number_appends_digit():
    s = initial_state()
    s = press_number(s, '5')
    assert s['current_input'] == '5'
    assert s['display'] == '5'

def test_press_number_chains_digits():
    s = initial_state()
    s = press_number(s, '3')
    s = press_number(s, '7')
    assert s['current_input'] == '37'
    assert s['display'] == '37'

def test_press_number_after_equals_resets():
    """After pressing equals, entering a number starts fresh"""
    s = initial_state()
    s = press_number(s, '2')
    s = press_operator(s, 'add')
    s = press_number(s, '3')
    s, _ = press_equals(s)
    s = press_number(s, '9')
    assert s['current_input'] == '9'
    assert s['display'] == '9'

# ─── press_operator ───

def test_press_operator_sets_pending():
    s = initial_state()
    s = press_number(s, '5')
    s = press_operator(s, 'add')
    assert s['pending_op'] == 'add'
    assert s['display'] == '5'

def test_press_operator_chains():
    """2 + 2 + should show 4 after second +"""
    s = initial_state()
    s = press_number(s, '2')
    s = press_operator(s, 'add')
    s = press_number(s, '2')
    s = press_operator(s, 'add')
    assert s['current_value'] == 4
    assert s['display'] == '4'

def test_press_operator_all_four():
    for op in ['add', 'subtract', 'multiply', 'divide']:
        s = initial_state()
        s = press_number(s, '1')
        s = press_operator(s, op)
        assert s['pending_op'] == op

# ─── press_equals ───

def test_press_equals_add():
    s = initial_state()
    s = press_number(s, '2')
    s = press_operator(s, 'add')
    s = press_number(s, '3')
    s, hist = press_equals(s)
    assert s['display'] == '5'
    assert hist is not None
    assert hist['expression'] == '2 + 3'
    assert hist['result'] == '5'

def test_press_equals_subtract():
    s = initial_state()
    s = press_number(s, '1')
    s = press_number(s, '0')
    s = press_operator(s, 'subtract')
    s = press_number(s, '5')
    s, hist = press_equals(s)
    assert s['display'] == '5'  # 10 - 5 = 5

def test_press_equals_multiply():
    s = initial_state()
    s = press_number(s, '7')
    s = press_operator(s, 'multiply')
    s = press_number(s, '8')
    s, hist = press_equals(s)
    assert s['display'] == '56'
    assert hist['result'] == '56'

def test_press_equals_divide():
    s = initial_state()
    s = press_number(s, '1')
    s = press_number(s, '0')
    s = press_operator(s, 'divide')
    s = press_number(s, '2')
    s, hist = press_equals(s)
    assert s['display'] == '5'
    assert hist['result'] == '5'

def test_press_equals_divide_by_zero():
    s = initial_state()
    s = press_number(s, '5')
    s = press_operator(s, 'divide')
    s = press_number(s, '0')
    s, hist = press_equals(s)
    assert s['display'] == 'Error'

def test_press_equals_returns_history_entry():
    s = initial_state()
    s = press_number(s, '5')
    s = press_operator(s, 'add')
    s = press_number(s, '3')
    s, hist = press_equals(s)
    assert hist is not None
    assert 'expression' in hist
    assert 'result' in hist
    assert '5' in hist['expression']
    assert '3' in hist['expression']
    assert hist['result'] == '8'

# ─── press_clear ───

def test_press_clear_resets_state():
    s = initial_state()
    s = press_number(s, '5')
    s = press_operator(s, 'add')
    s = press_number(s, '3')
    s = press_clear(s)
    assert s['current_value'] == 0
    assert s['pending_op'] is None
    assert s['current_input'] == ''
    assert s['just_evaluated'] is False
    assert s['display'] == '0'

# ─── press_decimal ───

def test_press_decimal():
    s = initial_state()
    s = press_number(s, '3')
    s = press_decimal(s)
    assert s['current_input'] == '3.'
    assert s['display'] == '3.'

def test_press_decimal_no_double():
    s = initial_state()
    s = press_number(s, '3')
    s = press_decimal(s)
    s = press_decimal(s)  # should be ignored
    assert s['current_input'] == '3.'

# ─── chaining ───

def test_chain_add_add():
    """2 + 2 + 2 = 6"""
    s = initial_state()
    s = press_number(s, '2')
    s = press_operator(s, 'add')
    s = press_number(s, '2')
    s = press_operator(s, 'add')
    s = press_number(s, '2')
    s, hist = press_equals(s)
    assert s['display'] == '6'

def test_chain_mixed_ops():
    """10 * 2 + 5 = 25"""
    s = initial_state()
    s = press_number(s, '1')
    s = press_number(s, '0')
    s = press_operator(s, 'multiply')
    s = press_number(s, '2')
    s = press_operator(s, 'add')
    s = press_number(s, '5')
    s, hist = press_equals(s)
    assert s['display'] == '25'

def test_operator_with_no_input_uses_current():
    """Pressing + then = without new number"""
    s = initial_state()
    s = press_number(s, '5')
    s = press_operator(s, 'add')
    # No new number, just equals
    s, hist = press_equals(s)
    # 5 + 0 = 5 (pressing equals with no second input)
    assert s['display'] == '5'

# ─── display formatting ───

def test_display_shows_integer_without_decimal():
    s = initial_state()
    s = press_number(s, '5')
    s = press_operator(s, 'add')
    s = press_number(s, '3')
    s, _ = press_equals(s)
    assert s['display'] == '8'  # not '8.0'

def test_display_shows_decimal_when_needed():
    s = initial_state()
    s = press_number(s, '1')
    s = press_decimal(s)
    s = press_number(s, '5')
    s = press_operator(s, 'add')
    s = press_number(s, '2')
    s = press_decimal(s)
    s = press_number(s, '5')
    s, _ = press_equals(s)
    assert s['display'] == '4'

# ─── immutability (DOP principle) ───

def test_press_number_does_not_mutate_original():
    s = initial_state()
    original_input = s['current_input']
    s2 = press_number(s, '5')
    assert s['current_input'] == original_input  # original unchanged
    assert s2['current_input'] == '5'

def test_press_operator_does_not_mutate_original():
    s = initial_state()
    s = press_number(s, '5')
    original_op = s['pending_op']
    s2 = press_operator(s, 'add')
    assert s['pending_op'] == original_op
    assert s2['pending_op'] == 'add'

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