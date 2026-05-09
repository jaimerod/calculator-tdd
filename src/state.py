"""DOP state machine for the calculator.

All functions are pure: they take a CalcState dict and return a new one.
No side effects, no mutation. History entries are returned as data, not persisted.
"""
from __future__ import annotations
from typing import TypedDict, Optional
from calculator import add, subtract, multiply, divide

# ─── Data shapes ───

class CalcState(TypedDict, total=False):
    current_value: float
    pending_op: Optional[str]
    current_input: str
    just_evaluated: bool
    display: str

class HistoryEntry(TypedDict):
    expression: str
    result: str

OP_SYMBOLS = {
    'add': '+',
    'subtract': '−',
    'multiply': '×',
    'divide': '÷',
}

OP_FUNCS = {
    'add': add,
    'subtract': subtract,
    'multiply': multiply,
    'divide': divide,
}

# ─── Pure state transitions ───

def initial_state() -> CalcState:
    return {
        'current_value': 0,
        'pending_op': None,
        'current_input': '',
        'just_evaluated': False,
        'display': '0',
    }

def _format_display(value) -> str:
    if value == 'Error':
        return 'Error'
    s = str(value)
    if s.endswith('.0'):
        return s[:-2]
    return s

def _apply_op(state: CalcState) -> CalcState:
    """Apply pending operation. Returns new state. No history side effect."""
    if state['pending_op'] is None:
        return {**state}

    a = state['current_value']
    b = float(state['current_input'] or 0)
    op = state['pending_op']
    op_func = OP_FUNCS.get(op)

    if op_func is None:
        return {**state, 'pending_op': None}

    try:
        result = op_func(a, b)
    except ZeroDivisionError:
        return {
            **state,
            'current_value': 'Error',
            'pending_op': None,
            'display': 'Error',
        }

    # Build history entry data
    a_str = str(int(a) if isinstance(a, float) and a == int(a) else a)
    b_str = str(int(b) if isinstance(b, float) and b == int(b) else b)
    result_str = str(int(result) if isinstance(result, float) and result == int(result) else result)
    expression = f"{a_str} {OP_SYMBOLS.get(op, '?')} {b_str}"

    return {
        **state,
        'current_value': result,
        'pending_op': None,
        '_last_expression': expression,
        '_last_result': result_str,
    }

def press_number(state: CalcState, digit: str) -> CalcState:
    s = {**state}
    if s['just_evaluated']:
        s['current_input'] = ''
        s['just_evaluated'] = False
    s['current_input'] += digit
    s['display'] = s['current_input']
    return s

def press_operator(state: CalcState, op: str) -> CalcState:
    s = {**state}

    if s['pending_op'] is not None and s['current_input'] != '':
        s = _apply_op(s)
        # Discard internal keys from chained ops
        s.pop('_last_expression', None)
        s.pop('_last_result', None)
    elif s['current_input'] != '':
        s['current_value'] = float(s['current_input'])

    s['pending_op'] = op
    s['current_input'] = ''
    s['just_evaluated'] = False
    s['display'] = _format_display(s['current_value'])
    return s

def press_equals(state: CalcState) -> tuple[CalcState, Optional[HistoryEntry]]:
    s = _apply_op({**state})

    # Extract history from _apply_op
    expression = s.pop('_last_expression', None)
    result = s.pop('_last_result', None)

    history_entry = None
    if expression is not None and result is not None:
        history_entry = {'expression': expression, 'result': result}

    s['pending_op'] = None
    s['current_input'] = ''
    s['just_evaluated'] = True
    s['display'] = _format_display(s['current_value'])
    return s, history_entry

def press_clear(state: CalcState) -> CalcState:
    return initial_state()

def press_decimal(state: CalcState) -> CalcState:
    s = {**state}
    if '.' in s['current_input']:
        return s  # no double decimal
    if s['current_input'] == '':
        s['current_input'] = '0.'
    else:
        s['current_input'] += '.'
    s['display'] = s['current_input']
    return s