from flask import Flask, render_template, request, jsonify
from calculator import add, subtract, multiply, divide
import os

app = Flask(__name__, template_folder='templates')

# Per-tab state: {client_id: {current_value, pending_op, current_input, just_evaluated}}
tab_states = {}

@app.after_request
def add_no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

def get_client_id():
    return request.json.get('client_id') if request.is_json else None

def get_state():
    cid = get_client_id()
    if cid is None:
        cid = 'default'
    if cid not in tab_states:
        tab_states[cid] = {
            'current_value': 0,
            'pending_op': None,
            'current_input': '',
            'just_evaluated': False
        }
    return tab_states[cid]

def save_state(state):
    cid = get_client_id() or 'default'
    tab_states[cid] = state

def apply_operation():
    state = get_state()
    if state['pending_op'] is None:
        state['current_value'] = float(state['current_input'] or 0)
        save_state(state)
        return
    
    a = state['current_value']
    b = float(state['current_input'] or 0)
    
    try:
        if state['pending_op'] == 'add':
            state['current_value'] = add(a, b)
        elif state['pending_op'] == 'subtract':
            state['current_value'] = subtract(a, b)
        elif state['pending_op'] == 'multiply':
            state['current_value'] = multiply(a, b)
        elif state['pending_op'] == 'divide':
            state['current_value'] = divide(a, b)
    except ZeroDivisionError:
        state['current_value'] = 'Error'
    
    state['pending_op'] = None
    save_state(state)

@app.route('/')
def index():
    return render_template('calculator.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()
    a = data.get('a', 0)
    b = data.get('b', 0)
    op = data.get('op', 'add')
    
    try:
        if op == 'add':
            result = add(a, b)
        elif op == 'subtract':
            result = subtract(a, b)
        elif op == 'multiply':
            result = multiply(a, b)
        elif op == 'divide':
            result = divide(a, b)
        else:
            return jsonify({'error': 'Unknown operation'}), 400
        
        return jsonify({'result': result})
    except ZeroDivisionError:
        return jsonify({'error': 'Cannot divide by zero'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/calc', methods=['POST'])
def calc():
    state = get_state()
    data = request.get_json()
    action = data.get('action')
    
    if action == 'clear':
        state = {
            'current_value': 0,
            'pending_op': None,
            'current_input': '',
            'just_evaluated': False
        }
        save_state(state)
        return jsonify({'display': '0'})
    
    elif action == 'number':
        value = str(data.get('value', ''))
        
        if state['just_evaluated']:
            state['current_input'] = ''
            state['just_evaluated'] = False
        
        state['current_input'] += value
        save_state(state)
        return jsonify({'display': state['current_input'] or '0'})
    
    elif action == 'operator':
        op = data.get('op')
        
        if state['pending_op'] is not None and state['current_input'] != '':
            apply_operation()
            state = get_state()
            state['pending_op'] = op
            state['current_input'] = ''
            state['just_evaluated'] = False
            save_state(state)
            display = str(state['current_value'])
            if display.endswith('.0'):
                display = display[:-2]
            return jsonify({'display': display})
        else:
            if state['current_input'] != '':
                state['current_value'] = float(state['current_input'])
            state['pending_op'] = op
            state['current_input'] = ''
            state['just_evaluated'] = False
            save_state(state)
            display = str(state['current_value'])
            if display.endswith('.0'):
                display = display[:-2]
            return jsonify({'display': display})
    
    elif action == 'equals':
        apply_operation()
        state = get_state()
        state['pending_op'] = None
        state['current_input'] = ''
        state['just_evaluated'] = True
        save_state(state)
        
        display = str(state['current_value'])
        if display.endswith('.0'):
            display = display[:-2]
        return jsonify({'display': display})
    
    return jsonify({'error': 'Unknown action'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)