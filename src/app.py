from flask import Flask, render_template, request, jsonify
import db
from state import initial_state, press_number, press_operator, press_equals, press_clear, press_decimal

app = Flask(__name__, template_folder='templates')
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.after_request
def add_no_cache(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return response

def get_client_id():
    if request.is_json:
        return request.json.get('client_id') or 'default'
    return request.args.get('client_id') or 'default'

def load_state():
    return db.load_state(get_client_id())

def save_state(state):
    db.save_state(get_client_id(), state)

@app.route('/')
def index():
    return render_template('calculator.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    """Stateless endpoint for simple a op b calculations."""
    data = request.get_json()
    from calculator import add, subtract, multiply, divide
    ops = {'add': add, 'subtract': subtract, 'multiply': multiply, 'divide': divide}
    op = data.get('op', 'add')
    a, b = data.get('a', 0), data.get('b', 0)
    try:
        return jsonify({'result': ops[op](a, b)})
    except ZeroDivisionError:
        return jsonify({'error': 'Cannot divide by zero'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/calc', methods=['POST'])
def calc():
    """Stateful endpoint — loads state from DuckDB, applies action, saves back."""
    data = request.get_json()
    action = data.get('action')

    if action == 'clear':
        state = press_clear(load_state())
        save_state(state)
        return jsonify({'display': state['display']})

    elif action == 'number':
        state = press_number(load_state(), str(data.get('value', '')))
        save_state(state)
        return jsonify({'display': state['display']})

    elif action == 'operator':
        state = press_operator(load_state(), data.get('op'))
        save_state(state)
        return jsonify({'display': state['display']})

    elif action == 'equals':
        state, history_entry = press_equals(load_state())
        save_state(state)
        if history_entry:
            db.add_history(get_client_id(), history_entry['expression'], history_entry['result'])
        return jsonify({'display': state['display']})

    elif action == 'decimal':
        state = press_decimal(load_state())
        save_state(state)
        return jsonify({'display': state['display']})

    return jsonify({'error': 'Unknown action'}), 400

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify({'history': db.get_history(get_client_id())})

@app.route('/history/clear', methods=['POST'])
def clear_history():
    db.clear_history(get_client_id())
    return jsonify({'ok': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)