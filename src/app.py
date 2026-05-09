from flask import Flask, render_template, request, jsonify
from calculator import add, subtract, multiply, divide

app = Flask(__name__, template_folder='templates')

@app.after_request
def add_no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

# In-memory state for the calculator (single user demo)
calc_state = {
    'current_value': 0,      # The running total
    'pending_op': None,      # Operator waiting to be applied
    'current_input': '',     # What user is currently typing
    'just_evaluated': False  # Whether we just showed a result
}

def apply_operation():
    """Apply pending operation to current_value and current_input"""
    global calc_state
    if calc_state['pending_op'] is None:
        # Just store the current input as the current value
        calc_state['current_value'] = float(calc_state['current_input'] or 0)
        return
    
    a = calc_state['current_value']
    b = float(calc_state['current_input'] or 0)
    
    try:
        if calc_state['pending_op'] == 'add':
            calc_state['current_value'] = add(a, b)
        elif calc_state['pending_op'] == 'subtract':
            calc_state['current_value'] = subtract(a, b)
        elif calc_state['pending_op'] == 'multiply':
            calc_state['current_value'] = multiply(a, b)
        elif calc_state['pending_op'] == 'divide':
            calc_state['current_value'] = divide(a, b)
    except ZeroDivisionError:
        calc_state['current_value'] = 'Error'
    
    calc_state['pending_op'] = None

@app.route('/')
def index():
    return render_template('calculator.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    """Original stateless API - kept for backward compatibility"""
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
    """Stateful calculator for chaining operations"""
    global calc_state
    data = request.get_json()
    action = data.get('action')
    
    if action == 'clear':
        calc_state = {
            'current_value': 0,
            'pending_op': None,
            'current_input': '',
            'just_evaluated': False
        }
        return jsonify({'display': '0'})
    
    elif action == 'number':
        value = str(data.get('value', ''))
        
        # If we just evaluated, start fresh
        if calc_state['just_evaluated']:
            calc_state['current_input'] = ''
            calc_state['just_evaluated'] = False
        
        calc_state['current_input'] += value
        return jsonify({'display': calc_state['current_input'] or '0'})
    
    elif action == 'operator':
        op = data.get('op')
        
        # If there's a pending op, apply it first (chaining!)
        if calc_state['pending_op'] is not None and calc_state['current_input'] != '':
            apply_operation()
            calc_state['pending_op'] = op
            calc_state['current_input'] = ''
            calc_state['just_evaluated'] = False
            # Return the intermediate result
            display = str(calc_state['current_value'])
            if display.endswith('.0'):
                display = display[:-2]
            return jsonify({'display': display})
        else:
            # First operator or chaining without new input
            if calc_state['current_input'] != '':
                calc_state['current_value'] = float(calc_state['current_input'])
            calc_state['pending_op'] = op
            calc_state['current_input'] = ''
            calc_state['just_evaluated'] = False
            display = str(calc_state['current_value'])
            if display.endswith('.0'):
                display = display[:-2]
            return jsonify({'display': display})
    
    elif action == 'equals':
        # Apply the pending operation
        apply_operation()
        calc_state['pending_op'] = None
        calc_state['current_input'] = ''
        calc_state['just_evaluated'] = True
        
        display = str(calc_state['current_value'])
        if display.endswith('.0'):
            display = display[:-2]
        return jsonify({'display': display})
    
    return jsonify({'error': 'Unknown action'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)