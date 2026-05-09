import os
import duckdb
import json

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'calculator.duckdb')

_connection = None

def get_connection():
    global _connection
    if _connection is None:
        _connection = duckdb.connect(DB_PATH)
        _connection.execute("""
            CREATE TABLE IF NOT EXISTS calculator_sessions (
                client_id VARCHAR PRIMARY KEY,
                state_json VARCHAR NOT NULL
            )
        """)
    return _connection

def close_connection():
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None

def load_state(client_id):
    con = get_connection()
    row = con.execute(
        'SELECT state_json FROM calculator_sessions WHERE client_id = ?',
        [client_id]
    ).fetchone()
    if row:
        return json.loads(row[0])
    else:
        state = {
            'current_value': 0,
            'pending_op': None,
            'current_input': '',
            'just_evaluated': False
        }
        con.execute(
            'INSERT INTO calculator_sessions (client_id, state_json) VALUES (?, ?)',
            [client_id, json.dumps(state)]
        )
        return state

def save_state(client_id, state):
    con = get_connection()
    con.execute(
        'INSERT OR REPLACE INTO calculator_sessions (client_id, state_json) VALUES (?, ?)',
        [client_id, json.dumps(state)]
    )